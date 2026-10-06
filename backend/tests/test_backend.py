import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from mailrisk.api import create_app
from mailrisk.application import AnalysisService
from mailrisk.domain import AppError, Extraction, validate_evidence
from mailrisk.ingestion import normalize, upload
from mailrisk.providers import create_provider
from mailrisk.settings import Settings
from mailrisk.storage import SQLiteStore


@pytest.fixture
def settings(tmp_path):
    return Settings(
        database_path=str(tmp_path / "test.sqlite3"),
        seed_path=str(tmp_path / "absent.json"),
        llm_max_retries=0,
    )


class FakeProvider:
    def __init__(self, fail_b=False):
        self.fail_b = fail_b

    async def generate_structured(self, instructions, input, output_schema, timeout):
        if "extraction" not in input:
            evidence = {"source_id": input["sources"][0]["id"], "quote": "Hello"}
            return json.dumps(
                {
                    "sender": "person@example.com",
                    "recipients": [],
                    "date": None,
                    "subject": "Greeting",
                    "summary": "Greeting",
                    "facts": [
                        {"kind": "greeting", "value": "Hello", "evidence": [evidence]}
                    ],
                }
            ), {}
        if self.fail_b:
            raise AppError("unavailable", "Unavailable", True)
        return json.dumps(
            {
                "risk": {"level": "none", "rationale": "Ordinary greeting", "tags": []},
                "entities": [],
                "relationships": [],
            }
        ), {}


@pytest.mark.asyncio
async def test_partial_failure_and_selected_success_survive(settings):
    store = SQLiteStore(settings.path(settings.database_path))
    mid, _ = store.ingest(normalize("Hello"))
    service = AnalysisService(store, FakeProvider(), settings)
    first = service.submit(mid)
    await service.process(first)
    assert store.detail(mid)["risk"]["level"] == "none"
    service.provider = FakeProvider(fail_b=True)
    second = service.submit(mid)
    await service.process(second)
    detail = store.detail(mid)
    assert detail["latest_run"]["status"] == "failed"
    assert detail["latest_run"]["extraction"]
    assert detail["selected_run"]["id"] == first
    assert detail["risk"]["level"] == "none"


@pytest.mark.asyncio
async def test_invalid_evidence_and_bounded_repair(settings):
    class BadProvider:
        calls = 0

        async def generate_structured(self, *args):
            self.calls += 1
            return "not JSON", {}

    settings.llm_max_retries = 1
    store = SQLiteStore(settings.path(settings.database_path))
    mid, _ = store.ingest(normalize("Hello"))
    provider = BadProvider()
    service = AnalysisService(store, provider, settings)
    run_id = service.submit(mid)
    await service.process(run_id)
    assert provider.calls == 2
    assert store.run(run_id)["error"]["code"] == "invalid_output"
    assert store.run(run_id)["risk"] is None


@pytest.mark.asyncio
async def test_outer_timeout(settings):
    class SlowProvider:
        async def generate_structured(self, *args):
            await asyncio.sleep(1)

    settings.llm_timeout_seconds = 0.01
    store = SQLiteStore(settings.path(settings.database_path))
    mid, _ = store.ingest(normalize("Hello"))
    service = AnalysisService(store, SlowProvider(), settings)
    run_id = service.submit(mid)
    await service.process(run_id)
    assert store.run(run_id)["error"]["code"] == "timeout"


def test_seed_idempotency_and_restart(settings):
    store = SQLiteStore(settings.path(settings.database_path))
    assert store.ingest(normalize("Hello"), "seed")[1]
    assert not store.ingest(normalize("Changed"), "seed")[1]
    service = AnalysisService(store, FakeProvider(), settings)
    rid = service.submit("seed")
    assert service.submit("seed") == rid
    store.interrupt()
    assert store.run(rid)["status"] == "interrupted"
    assert len(store.inbox()) == 1


