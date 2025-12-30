import React, { useEffect, useMemo, useState } from "react";
import { listTickers, getTickerSummary, runDaily, Ticker, TickerSummary } from "../lib/api";

export default function App() {
  const [tickers, setTickers] = useState<Ticker[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [summary, setSummary] = useState<TickerSummary | null>(null);
  const [status, setStatus] = useState<string>("");

  useEffect(() => {
    listTickers()
      .then((t) => {
        setTickers(t);
        if (t.length) setSelected(t[0].symbol);
      })
      .catch((e) => setStatus(String(e)));
  }, []);

  useEffect(() => {
    if (!selected) return;
    setSummary(null);
    getTickerSummary(selected)
      .then(setSummary)
      .catch((e) => setStatus(String(e)));
  }, [selected]);

  const selectedName = useMemo(() => tickers.find((x) => x.symbol === selected)?.name ?? "", [tickers, selected]);

  return (
    <div style={{ maxWidth: 980, margin: "24px auto", fontFamily: "system-ui, -apple-system, Segoe UI, Roboto" }}>
      <h1>Stock Report Hub (MVP)</h1>

      <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <button
          onClick={async () => {
            setStatus("Running daily pipeline...");
            try {
              const r = await runDaily();
              setStatus(`Done. fetched=${r.fetched_reports}, mentions=${r.mentions_created}, summaries=${r.summaries_created}, asof=${r.asof_date}`);
              const s = await getTickerSummary(selected);
              setSummary(s);
            } catch (e) {
              setStatus(String(e));
            }
          }}
        >
          Run Daily (manual)
        </button>

        <label>
          종목 선택:&nbsp;
          <select value={selected} onChange={(e) => setSelected(e.target.value)}>
            {tickers.map((t) => (
              <option key={t.symbol} value={t.symbol}>
                {t.name} ({t.symbol})
              </option>
            ))}
          </select>
        </label>
      </div>

      {status && <p style={{ marginTop: 12 }}>{status}</p>}

      <hr style={{ margin: "18px 0" }} />

      <h2>
        {selectedName} ({selected})
      </h2>

      {!summary ? (
        <p>요약을 불러오는 중... (없다면 Run Daily를 먼저 눌러주세요)</p>
      ) : (
        <div>
          <p>
            <b>As-of:</b> {summary.asof_date} &nbsp; <b>Confidence:</b> {summary.confidence}
          </p>
          <p style={{ whiteSpace: "pre-wrap", lineHeight: 1.55 }}>{summary.summary}</p>
          {summary.bullets?.length ? (
            <ul>
              {summary.bullets.map((b, i) => (
                <li key={i}>{b}</li>
              ))}
            </ul>
          ) : null}
        </div>
      )}

      <hr style={{ margin: "18px 0" }} />
      <p style={{ color: "#666" }}>
        백엔드 설정은 <code>backend/.env</code>에서 URLs를 넣고 실행하세요.
      </p>
    </div>
  );
}
