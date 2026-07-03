import "./NightClock.css";

interface Props {
  step: number;
}

// ── Mini clock: right semicircle = night, highlighted hour sector ──
function NightClockSvg({ highlightHour }: { highlightHour?: number }) {
  const R = 130; const cx = 150; const cy = 150;
  const toRad = (h: number) => (h / 12) * Math.PI - Math.PI / 2;
  return (
    <svg className="nc-mini-clock" viewBox="0 0 300 300" fill="none">
      {/* 白天左半圓底色 */}
      <path
        d={`M ${cx} ${cy} L ${cx} ${cy - R} A ${R} ${R} 0 0 0 ${cx} ${cy + R} Z`}
        fill="var(--text)" opacity="0.05"
      />
      {/* 夜晚右半圓底色 (highlighted) */}
      <path
        d={`M ${cx} ${cy} L ${cx} ${cy - R} A ${R} ${R} 0 0 1 ${cx} ${cy + R} Z`}
        fill="var(--accent)" opacity="0.18"
      />
      <circle cx={cx} cy={cy} r={R} stroke="var(--rule)" strokeWidth="1.5" />
      {/* 高亮時段扇形 */}
      {highlightHour !== undefined && (() => {
        const a1 = toRad(highlightHour % 12);
        const a2 = toRad((highlightHour % 12) + 1);
        const x1 = cx + R * Math.cos(a1); const y1 = cy + R * Math.sin(a1);
        const x2 = cx + R * Math.cos(a2); const y2 = cy + R * Math.sin(a2);
        return (
          <path
            d={`M ${cx} ${cy} L ${x1} ${y1} A ${R} ${R} 0 0 1 ${x2} ${y2} Z`}
            fill="var(--accent)" opacity="0.72"
            style={{ animation: "nc-sector-in 0.5s ease both" }}
          />
        );
      })()}
      {/* 刻度與時間標注 */}
      {[0, 3, 6, 9, 12, 15, 18, 21].map(h => {
        const a = toRad(h % 12);
        return (
          <g key={h}>
            <line
              x1={cx + (R - 12) * Math.cos(a)} y1={cy + (R - 12) * Math.sin(a)}
              x2={cx + R * Math.cos(a)}           y2={cy + R * Math.sin(a)}
              stroke="var(--text-mute)" strokeWidth={h % 6 === 0 ? 2.5 : 1}
            />
            <text
              x={cx + (R + 18) * Math.cos(a)} y={cy + (R + 18) * Math.sin(a)}
              textAnchor="middle" dominantBaseline="middle"
              fill="var(--text-mute)"
              style={{ fontSize: 11, fontFamily: "var(--font-mono)" }}
            >
              {String(h).padStart(2, "0")}
            </text>
          </g>
        );
      })}
      {/* 夜晚分隔線 */}
      <line x1={cx} y1={cy - R - 4} x2={cx} y2={cy + R + 4} stroke="var(--rule)" strokeWidth="1" strokeDasharray="4 3" />
      <circle cx={cx} cy={cy} r={4} fill="var(--text)" opacity="0.4" />
    </svg>
  );
}