def test_upload_formats_and_limits():
    assert upload("test.txt", b"Hello")["body"] == "Hello"
    email = b"From: a@example.com\nTo: b@example.com, c@example.com\nSubject: Test\nContent-Type: text/plain\n\nHello"
    assert upload("test.eml", email)["recipients"] == ["b@example.com", "c@example.com"]
    for name, content in [
        ("x.exe", b"x"),
        ("x.txt", b"\xff"),
        ("x.pdf", b"bad"),
        ("x.txt", b" "),
    ]:
        with pytest.raises(AppError):
            upload(name, content)
    with pytest.raises(AppError) as error:
        upload("x.txt", b"x" * (10 * 1024 * 1024 + 1))
    assert error.value.status == 413


def test_evidence_validation():
    result = Extraction(
        sender=None,
        recipients=[],
        date=None,
        subject=None,
        summary="test",
        facts=[
            {
                "kind": "amount",
                "value": "100",
                "evidence": [{"source_id": "s", "quote": "invented"}],
            }
        ],
    )
    with pytest.raises(AppError):
        validate_evidence(result, [{"id": "s", "text": "Hello"}])


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_name", ["ollama", "groq"])
async def test_provider_payload_and_auth(settings, provider_name):
    settings.llm_provider = provider_name
    settings.groq_api_key = "test-only-key"

    def handler(request):
        payload = json.loads(request.content)
        assert payload["messages"][0]["role"] == "system"
        if provider_name == "ollama":
            assert payload["stream"] is False
            return httpx.Response(200, json={"message": {"content": "{}"}})
        assert request.headers["authorization"] == "Bearer test-only-key"
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})

    raw, _ = await create_provider(
        settings, httpx.MockTransport(handler)
    ).generate_structured("instructions", {}, {}, 1)
    assert raw == "{}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,code,retryable",
    [
        (401, "authentication", False),
        (429, "rate_limit", True),
        (500, "unavailable", True),
        (404, "configuration", False),
    ],
)
async def test_provider_errors(settings, status, code, retryable):
    provider = create_provider(
        settings,
        httpx.MockTransport(
            lambda request: httpx.Response(status, text="private provider body")
        ),
    )
    with pytest.raises(AppError) as error:
        await provider.generate_structured("instructions", {}, {}, 1)
    assert error.value.code == code
    assert error.value.retryable == retryable
    assert "private" not in str(error.value)


def test_http_contract(settings):
    with TestClient(create_app(settings, FakeProvider())) as client:
        assert client.get("/health").status_code == 200
        response = client.post("/emails", json={"raw_text": "Hello"})
        assert response.status_code == 202
        ids = response.json()
        detail = client.get("/emails/" + ids["message_id"]).json()
        assert detail["body"] == "Hello"
        assert "prompt_snapshots" not in detail["latest_run"]
        assert client.get("/emails/absent").status_code == 404
        assert client.post("/emails", json={"raw_text": ""}).status_code == 422
        assert client.get("/graph").json() == {"entities": [], "relationships": []}


def test_selected_graph_and_conservative_identity(settings):
    store = SQLiteStore(settings.path(settings.database_path))
    mid, _ = store.ingest(normalize("Hello"))
    service = AnalysisService(store, FakeProvider(), settings)
    evidence = [{"source_id": store.message(mid)["sources"][0]["id"], "quote": "Hello"}]
    assessment = {
        "risk": {"level": "low", "rationale": "Review", "tags": []},
        "entities": [
            {"id": "p", "type": "person", "label": "James", "evidence": evidence},
            {
                "id": "e",
                "type": "email",
                "label": "james@example.com",
                "evidence": evidence,
            },
        ],
        "relationships": [
            {
                "source_id": "p",
                "target_id": "e",
                "type": "claims_identity",
                "evidence": evidence,
            }
        ],
    }
    first = service.submit(mid)
    store.complete(first, assessment)
    first_person = next(
        e["id"] for e in store.graph()["entities"] if e["type"] == "person"
    )
    second = service.submit(mid)
    store.complete(second, assessment)
    graph = store.graph()
    assert len(graph["relationships"]) == 1
    assert len(graph["entities"]) == 2
    assert graph["relationships"][0]["analysis_run_id"] == second
    assert (
        next(e["id"] for e in graph["entities"] if e["type"] == "person")
        != first_person
    )


