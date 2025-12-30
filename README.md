# Stock Report Hub (MVP)
매일 아침 웹에서 여러 증권/리서치 리포트(HTML/PDF)를 수집 → 텍스트 추출 → 종목(티커)별로 묶어 요약/분석 → 웹에서 조회하는 서비스 (MVP).

## 구성
- `backend/` : FastAPI + SQLite (수집/저장/분석 API)
- `frontend/` : React (Vite) 대시보드
- `scripts/` : 개발 편의용 쉘 스크립트

## 빠른 시작 (macOS/Linux)
1) 백엔드
```bash
cd backend
cp .env.example .env
bash ../scripts/dev_backend.sh
```

2) 프론트엔드
```bash
cd frontend
npm install
npm run dev
```

- 프론트: http://localhost:5173
- 백엔드: http://localhost:8000 (Swagger: /docs)

## 리포트 수집
- MVP는 `NAVER_MOBILE_RESEARCH_URLS`에 넣은 URL을 대상으로 HTML을 수집합니다.
- PDF는 `PDF_URLS`에 넣으면 다운로드 후 텍스트 추출을 시도합니다(간단 구현).

## OpenAI 요약
- 실제 운영 시 `OPENAI_API_KEY`를 `.env`에 넣고 사용하세요.
- 키가 없으면 백엔드는 "모의(placeholder) 요약"을 반환하도록 되어 있습니다.

## 스케줄링(운영)
- 로컬: cron 또는 GitHub Actions/Cloud Scheduler로 `python -m app.jobs.run_daily` 실행
- 운영: 컨테이너/Docker + cron sidecar 등으로 확장 가능

## 주의
- 사이트 약관/robots.txt를 준수하세요.
- 과도한 크롤링은 차단될 수 있으니 `RATE_LIMIT_*` 설정을 조정하세요.
