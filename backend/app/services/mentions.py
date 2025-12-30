import re
from typing import Iterable

# Simple mention extractor:
# - Match ticker names (Korean) and/or codes (6-digit) in text
# - Return snippets around matches

def _make_windows(text: str, spans: list[tuple[int,int]], window: int = 120) -> list[str]:
    out = []
    for a,b in spans:
        start = max(0, a-window)
        end = min(len(text), b+window)
        snippet = text[start:end].replace("\n", " ").strip()
        out.append(snippet)
    # de-dup
    uniq = []
    seen = set()
    for s in out:
        k = s[:200]
        if k not in seen:
            uniq.append(s)
            seen.add(k)
    return uniq[:10]

def extract_mentions(text: str, ticker_symbol: str, ticker_name: str) -> list[str]:
    spans = []

    # code
    for m in re.finditer(re.escape(ticker_symbol), text):
        spans.append((m.start(), m.end()))

    # name (Korean/English)
    if ticker_name:
        for m in re.finditer(re.escape(ticker_name), text):
            spans.append((m.start(), m.end()))

    if not spans:
        return []
    spans.sort()
    return _make_windows(text, spans)