export default function NightClock({ step }: Props) {

  // ── Step 0: 19:00 兩棲類登場 ──
  if (step === 0) {
    const species = [
      { name: "黑眶蟾蜍", count: 90 },
      { name: "花狹口蛙", count: 50 },
    ];
    const max = 90;
    return (
      <div className="nc-stage">
        <div className="nc-lr">
          <div className="nc-left">
            <NightClockSvg highlightHour={7} />
            <span className="nc-time-label">19:00</span>
            <span className="nc-time-sub">215 條夜間記錄（71.7%）</span>
          </div>
          <div className="nc-right">
            <span className="nc-section-label">夜晚的時鐘 · 兩棲類</span>
            <h2 className="nc-title">夜行兩棲類登場</h2>
            <div className="nc-sp-list">
              {species.map((s, i) => (
                <div key={i} className="nc-sp-row" style={{ animationDelay: `${i * 0.09}s` }}>
                  <span className="nc-sp-name">{s.name}</span>
                  <div className="nc-sp-bar-wrap">
                    <div className="nc-sp-bar" style={{ width: `${(s.count / max) * 100}%` }} />
                  </div>
                  <span className="nc-sp-count">{s.count}</span>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 12, display: "flex", alignItems: "baseline", gap: 8 }}>
              <span className="hero-num" style={{ fontSize: 68 }}>71.7</span>
              <span style={{ fontFamily: "var(--font-body)", fontSize: 22, color: "var(--text-2)" }}>% 在夜間</span>
            </div>
            <p style={{ fontFamily: "var(--font-body)", fontSize: 18, color: "var(--text-mute)", margin: 0 }}>
              303 條總記錄 · 215 條夜間
            </p>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 1: 三類夜間比例對比 ──
  if (step === 1) {
    const trio = [
      { name: "兩棲類", pct: 71.7, icon: "🐸", color: "var(--accent)",     opacity: 0.70, note: "215 / 303 條" },
      { name: "昆蟲",   pct: 18.7, icon: "🪲", color: "var(--text-2)",     opacity: 0.60, note: "676 / 3,612 條" },
      { name: "鳥類",   pct:  3.1, icon: "🐦", color: "var(--text-mute)",  opacity: 0.50, note: "90 / 2,943 條" },
    ];
    const maxH = 280;
    return (
      <div className="nc-stage">
        <div className="nc-s1">
          <span className="nc-section-label">夜間活動比例 · 三大類群比較</span>
          <div className="nc-trio">
            {trio.map((t, i) => (
              <div key={i} className="nc-trio-col" style={{ animationDelay: `${i * 0.1}s` }}>
                <span className="nc-trio-pct" style={{ color: t.color }}>{t.pct}%</span>
                <div className="nc-trio-bar-wrap" style={{ height: maxH }}>
                  <div
                    className="nc-trio-bar"
                    style={{
                      height: `${(t.pct / 71.7) * maxH}px`,
                      background: t.color,
                      opacity: t.opacity,
                    }}
                  />
                </div>
                <span className="nc-trio-icon">{t.icon}</span>
                <span className="nc-trio-name">{t.name}</span>
                <span className="nc-trio-note">{t.note}</span>
              </div>
            ))}
          </div>
          <p className="nc-s1-caption">同一個城市，同一個夜晚，三條截然不同的生命曲線</p>
        </div>
      </div>
    );
  }

  // ── Step 2: 兩棲類四種詳情 ──
  if (step === 2) {
    const species = [
      { name: "黑眶蟾蜍", count: 90 },
      { name: "花狹口蛙", count: 50 },
      { name: "斑腿泛樹蛙", count: 43 },
      { name: "溫室蟾",   count: 23 },
    ];
    const max = 90;
    return (
      <div className="nc-stage">
        <div className="nc-s2">
          <span className="nc-section-label">夜間兩棲類 · 四種詳情（215 條夜間記錄）</span>
          <div className="nc-sp-cards">
            {species.map((s, i) => (
              <div key={i} className="nc-sp-card" style={{ animationDelay: `${i * 0.1}s` }}>
                <span className="nc-sp-card-name">{s.name}</span>
                <span className="hero-num nc-sp-card-num">{s.count}</span>
                <span className="nc-sp-card-unit">條記錄</span>
                <div className="nc-sp-card-bar-wrap">
                  <div className="nc-sp-card-bar" style={{ width: `${(s.count / max) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
          <p className="nc-s2-note">
            四種蛙類共同構成澳門夜間最密集的聲景
          </p>
        </div>
      </div>
    );
  }

  // ── Step 3: 21:00 軟體動物高峰 + 夜行昆蟲 ──
  if (step === 3) {
    const insects = [
      { name: "麗叩甲",   count: 35 },
      { name: "東方水蠊", count: 31 },
      { name: "美洲大蠊", count: 26 },
    ];
    const max = 35;
    return (
      <div className="nc-stage">
        <div className="nc-lr">
          <div className="nc-left">
            <NightClockSvg highlightHour={9} />
            <span className="nc-time-label">21:00</span>
            <span className="nc-time-sub">軟體動物活動高峰</span>
          </div>
          <div className="nc-right">
            <span className="nc-section-label">夜晚的時鐘 · 昆蟲與軟體動物</span>
            <div className="nc-mol-badge">
              <span className="nc-mol-label">MOLLUSCA · 軟體動物</span>
              <span className="nc-mol-text">21:00 達到活動高峰</span>
            </div>
            <h2 className="nc-title" style={{ fontSize: 28 }}>夜行昆蟲（676 條 · 18.7%）</h2>
            <div className="nc-insect-grid">
              {insects.map((ins, i) => (
                <div key={i} className="nc-ins-row" style={{ animationDelay: `${i * 0.09}s` }}>
                  <span className="nc-ins-name">{ins.name}</span>
                  <div className="nc-ins-bar-wrap">
                    <div className="nc-ins-bar" style={{ width: `${(ins.count / max) * 100}%` }} />
                  </div>
                  <span className="nc-ins-count">{ins.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 4: 深夜鳥類與光污染 ──
  if (step === 4) {
    const birds = [
      { name: "鵲鴝",   count: 14 },
      { name: "白頭鵯", count: 8  },
      { name: "麻雀",   count: 7  },
    ];
    const max = 14;
    return (
      <div className="nc-stage">
        <div className="nc-lr">
          <div className="nc-left">
            <NightClockSvg highlightHour={0} />
            <span className="nc-time-label" style={{ color: "var(--text-mute)" }}>00:00–05:00</span>
            <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 4 }}>
              <span className="hero-num" style={{ fontSize: 56, color: "var(--text-mute)" }}>90</span>
              <span style={{ fontFamily: "var(--font-body)", fontSize: 18, color: "var(--text-mute)" }}>條夜行性鳥類</span>
            </div>
          </div>
          <div className="nc-right">
            <span className="nc-section-label">夜晚的時鐘 · 深夜鳥類</span>
            <h2 className="nc-title">深夜的鳥類記錄</h2>
            <div className="nc-bird-grid">
              {birds.map((b, i) => (
                <div key={i} className="nc-bird-row" style={{ animationDelay: `${i * 0.09}s` }}>
                  <span className="nc-bird-name">{b.name}</span>
                  <div className="nc-bird-bar-wrap">
                    <div className="nc-bird-bar" style={{ width: `${(b.count / max) * 100}%` }} />
                  </div>
                  <span className="nc-bird-count">{b.count}</span>
                </div>
              ))}
            </div>
            <p className="nc-s4-note">
              鵲鴝、白頭鵯、麻雀——<br />
              本應是白天的物種，卻出現在深夜
            </p>
            <p className="nc-light-warn">
              光污染正在打亂城市鳥類的生理節律
            </p>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 5: 三組數字鎖定 + 結語 ──
  if (step === 5) {
    const locks = [
      { num: "71.7%", taxon: "兩棲類", label: "夜間比例", color: "var(--accent)", delay: "0s" },
      { num: "18.7%", taxon: "昆蟲",   label: "夜間比例", color: "var(--text-2)", delay: "0.12s" },
      { num: "3.1%",  taxon: "鳥類",   label: "夜間比例", color: "var(--text-mute)", delay: "0.24s" },
    ];
    return (
      <div className="nc-stage">
        <div className="nc-s5">
          <span className="nc-section-label">夜晚的時鐘 · 數字總覽</span>
          <div style={{ display: "flex", gap: 48, alignItems: "center" }}>
            <div className="nc-s5-clock-wrap">
              <NightClockSvg />
            </div>
            <div className="nc-lock-row">
              {locks.map((l, i) => (
                <div key={i} className="nc-lock-col" style={{ animationDelay: l.delay }}>
                  <span className="hero-num nc-lock-num" style={{ color: l.color }}>{l.num}</span>
                  <span className="nc-lock-taxon">{l.taxon}</span>
                  <span className="nc-lock-label">{l.label}</span>
                </div>
              ))}
            </div>
          </div>
          <p className="nc-conclusion">
            夜晚不是空的<br />
            <span style={{ fontSize: 22, color: "var(--text-2)", fontFamily: "var(--font-body)" }}>
              它只是換了一批主角
            </span>
          </p>
        </div>
      </div>
    );
  }

  return null;
}
