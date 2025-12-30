import re
from bs4 import BeautifulSoup
from pypdf import PdfReader

def extract_text_from_html(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "lxml")

    # best-effort title
    title = ""
    if soup.title and soup.title.text:
        title = soup.title.text.strip()

    # remove scripts/styles
    for t in soup(["script", "style", "noscript"]):
        t.decompose()

    text = soup.get_text("\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, title

def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts).strip()
