import "./Data.css";

interface Props {
  step: number;
}

export default function DataChapter({ step }: Props) {
  // ── Step 0: 數據規模對比 ──
  if (step === 0) {
    return (
      <div className="dt-stage">
        <div className="dt-s0">
          <span className="dt-section-label">數據基礎</span>
          <div className="dt-year-compare">
            <div className="dt-year-col dt-year-2025">
              <span className="dt-year-tag">2025</span>
              <span className="dt-year-num hero-num">33,486</span>
              <span className="dt-year-unit">條有效記錄</span>
              <div className="dt-year-detail">
                <span>原始：33,571 條</span>
                <span>剔除坐標異常：85 條</span>
                <span>含圈養/栽培：5,679 條</span>
              </div>
            </div>
            <div className="dt-year-plus">+</div>
            <div className="dt-year-col dt-year-2026">
              <span className="dt-year-tag">2026</span>
              <span className="dt-year-num hero-num">18,367</span>
              <span className="dt-year-unit">條有效記錄</span>
              <div className="dt-year-detail">
                <span>原始：18,437 條</span>
                <span>剔除坐標異常：70 條</span>
                <span>全部野生自然記錄</span>
              </div>
            </div>
          </div>
          <div className="dt-total-row">
            <span className="dt-total-label">兩年合計</span>
            <span className="dt-total-num hero-num">51,853</span>
            <span className="dt-total-unit">條</span>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 1: 類群覆蓋 ──
  if (step === 1) {
    const taxa = [
      { name: "植物", en: "Plantae", records: "主體類群" },
      { name: "昆蟲", en: "Insecta", records: "最大漲幅" },
      { name: "鳥類", en: "Aves", records: "穩定類群" },
      { name: "兩棲類", en: "Amphibia", records: "夜行焦點" },
      { name: "軟體動物", en: "Mollusca", records: "夜間高峰" },
      { name: "蛛形綱", en: "Arachnida", records: "高稀有率" },
      { name: "魚類", en: "Pisces", records: "水域指示" },
      { name: "真菌", en: "Fungi", records: "最高稀有率" },
    ];
    return (
      <div className="dt-stage">
        <div className="dt-s1">
          <span className="dt-section-label">類群覆蓋 · 12+ 大類</span>
          <div className="dt-taxa-grid">
            {taxa.map((t, i) => (
              <div key={i} className="dt-taxa-card" style={{ animationDelay: `${i * 0.06}s` }}>
                <span className="dt-taxa-cn">{t.name}</span>
                <span className="dt-taxa-en">{t.en}</span>
                <span className="dt-taxa-note">{t.records}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ── Step 2: 類群結構變化（橫條圖） ──
  if (step === 2) {
    const groups = [
      { name: "植物", y25: 76.0, y26: 53.0, dir: "down" },
      { name: "昆蟲", y25: 8.7,  y26: 20.0, dir: "up" },
      { name: "鳥類", y25: 9.5,  y26: 16.4, dir: "up" },
      { name: "其他", y25: 5.8,  y26: 10.6, dir: "up" },
    ];
    return (
      <div className="dt-stage">
        <div className="dt-s2">
          <span className="dt-section-label">類群佔比變化 2025 → 2026</span>
          <div className="dt-bar-chart">
            {groups.map((g) => (
              <div key={g.name} className="dt-bar-row">
                <span className="dt-bar-label">{g.name}</span>
                <div className="dt-bar-tracks">
                  <div className="dt-bar-track">
                    <div className="dt-bar dt-bar-25" style={{ width: `${g.y25 * 0.9}%` }} />
                    <span className="dt-bar-val dt-bar-val-25">{g.y25}%</span>
                  </div>
                  <div className="dt-bar-track">
                    <div
                      className={`dt-bar ${g.dir === "up" ? "dt-bar-26-up" : "dt-bar-26-down"}`}
                      style={{ width: `${g.y26 * 0.9}%` }}
                    />
                    <span className="dt-bar-val dt-bar-val-26">
                      {g.y26}%
                      <span className={`dt-delta ${g.dir}`}>
                        {g.dir === "up" ? "▲" : "▼"}
                      </span>
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <p className="dt-note">動物界記錄反而增加 <strong>+682 條</strong>（7,792 → 8,474）</p>
        </div>
      </div>
    );
  }

  // ── Step 3: 多樣性指數 ──
  if (step === 3) {
    const indices = [
      { name: "Shannon H′", y25: "6.7060", y26: "6.4099", delta: "−0.2961", dir: "down", note: "多樣性略降" },
      { name: "Pielou J′",  y25: "0.8383", y26: "0.8428", delta: "+0.0045", dir: "up",   note: "均勻度微升" },
      { name: "Simpson 1−D", y25: "0.9974", y26: "0.9958", delta: "−0.0016", dir: "down", note: "優勢度稍降" },
    ];
    return (
      <div className="dt-stage">
        <div className="dt-s3">
          <span className="dt-section-label">多樣性指數對比</span>
          <div className="dt-index-table">
            <div className="dt-index-header">
              <span>指數</span>
              <span>2025</span>
              <span>2026</span>
              <span>變化</span>
              <span>解讀</span>
            </div>
            {indices.map((idx) => (
              <div key={idx.name} className="dt-index-row">
                <span className="dt-idx-name">{idx.name}</span>
                <span className="dt-idx-val">{idx.y25}</span>
                <span className="dt-idx-val">{idx.y26}</span>
                <span className={`dt-idx-delta ${idx.dir}`}>{idx.delta}</span>
                <span className="dt-idx-note">{idx.note}</span>
              </div>
            ))}
          </div>
          <div className="dt-index-highlight">
            <span className="dt-highlight-num hero-num">2,979</span>
            <span className="dt-highlight-arrow">→</span>
            <span className="dt-highlight-num hero-num">2,009</span>
            <span className="dt-highlight-label">記錄物種數（−970 種）</span>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 4: 解讀邊界 ──
  if (step === 4) {
    return (
      <div className="dt-stage">
        <div className="dt-s4">
          <span className="dt-section-label">數據解讀邊界</span>
          <div className="dt-boundary-cards">
            <div className="dt-boundary-card dt-boundary-caution">
              <span className="dt-boundary-icon">⚠</span>
              <p className="dt-boundary-text">兩年觀測焦點不同<br />2026 年更集中於動物類群</p>
            </div>
            <div className="dt-boundary-card dt-boundary-caution">
              <span className="dt-boundary-icon">⚠</span>
              <p className="dt-boundary-text">記錄數下降 −45.2%<br />不等於生物多樣性整體下降</p>
            </div>
            <div className="dt-boundary-card dt-boundary-ok">
              <span className="dt-boundary-icon">✓</span>
              <p className="dt-boundary-text">動物類群信號更清晰<br />昆蟲 · 鳥類 · 兩棲類趨勢可信</p>
            </div>
          </div>
          <p className="dt-boundary-quote">
            這份數據最可靠的，是昼夜節律的差異——<br />
            兩年觀測口徑一致，時間分佈不受類群取樣偏差影響。
          </p>
        </div>
      </div>
    );
  }

  return null;
}
