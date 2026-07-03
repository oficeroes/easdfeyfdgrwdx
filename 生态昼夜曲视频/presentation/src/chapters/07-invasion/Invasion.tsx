import "./Invasion.css";

interface Props {
  step: number;
}

const SPECIES = [
  { name: "南美蟛蜞菊", count: 183, level: "HIGH" as const },
  { name: "長足捷蟻",   count: 27,  level: "HIGH" as const },
  { name: "紅火蟻",     count: 7,   level: "HIGH" as const },
  { name: "溫室蟾",     count: 27,  level: "WATCH" as const },
  { name: "新幾內亞扁蟲", count: 7, level: "WATCH" as const },
];

export default function Invasion({ step }: Props) {
  // ── Step 0: 五種入侵物種警示卡 ──
  if (step === 0) {
    return (
      <div className="inv-stage">
        <div className="inv-s0">
          <div className="inv-s0-header">
            <span className="inv-kicker">外來入侵物種 · 五種警示</span>
          </div>
          <div className="inv-cards-row">
            {SPECIES.map((sp, i) => (
              <div
                key={sp.name}
                className={`inv-sp-card inv-sp-card--${sp.level.toLowerCase()}`}
                style={{ animationDelay: `${i * 0.09}s` }}
              >
                <div className="inv-sp-badge">
                  {sp.level === "HIGH" ? (
                    <span className="inv-badge inv-badge--high">
                      <span className="inv-badge-icon">⚠</span> 高風險
                    </span>
                  ) : (
                    <span className="inv-badge inv-badge--watch">
                      <span className="inv-badge-icon">⚠</span> 觀察
                    </span>
                  )}
                </div>
                <span className="inv-sp-name">{sp.name}</span>
                <span className="inv-sp-count hero-num">{sp.count}</span>
                <span className="inv-sp-unit">條記錄</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ── Step 1: 南美蟛蜞菊 183 條三分區分佈條圖 ──
  if (step === 1) {
    const zones = [
      { name: "半島", count: 81,  pct: 81 / 183 },
      { name: "氹仔", count: 69,  pct: 69 / 183 },
      { name: "路環", count: 27,  pct: 27 / 183 },
    ];
    const maxW = 440;
    return (
      <div className="inv-stage">
        <div className="inv-s1">
          <div className="inv-s1-left">
            <span className="inv-kicker">入侵植物 · 分區分佈</span>
            <h2 className="inv-title">南美蟛蜞菊</h2>
            <div className="inv-total-row">
              <span className="inv-total-num hero-num">183</span>
              <span className="inv-total-unit">條記錄</span>
              <span className="inv-badge inv-badge--high" style={{ marginLeft: 16 }}>
                <span className="inv-badge-icon">⚠</span> 高風險
              </span>
            </div>
            <p className="inv-note">三個分區均有分佈<br />擴散範圍已覆蓋全澳</p>
          </div>
          <div className="inv-s1-right">
            <div className="inv-bar-chart">
              {zones.map((z, i) => (
                <div key={z.name} className="inv-bar-row" style={{ animationDelay: `${i * 0.1}s` }}>
                  <span className="inv-bar-label">{z.name}</span>
                  <div className="inv-bar-track">
                    <div
                      className="inv-bar-fill"
                      style={{ width: `${z.pct * maxW}px` }}
                    />
                  </div>
                  <span className="inv-bar-count">{z.count}</span>
                  <span className="inv-bar-pct">{Math.round(z.pct * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 2: 路環受威脅 — 長足捷蟻 + 溫室蟾 ──
  if (step === 2) {
    return (
      <div className="inv-stage">
        <div className="inv-s2">
          <span className="inv-kicker">路環暗夜島嶼 · 入侵壓力</span>
          <h2 className="inv-title">暗夜孤島，同樣淪陷</h2>
          <div className="inv-coloane-row">
            <div className="inv-threat-card inv-threat-card--high">
              <span className="inv-badge inv-badge--high">
                <span className="inv-badge-icon">⚠</span> 高風險
              </span>
              <span className="inv-threat-name">長足捷蟻</span>
              <span className="inv-threat-num hero-num">17</span>
              <span className="inv-threat-unit">路環記錄</span>
              <span className="inv-threat-total">全澳共 27 條</span>
            </div>
            <div className="inv-threat-plus">+</div>
            <div className="inv-threat-card inv-threat-card--watch">
              <span className="inv-badge inv-badge--watch">
                <span className="inv-badge-icon">⚠</span> 觀察
              </span>
              <span className="inv-threat-name">溫室蟾</span>
              <span className="inv-threat-num hero-num">21</span>
              <span className="inv-threat-unit">路環記錄</span>
              <span className="inv-threat-total">全澳共 27 條</span>
            </div>
          </div>
          <div className="inv-coloane-note">
            <div className="inv-rule-bar" />
            <p className="inv-note-text">
              路環夜間兩棲類比例最高達 37.6%——<br />
              入侵物種在此擴散，影響最難挽回
            </p>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 3: 質性說明 — 點位是預警，不是擴散預測 ──
  if (step === 3) {
    return (
      <div className="inv-stage">
        <div className="inv-s3">
          <span className="inv-kicker">方法論說明</span>
          <div className="inv-quote-block">
            <div className="inv-quote-accent" />
            <p className="inv-quote-text">
              點位是早期預警，<br />不是擴散預測。
            </p>
          </div>
          <div className="inv-timing-row">
            <div className="inv-timing-card">
              <span className="inv-timing-icon">◉</span>
              <span className="inv-timing-label">現在介入</span>
              <span className="inv-timing-sub">種群未穩定<br />成本最低</span>
            </div>
            <div className="inv-timing-arrow">→</div>
            <div className="inv-timing-card inv-timing-card--dim">
              <span className="inv-timing-icon inv-timing-icon--dim">○</span>
              <span className="inv-timing-label inv-timing-label--dim">延遲介入</span>
              <span className="inv-timing-sub inv-timing-sub--dim">種群穩定後<br />難以清除</span>
            </div>
          </div>
          <p className="inv-footer-note">
            建立常態監測體系，是當下最具效益的行動
          </p>
        </div>
      </div>
    );
  }

  return null;
}
