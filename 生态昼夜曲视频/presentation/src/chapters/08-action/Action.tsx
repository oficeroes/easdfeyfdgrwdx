import "./Action.css";

interface Props {
  step: number;
}

const CARDS = [
  {
    id: "lighting",
    num: "01",
    title: "暗夜友好照明",
    subtitle: "Dark-sky Lighting",
    tag: "光汙染管理",
  },
  {
    id: "coloane",
    num: "02",
    title: "路環暗夜復查",
    subtitle: "Coloane Night Survey",
    tag: "系統調查",
  },
  {
    id: "invasion",
    num: "03",
    title: "入侵物種分級預警",
    subtitle: "Tiered Invasive Alert",
    tag: "風險管控",
  },
  {
    id: "rare",
    num: "04",
    title: "低頻物種復查",
    subtitle: "Rare Species Resurvey",
    tag: "數據品質",
  },
];

export default function Action({ step }: Props) {
  // ── Step 0: 四項建議 2×2 概覽 ──
  if (step === 0) {
    return (
      <div className="ac-stage">
        <div className="ac-s0">
          <span className="ac-kicker">行動建議 · 四項方向</span>
          <div className="ac-grid">
            {CARDS.map((c, i) => (
              <div
                key={c.id}
                className="ac-overview-card"
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                <span className="ac-card-num">{c.num}</span>
                <div className="ac-card-body">
                  <span className="ac-card-title">{c.title}</span>
                  <span className="ac-card-sub">{c.subtitle}</span>
                </div>
                <span className="ac-card-tag">{c.tag}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ── Step 1: 建議 01 + 02 展開 ──
  if (step === 1) {
    return (
      <div className="ac-stage">
        <div className="ac-s1">
          <span className="ac-kicker">建議一 · 二</span>
          <div className="ac-detail-pair">
            {/* 01 暗夜照明 */}
            <div className="ac-detail-card ac-detail-card--accent">
              <div className="ac-detail-header">
                <span className="ac-detail-num">01</span>
                <div>
                  <span className="ac-detail-title">暗夜友好照明</span>
                  <span className="ac-detail-tag">光汙染管理</span>
                </div>
              </div>
              <div className="ac-detail-stat">
                <span className="ac-stat-num hero-num">71.7%</span>
                <span className="ac-stat-desc">兩棲類夜間活動比例<br />對光汙染最敏感的類群</span>
              </div>
              <p className="ac-detail-note">
                路燈設計與亮度管理中<br />為夜行生命留出緩衝空間
              </p>
            </div>
            {/* 02 路環復查 */}
            <div className="ac-detail-card">
              <div className="ac-detail-header">
                <span className="ac-detail-num">02</span>
                <div>
                  <span className="ac-detail-title">路環暗夜復查</span>
                  <span className="ac-detail-tag">系統調查</span>
                </div>
              </div>
              <div className="ac-detail-stat">
                <span className="ac-stat-num hero-num">37.6%</span>
                <span className="ac-stat-desc">路環夜行焦點類群比例<br />氹仔中高光區的 7.1 倍</span>
              </div>
              <p className="ac-detail-note">
                系統性夜間複查，確認路環<br />能否成為澳門暗夜保育核心
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 2: 建議 03 + 04 展開 ──
  if (step === 2) {
    return (
      <div className="ac-stage">
        <div className="ac-s2">
          <span className="ac-kicker">建議三 · 四</span>
          <div className="ac-detail-pair">
            {/* 03 入侵預警 */}
            <div className="ac-detail-card">
              <div className="ac-detail-header">
                <span className="ac-detail-num">03</span>
                <div>
                  <span className="ac-detail-title">入侵物種分級預警</span>
                  <span className="ac-detail-tag">風險管控</span>
                </div>
              </div>
              <div className="ac-invasion-tiers">
                <div className="ac-tier ac-tier--high">
                  <span className="ac-tier-label">⚠ 紅色 · 高風險</span>
                  <div className="ac-tier-species">
                    <span>南美蟛蜞菊</span>
                    <span>長足捷蟻</span>
                    <span>紅火蟻</span>
                  </div>
                </div>
                <div className="ac-tier ac-tier--watch">
                  <span className="ac-tier-label">⚠ 黃色 · 觀察</span>
                  <div className="ac-tier-species">
                    <span>溫室蟾</span>
                    <span>新幾內亞扁蟲</span>
                  </div>
                </div>
              </div>
            </div>
            {/* 04 低頻復查 */}
            <div className="ac-detail-card">
              <div className="ac-detail-header">
                <span className="ac-detail-num">04</span>
                <div>
                  <span className="ac-detail-title">低頻物種復查</span>
                  <span className="ac-detail-tag">數據品質</span>
                </div>
              </div>
              <div className="ac-detail-stat">
                <span className="ac-stat-num hero-num">720</span>
                <span className="ac-stat-desc">單一點位物種<br />需影像佐證確認有效性</span>
              </div>
              <p className="ac-detail-note">
                這批資料是物種名錄<br />準確性的關鍵環節
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 3: 結語 ──
  if (step === 3) {
    return (
      <div className="ac-stage">
        <div className="ac-s3">
          {/* 時鐘裝飾 */}
          <svg className="ac-clock-deco" viewBox="0 0 200 200" fill="none">
            {/* 夜半圓 */}
            <path
              d="M 100 100 L 100 10 A 90 90 0 0 1 100 190 Z"
              fill="var(--accent)"
              opacity="0.18"
            />
            {/* 晝半圓 */}
            <path
              d="M 100 100 L 100 10 A 90 90 0 0 0 100 190 Z"
              fill="var(--text)"
              opacity="0.07"
            />
            <circle cx="100" cy="100" r="90" stroke="var(--rule)" strokeWidth="1.5" />
            {[0, 90, 180, 270].map((deg) => {
              const rad = (deg * Math.PI) / 180 - Math.PI / 2;
              return (
                <line
                  key={deg}
                  x1={100 + 78 * Math.cos(rad)}
                  y1={100 + 78 * Math.sin(rad)}
                  x2={100 + 90 * Math.cos(rad)}
                  y2={100 + 90 * Math.sin(rad)}
                  stroke="var(--text-mute)"
                  strokeWidth="2"
                />
              );
            })}
            <circle cx="100" cy="100" r="4" fill="var(--text)" opacity="0.5" />
          </svg>

          <div className="ac-closing-quote">
            <div className="ac-closing-rule" />
            <p className="ac-quote-main">
              讓城市繼續明亮，<br />
              也給夜晚的生命，<br />
              留一點黑暗。
            </p>
            <div className="ac-closing-rule" />
          </div>

          <div className="ac-closing-meta">
            <span className="ac-meta-line">澳門生物多樣性研究 2025–2026</span>
            <span className="ac-meta-sep">·</span>
            <span className="ac-meta-line">51,853 條記錄 · 兩年觀測</span>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
