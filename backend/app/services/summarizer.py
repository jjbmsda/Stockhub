import json
from typing import List, Dict
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """너는 주식 리서치 애널리스트다.
입력은 '같은 날짜(as-of)의 여러 리포트에서 특정 종목에 대해 언급된 스니펫 묶음'이다.
아래 형식으로 한국어로 간결하게 요약하라.

요구:
- 사실/수치/이벤트를 우선.
- 서로 다른 리포트가 '동일 주장'인지 '상충'인지 구분.
- 과도한 확신 금지. 근거가 약하면 '추정'이라고 명시.
- 투자 조언/매수·매도 지시는 하지 말고, 관찰/리스크/체크포인트로 마무리.

출력(JSON):
{
  "summary": "3~6문장 요약",
  "bullets": ["핵심1", "핵심2", "리스크/체크포인트"],
  "confidence": 0~100 (근거의 일관성과 구체성 기반)
}
"""

def _mock_summary(snippets: List[str]) -> Dict:
    # fallback if no API key
    s = " / ".join([x[:120] for x in snippets[:4]])
    return {
        "summary": f"(모의요약) 스니펫 기반 요약: {s}",
        "bullets": [
            "(모의) 리포트에서 종목 관련 이벤트/모멘텀 언급",
            "(모의) 수급/환율/실적/정책 변수 체크",
            "(모의) 다음 실적/지표 발표에 따른 변동성 가능",
        ],
        "confidence": 35,
    }

async def summarize_snippets(snippets: List[str]) -> Dict:
    if not snippets:
        return {"summary": "언급 없음", "bullets": [], "confidence": 0}

    if not settings.OPENAI_API_KEY:
        return _mock_summary(snippets)

    # Minimal OpenAI-compatible call (Responses API style not implemented here to avoid dependency).
    # We use a generic chat-completions compatible endpoint style.
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "\n\n".join(f"- {s}" for s in snippets)},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=40.0) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except Exception:
            logger.info("Model returned non-JSON; fallback to mock parse")
            return {"summary": content, "bullets": [], "confidence": 40}