def test_queue_saturation_preserves_message(settings):
    store = SQLiteStore(settings.path(settings.database_path))
    service = AnalysisService(store, FakeProvider(), settings)
    for _ in range(20):
        mid, _ = store.ingest(normalize("Hello"))
        service.submit(mid)
    mid, _ = store.ingest(normalize("Hello"))
    with pytest.raises(AppError) as error:
        service.submit(mid)
    assert error.value.status == 429
    assert store.message(mid)["body"] == "Hello"
    assert store.latest(mid) is None


def test_worker_processes_http_submission(settings):
    import time

    with TestClient(create_app(settings, FakeProvider())) as client:
        response = client.post("/emails", json={"raw_text": "Hello"})
        run_id = response.json()["analysis_run_id"]
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            run = client.get("/analyses/" + run_id).json()
            if run["status"] == "completed":
                break
            time.sleep(0.01)
        assert run["status"] == "completed"
        assert run["extraction_metadata"]["attempts"] == 1
        assert "prompt_snapshots" not in run


def test_real_seed_restart_import(settings):
    from pathlib import Path

    settings.seed_path = str(
        Path(__file__).resolve().parents[2] / "mock_mailbox_data.json"
    )
    for _ in range(2):
        with TestClient(create_app(settings, FakeProvider())) as client:
            items = client.get("/emails").json()
            assert len(items) == 10
            assert {item["id"] for item in items} == {f"E{i:03}" for i in range(1, 11)}
            detail = client.get("/emails/E004").json()
            assert "9902" in detail["sources"][1]["text"]


def test_pdf_text_layer_and_eml_attachment():
    from email.message import EmailMessage
    from io import BytesIO

    from pypdf import PdfWriter
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    writer = PdfWriter()
    page = writer.add_blank_page(width=200, height=200)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {NameObject("/F1"): writer._add_object(font)}
            )
        }
    )
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 20 100 Td (Invoice USD 100) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(stream)
    output = BytesIO()
    writer.write(output)
    assert "Invoice USD 100" in upload("invoice.pdf", output.getvalue())["body"]
    message = EmailMessage()
    message["From"] = "a@example.com"
    message["To"] = "b@example.com"
    message.set_content("Hello")
    message.add_attachment("Invoice USD 100", subtype="plain", filename="invoice.txt")
    message.add_attachment(
        b"ignored",
        maintype="application",
        subtype="octet-stream",
        filename="unknown.bin",
    )
    result = upload("mail.eml", message.as_bytes())
    assert "Invoice USD 100" in result["sources"][1]["text"]
    assert result["warnings"]


def test_configuration_and_invalid_prompt(settings):
    settings.llm_provider = "groq"
    settings.groq_api_key = ""
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        create_app(settings)
    settings.llm_provider = "ollama"
    settings.agent_a_system_prompt_path = "does-not-exist.txt"
    with pytest.raises(RuntimeError, match="prompt"):
        create_app(settings)


def test_html_only_eml_preserves_inert_link_evidence():
    from email.message import EmailMessage

    message = EmailMessage()
    message["From"] = "security@example.com"
    message["Subject"] = "Reset request"
    message.set_content(
        '<html><head><style>hidden css</style></head><body><p>Reset now</p><a href="https://example.com/reset">Verify</a><script>hidden script</script></body></html>',
        subtype="html",
    )
    result = upload("mail.eml", message.as_bytes())
    assert "Reset now" in result["body"]
    assert "https://example.com/reset" in result["body"]
    assert "hidden script" not in result["body"]
    assert "hidden css" not in result["body"]
    assert "<html>" not in result["body"]
