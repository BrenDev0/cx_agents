from src.knowledge_base.pdf import extract_text_from_pdf


class FakePage:
    def __init__(self, text: str | None):
        self._text = text

    def extract_text(self) -> str | None:
        return self._text


class FakePdfReader:
    def __init__(self, pages: list[FakePage]):
        self.pages = pages


def test_extract_text_from_pdf_joins_pages_with_newline(monkeypatch):
    monkeypatch.setattr(
        "src.knowledge_base.pdf.PdfReader",
        lambda _stream: FakePdfReader([FakePage("page one"), FakePage("page two")])
    )

    result = extract_text_from_pdf(b"irrelevant-bytes")

    assert result == "page one\npage two"


def test_extract_text_from_pdf_treats_none_page_text_as_empty_string(monkeypatch):
    monkeypatch.setattr(
        "src.knowledge_base.pdf.PdfReader",
        lambda _stream: FakePdfReader([FakePage("page one"), FakePage(None), FakePage("page three")])
    )

    result = extract_text_from_pdf(b"irrelevant-bytes")

    assert result == "page one\n\npage three"


def test_extract_text_from_pdf_returns_empty_string_for_no_pages(monkeypatch):
    monkeypatch.setattr(
        "src.knowledge_base.pdf.PdfReader",
        lambda _stream: FakePdfReader([])
    )

    result = extract_text_from_pdf(b"irrelevant-bytes")

    assert result == ""
