import "./Space.css";

interface Props {
  step: number;
}

export default function Space({ step }: Props) {
  // ── Step 0: 三區地圖 ──
  if (step === 0) {
    return (
      <div className="sp-stage">
        <div className="sp-s0">
          <div className="sp-map-header">
            <span className="sp-map-kicker">空間分佈 · 光照分區</span>
            <h2 className="sp-map-title">澳門三個光照區域</h2>
          </div>

          {/* SVG simplified Macau map — three zones stacked roughly N→S */}
          <svg className="sp-map-svg" viewBox="0 0 520 480" fill="none">
            {/* ── 底色海域 ── */}
            <rect width="520" height="480" fill="color-mix(in srgb, var(--rule) 20%, transparent)" rx="8" />

            {/* ── Zone 1: 半島 (澳門半島) — top, brightest ── */}
            {/* Simplified as irregular polygon, northern lozenge */}
            <path
              d="M 200 40 L 320 40 L 345 80 L 340 160 L 290 180 L 230 180 L 185 160 L 178 100 Z"
              fill="var(--accent)"
              opacity="0.72"
              stroke="var(--bg, #fff)"
              strokeWidth="2"
            />
            <text x="262" y="112" textAnchor="middle" dominantBaseline="middle"
              fill="var(--bg, #fff)" style={{ fontSize: 20, fontFamily: "var(--font-display-cn)", fontWeight: 700 }}>
              澳門半島
            </text>
            <text x="262" y="136" textAnchor="middle" dominantBaseline="middle"
              fill="var(--bg, #fff)" style={{ fontSize: 13, fontFamily: "var(--font-mono)", opacity: 0.9 }}>
              高光區
            </text>

            {/* ── 連接水道 ── */}
            <rect x="220" y="178" width="80" height="28" fill="color-mix(in srgb, var(--rule) 35%, transparent)" />

            {/* ── Zone 2: 氹仔+路氹城 — middle, medium ── */}
            <path
              d="M 170 205 L 352 205 L 365 260 L 355 320 L 300 338 L 215 338 L 162 318 L 155 260 Z"
              fill="var(--accent)"
              opacity="0.42"
              stroke="var(--bg, #fff)"
              strokeWidth="2"
            />
            <text x="260" y="262" textAnchor="middle" dominantBaseline="middle"
              fill="var(--text)" style={{ fontSize: 20, fontFamily: "var(--font-display-cn)", fontWeight: 700 }}>
              氹仔 · 路氹城
            </text>
            <text x="260" y="286" textAnchor="middle" dominantBaseline="middle"
              fill="var(--text-mute)" style={{ fontSize: 13, fontFamily: "var(--font-mono)" }}>
              中高光區
            </text>

            {/* ── 連接水道 2 ── */}
            <rect x="215" y="336" width="90" height="22" fill="color-mix(in srgb, var(--rule) 35%, transparent)" />

            {/* ── Zone 3: 路環 — bottom, darkest ── */}
            <path
              d="M 195 357 L 325 357 L 342 400 L 330 445 L 260 458 L 192 445 L 178 400 Z"
              fill="var(--text-mute)"
              opacity="0.38"
              stroke="var(--bg, #fff)"
              strokeWidth="2"
            />
            <text x="260" y="400" textAnchor="middle" dominantBaseline="middle"
              fill="var(--text)" style={{ fontSize: 20, fontFamily: "var(--font-display-cn)", fontWeight: 700 }}>
              路環
            </text>
            <text x="260" y="424" textAnchor="middle" dominantBaseline="middle"
              fill="var(--text-mute)" style={{ fontSize: 13, fontFamily: "var(--font-mono)" }}>
              相對低光區
            </text>

            {/* ── 羅盤方向 N ── */}
            <text x="468" y="50" textAnchor="middle" dominantBaseline="middle"
              fill="var(--text-mute)" style={{ fontSize: 16, fontFamily: "var(--font-mono)", opacity: 0.5 }}>
              N ↑
            </text>

            {/* ── 比例標 ── */}
            <line x1="32" y1="448" x2="82" y2="448" stroke="var(--text-mute)" strokeWidth="1.5" opacity="0.45" />
            <text x="57" y="464" textAnchor="middle" dominantBaseline="middle"
              fill="var(--text-mute)" style={{ fontSize: 11, fontFamily: "var(--font-mono)", opacity: 0.45 }}>
              示意圖
            </text>
          </svg>

          <div className="sp-map-legend">
            <div className="sp-legend-item">
              <span className="sp-legend-dot sp-legend-dot--high" />
              高光區 · 半島
            </div>
            <div className="sp-legend-item">
              <span className="sp-legend-dot sp-legend-dot--mid" />
              中高光區 · 氹仔路氹城
            </div>
            <div className="sp-legend-item">
              <span className="sp-legend-dot sp-legend-dot--low" />
              相對低光區 · 路環
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 1: 三區夜行比例對比 ──
  if (step === 1) {
    const zones = [
      {
        name: "澳門半島",
        sub: "高光區",
        pct: 16.9,
        barWidth: "44.9%",
        key: "high" as const,
      },
      {
        name: "氹仔 · 路氹城",
        sub: "中高光區",
        pct: 5.3,
        barWidth: "14.1%",
        key: "mid" as const,
      },
      {
        name: "路環",
        sub: "相對低光區",
        pct: 37.6,
        barWidth: "100%",
        key: "low" as const,
      },
    ];

    return (
      <div className="sp-stage">
        <div className="sp-s1">
          <div className="sp-s1-header">
            <span className="sp-s1-kicker">夜行類群比例 · 分區比較</span>
            <h2 className="sp-s1-title">三區夜行比例差距懸殊</h2>
          </div>

          <div className="sp-zone-bars">
            {zones.map((z) => (
              <div className="sp-zone-row" key={z.key}>
                <div className="sp-zone-meta">
                  <span className="sp-zone-name">{z.name}</span>
                  <span className="sp-zone-sub">{z.sub}</span>
                  <span className={`sp-zone-pct sp-zone-pct--${z.key}`}>
                    {z.pct}%
                  </span>
                </div>
                <div className="sp-zone-track">
                  <div
                    className={`sp-zone-fill sp-zone-fill--${z.key}`}
                    style={{ "--bar-target": z.barWidth } as React.CSSProperties}
                  />
                </div>
              </div>
            ))}
          </div>

          <p className="sp-s1-note">
            路環 <strong>37.6%</strong>，是氹仔中高光區的 <strong>7.1 倍</strong>
          </p>
        </div>
      </div>
    );
  }

  // ── Step 2: 路環暗夜孤島 ──
  if (step === 2) {
    return (
      <div className="sp-stage">
        <div className="sp-s2">
          <h2 className="sp-island-title">
            <em>路環</em>：事實上的暗夜孤島
          </h2>

          <div className="sp-island-stats">
            <div className="sp-island-stat">
              <span className="sp-stat-num">37.6%</span>
              <span className="sp-stat-unit">夜行比例</span>
              <span className="sp-stat-sub">三區最高</span>
            </div>
            <div className="sp-stat-divider" />
            <div className="sp-island-stat">
              <span className="sp-stat-num">1,633</span>
              <span className="sp-stat-unit">昆蟲記錄</span>
              <span className="sp-stat-sub">三區最高</span>
            </div>
            <div className="sp-stat-divider" />
            <div className="sp-island-stat">
              <span className="sp-stat-num">204</span>
              <span className="sp-stat-unit">兩棲類記錄</span>
              <span className="sp-stat-sub">三區最高</span>
            </div>
          </div>

          <p className="sp-island-quote">
            在這座不夜城裡，它是最後一片<br />還保留著黑夜節律的土地。
          </p>
        </div>
      </div>
    );
  }

  // ── Step 3: 入侵物種威脅 ──
  if (step === 3) {
    return (
      <div className="sp-stage">
        <div className="sp-s3">
          <div className="sp-threat-header">
            <span className="sp-threat-kicker">路環 · 入侵物種記錄</span>
            <h2 className="sp-threat-title">暗夜孤島，正遭入侵</h2>
          </div>

          <div className="sp-threat-cards">
            {/* 長足捷蚁 */}
            <div className="sp-threat-card">
              <svg className="sp-threat-icon" viewBox="0 0 64 64" fill="none">
                {/* 螞蟻簡筆 */}
                <ellipse cx="32" cy="44" rx="10" ry="8" fill="var(--text-mute)" opacity="0.55" />
                <ellipse cx="32" cy="30" rx="7" ry="6" fill="var(--text-mute)" opacity="0.55" />
                <ellipse cx="32" cy="18" rx="6" ry="6" fill="var(--text-mute)" opacity="0.55" />
                <line x1="32" y1="36" x2="32" y2="24" stroke="var(--text-mute)" strokeWidth="1.5" opacity="0.5" />
                <line x1="22" y1="40" x2="14" y2="32" stroke="var(--text-mute)" strokeWidth="1.5" opacity="0.4" />
                <line x1="22" y1="44" x2="12" y2="44" stroke="var(--text-mute)" strokeWidth="1.5" opacity="0.4" />
                <line x1="22" y1="48" x2="14" y2="56" stroke="var(--text-mute)" strokeWidth="1.5" opacity="0.4" />
                <line x1="42" y1="40" x2="50" y2="32" stroke="var(--text-mute)" strokeWidth="1.5" opacity="0.4" />
                <line x1="42" y1="44" x2="52" y2="44" stroke="var(--text-mute)" strokeWidth="1.5" opacity="0.4" />
                <line x1="42" y1="48" x2="50" y2="56" stroke="var(--text-mute)" strokeWidth="1.5" opacity="0.4" />
              </svg>
              <span className="sp-threat-name">長足捷蚁</span>
              <span className="sp-threat-count">17</span>
              <span className="sp-threat-count-label">條記錄</span>
              <span className="sp-threat-tag">入侵螞蟻</span>
            </div>

            {/* 溫室蟾 */}
            <div className="sp-threat-card">
              <svg className="sp-threat-icon" viewBox="0 0 64 64" fill="none">
                {/* 蟾蜍簡筆 */}
                <ellipse cx="32" cy="38" rx="18" ry="13" fill="var(--text-mute)" opacity="0.5" />
                <ellipse cx="20" cy="26" rx="7" ry="6" fill="var(--text-mute)" opacity="0.45" />
                <ellipse cx="44" cy="26" rx="7" ry="6" fill="var(--text-mute)" opacity="0.45" />
                <circle cx="20" cy="25" r="3" fill="var(--bg, #fff)" opacity="0.6" />
                <circle cx="44" cy="25" r="3" fill="var(--bg, #fff)" opacity="0.6" />
                <line x1="16" y1="50" x2="10" y2="58" stroke="var(--text-mute)" strokeWidth="2" opacity="0.4" strokeLinecap="round" />
                <line x1="48" y1="50" x2="54" y2="58" stroke="var(--text-mute)" strokeWidth="2" opacity="0.4" strokeLinecap="round" />
              </svg>
              <span className="sp-threat-name">溫室蟾</span>
              <span className="sp-threat-count">21</span>
              <span className="sp-threat-count-label">條記錄</span>
              <span className="sp-threat-tag">外來兩棲</span>
            </div>
          </div>

          <p className="sp-threat-caption">
            外來入侵物種正在悄悄滲透<br />澳門最後一片暗夜棲地。
          </p>
        </div>
      </div>
    );
  }

  // ── Step 4: 科學邊界說明 ──
  if (step === 4) {
    return (
      <div className="sp-stage">
        <div className="sp-s4">
          <span className="sp-caveat-kicker">研究邊界 · 方法說明</span>
          <div className="sp-caveat-items">
            <div className="sp-caveat-row">
              <span className="sp-caveat-mark">△</span>
              <p className="sp-caveat-text">
                三個分區基於行政區劃與文獻資料的簡化處理，<br />
                並非精確遙感光照數據，邊界並非硬性截斷。
              </p>
            </div>
            <div className="sp-caveat-row">
              <span className="sp-caveat-mark">△</span>
              <p className="sp-caveat-text">
                各區觀測強度存在差異，可能部分影響記錄數量，<br />
                需結合抽樣密度解讀絕對數字。
              </p>
            </div>
            <div className="sp-caveat-row is-signal">
              <span className="sp-caveat-mark">◎</span>
              <p className="sp-caveat-text">
                即便如此，訊號是清晰的：<br />
                路環的夜行比例差異，值得系統性的深入研究。
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
