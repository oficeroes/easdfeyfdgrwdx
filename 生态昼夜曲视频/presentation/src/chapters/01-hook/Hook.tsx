import "./Hook.css";

interface Props {
  step: number;
}

export default function Hook({ step }: Props) {
  // ── Step 0: 澳門不夜城 hero ──
  if (step === 0) {
    return (
      <div className="hk-stage">
        <div className="hk-city-bg" />
        <div className="hk-glow-bar" />
        <div className="hk-s0">
          <span className="hk-pretitle">澳門生物多樣性研究 2025–2026</span>
          <div className="hk-rule-line" />
          <h1 className="hk-main-title">生態晝夜曲</h1>
          <p className="hk-subtitle">誰還按自己的生物鐘生活？</p>
          <div className="hk-tag-row">
            <span className="hk-tag">51,853 條記錄</span>
            <span className="hk-tag-sep">·</span>
            <span className="hk-tag">2 年觀測</span>
            <span className="hk-tag-sep">·</span>
            <span className="hk-tag">12+ 生物類群</span>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 1: 光明 vs 黑暗 反差 ──
  if (step === 1) {
    return (
      <div className="hk-stage">
        <div className="hk-city-bg" />
        <div className="hk-s1">
          <div className="hk-contrast-row">
            <div className="hk-contrast-col">
              <svg className="hk-contrast-icon" viewBox="0 0 80 80" fill="none">
                <circle cx="40" cy="40" r="16" fill="var(--accent)" opacity="0.9" />
                {[0,45,90,135,180,225,270,315].map((deg, i) => (
                  <line key={i}
                    x1={40 + 22 * Math.cos((deg * Math.PI) / 180)}
                    y1={40 + 22 * Math.sin((deg * Math.PI) / 180)}
                    x2={40 + 32 * Math.cos((deg * Math.PI) / 180)}
                    y2={40 + 32 * Math.sin((deg * Math.PI) / 180)}
                    stroke="var(--accent)" strokeWidth="3" strokeLinecap="round"
                  />
                ))}
              </svg>
              <p className="hk-contrast-label">燈光徹夜不息</p>
              <p className="hk-contrast-sub">澳門半島 · 不夜城</p>
            </div>
            <div className="hk-contrast-divider" />
            <div className="hk-contrast-col">
              <svg className="hk-contrast-icon" viewBox="0 0 80 80" fill="none">
                <path d="M50 16 A26 26 0 1 0 50 64 A18 18 0 1 1 50 16Z" fill="var(--text-2)" opacity="0.75" />
                <circle cx="58" cy="20" r="3.5" fill="var(--text-mute)" opacity="0.5" />
                <circle cx="65" cy="34" r="2.5" fill="var(--text-mute)" opacity="0.4" />
                <circle cx="55" cy="14" r="2" fill="var(--text-mute)" opacity="0.35" />
              </svg>
              <p className="hk-contrast-label">有自己的生物鐘</p>
              <p className="hk-contrast-sub">夜行生命 · 節律自存</p>
            </div>
          </div>
          <div className="hk-quote-box">
            <p className="hk-contrast-quote">它們靠的是黑暗，不是光。</p>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 2: 三個核心數字 ──
  if (step === 2) {
    return (
      <div className="hk-stage">
        <div className="hk-city-bg" />
        <div className="hk-s2">
          <span className="hk-s2-label">核心發現 · 三個數字</span>
          <div className="hk-three-nums">
            <div className="hk-num-card hk-visible">
              <span className="hk-big-num hero-num">39%</span>
              <p className="hk-num-title">兩年物種相似度</p>
              <p className="hk-num-desc">Jaccard 指數<br />物種組成明顯更替<br />共有種僅 1,399 種</p>
            </div>
            <div className="hk-num-divider" />
            <div className="hk-num-card hk-visible" style={{ animationDelay: "0.15s" }}>
              <span className="hk-big-num hero-num">71.7%</span>
              <p className="hk-num-title">兩棲類夜間活動比例</p>
              <p className="hk-num-desc">焦點類群最高<br />303 條記錄中 215 條在夜間<br />高峰 19:00</p>
            </div>
            <div className="hk-num-divider" />
            <div className="hk-num-card hk-visible" style={{ animationDelay: "0.30s" }}>
              <span className="hk-big-num hero-num">37.6%</span>
              <p className="hk-num-title">路環夜行比例</p>
              <p className="hk-num-desc">氹仔中高光區的 7.1 倍<br />半島的 2.2 倍<br />澳門的暗夜孤島</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 3: 研究規模 ──
  if (step === 3) {
    return (
      <div className="hk-stage">
        <div className="hk-city-bg" />
        <div className="hk-s3">
          <span className="hk-s2-label">研究規模</span>
          <div className="hk-data-strip">
            <div className="hk-data-item">
              <span className="hk-data-num hero-num">2</span>
              <span className="hk-data-unit">年觀測數據</span>
              <span className="hk-data-sub">2025 · 2026</span>
            </div>
            <div className="hk-num-divider" style={{ height: 90 }} />
            <div className="hk-data-item">
              <span className="hk-data-num hero-num">51,853</span>
              <span className="hk-data-unit">條有效記錄</span>
              <span className="hk-data-sub">33,486 + 18,367</span>
            </div>
            <div className="hk-num-divider" style={{ height: 90 }} />
            <div className="hk-data-item">
              <span className="hk-data-num hero-num">12+</span>
              <span className="hk-data-unit">個生物類群</span>
              <span className="hk-data-sub">植物·昆蟲·鳥類·兩棲</span>
            </div>
          </div>
          <p className="hk-research-quote">把這座城市的生態活動，畫成了一個時鐘。</p>
        </div>
      </div>
    );
  }

  // ── Step 4: 時鐘視覺 ──
  if (step === 4) {
    const R = 175;
    const cx = 210;
    const cy = 210;
    const toRad = (h: number) => ((h / 12) * Math.PI) - Math.PI / 2;
    const tickHours = [0, 3, 6, 9, 12, 15, 18, 21];

    return (
      <div className="hk-stage">
        <div className="hk-city-bg" />
        <div className="hk-s4">
          <div className="hk-clock-wrap">
            <svg className="hk-clock-svg" viewBox="0 0 420 420" fill="none">
              {/* 夜晚：右半圓 18:00→06:00（x>cx） */}
              <path
                d={`M ${cx} ${cy} L ${cx} ${cy - R} A ${R} ${R} 0 0 1 ${cx} ${cy + R} Z`}
                fill="var(--accent)"
                style={{ animation: "hk-fill-night 0.9s ease 0.3s both", opacity: 0 }}
              />
              {/* 白天：左半圓 06:00→18:00（x<cx） */}
              <path
                d={`M ${cx} ${cy} L ${cx} ${cy - R} A ${R} ${R} 0 0 0 ${cx} ${cy + R} Z`}
                fill="var(--text)"
                style={{ animation: "hk-fill-day 0.9s ease 0.1s both", opacity: 0 }}
              />
              {/* 圓框 */}
              <circle cx={cx} cy={cy} r={R}
                stroke="var(--text)" strokeWidth="2.5"
                strokeDasharray="1100" strokeDashoffset="1100"
                style={{ animation: "hk-dash-draw 1.1s cubic-bezier(0.4,0,0.2,1) 0.1s forwards" }}
              />
              {tickHours.map((h) => {
                const angle = toRad(h);
                const x1 = cx + (R - 18) * Math.cos(angle);
                const y1 = cy + (R - 18) * Math.sin(angle);
                const x2 = cx + R * Math.cos(angle);
                const y2 = cy + R * Math.sin(angle);
                return (
                  <line key={h} x1={x1} y1={y1} x2={x2} y2={y2}
                    stroke="var(--text)" strokeWidth={h % 6 === 0 ? 3.5 : 1.5}
                    strokeLinecap="round" opacity={h % 6 === 0 ? 0.9 : 0.4}
                  />
                );
              })}
              {[
                { h: 0,  label: "00:00", dx: 0,   dy: -28 },
                { h: 6,  label: "06:00", dx: -32, dy: 0   },
                { h: 12, label: "12:00", dx: 0,   dy: 28  },
                { h: 18, label: "18:00", dx: 30,  dy: 0   },
              ].map(({ h, label, dx, dy }) => {
                const angle = toRad(h);
                const tx = cx + (R + 34) * Math.cos(angle) + dx;
                const ty = cy + (R + 34) * Math.sin(angle) + dy;
                return (
                  <text key={h} x={tx} y={ty} textAnchor="middle" dominantBaseline="middle"
                    fill="var(--text-mute)" style={{ fontSize: 14, fontFamily: "var(--font-mono)" }}>
                    {label}
                  </text>
                );
              })}
              <text x={cx - 62} y={cy - 16} textAnchor="middle" dominantBaseline="middle"
                fill="var(--text)" style={{ fontSize: 18, fontFamily: "var(--font-body)" }}>白天</text>
              <text x={cx - 62} y={cy + 16} textAnchor="middle" dominantBaseline="middle"
                fill="var(--text-mute)" style={{ fontSize: 13, fontFamily: "var(--font-mono)" }}>3.1% 夜行</text>
              <text x={cx + 62} y={cy - 16} textAnchor="middle" dominantBaseline="middle"
                fill="var(--accent)" style={{ fontSize: 18, fontFamily: "var(--font-body)" }}>夜晚</text>
              <text x={cx + 62} y={cy + 16} textAnchor="middle" dominantBaseline="middle"
                fill="var(--accent)" style={{ fontSize: 13, fontFamily: "var(--font-mono)", opacity: 0.85 }}>71.7% 兩棲</text>
              <circle cx={cx} cy={cy} r={5} fill="var(--text)" opacity="0.7" />
            </svg>
          </div>
          <div className="hk-clock-legend">
            <span className="hk-legend-day">● 白天（06:00–18:00）鳥類 · 昆蟲</span>
            <span className="hk-legend-sep">　|　</span>
            <span className="hk-legend-night">● 夜晚（18:00–06:00）兩棲 · 夜行昆蟲</span>
          </div>
          <p className="hk-clock-caption">看看在越來越亮的澳門，夜晚的低語，還剩多少。</p>
        </div>
      </div>
    );
  }

  return null;
}
