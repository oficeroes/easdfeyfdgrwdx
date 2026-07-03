import "./DeepData.css";

interface Props {
  step: number;
}

export default function DeepData({ step }: Props) {
  // ── Step 0: 多樣性指數表 + 物種數 ──
  if (step === 0) {
    const indices = [
      { name: "Shannon H′",  y25: "6.7060", y26: "6.4099", delta: "−0.2961", dir: "down", note: "多樣性略降" },
      { name: "Pielou J′",   y25: "0.8383", y26: "0.8428", delta: "+0.0045", dir: "up",   note: "均勻度微升" },
      { name: "Simpson 1−D", y25: "0.9974", y26: "0.9958", delta: "−0.0016", dir: "down", note: "維持高水平" },
    ];
    return (
      <div className="dd-stage">
        <div className="dd-s0">
          <span className="dd-section-label">多樣性指數對比</span>
          <div className="dd-index-table">
            <div className="dd-index-header">
              <span>指數</span>
              <span>2025</span>
              <span>2026</span>
              <span>變化</span>
              <span>解讀</span>
            </div>
            {indices.map((idx) => (
              <div key={idx.name} className="dd-index-row">
                <span className="dd-idx-name">{idx.name}</span>
                <span className="dd-idx-val">{idx.y25}</span>
                <span className="dd-idx-val">{idx.y26}</span>
                <span className={`dd-idx-delta ${idx.dir}`}>{idx.delta}</span>
                <span className="dd-idx-note">{idx.note}</span>
              </div>
            ))}
          </div>
          <div className="dd-species-row">
            <div className="dd-species-block">
              <span className="dd-species-year">2025</span>
              <span className="dd-species-num hero-num">2,979</span>
              <span className="dd-species-unit">種</span>
            </div>
            <div className="dd-species-arrow">→</div>
            <div className="dd-species-block">
              <span className="dd-species-year">2026</span>
              <span className="dd-species-num hero-num">2,009</span>
              <span className="dd-species-unit">種</span>
            </div>
            <div className="dd-species-delta">−970 種</div>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 1: Jaccard 韋恩圖 ──
  if (step === 1) {
    return (
      <div className="dd-stage">
        <div className="dd-s1">
          <span className="dd-section-label">物種年際更替 · Jaccard 相似度</span>
          <div className="dd-jaccard-hero">
            <span className="dd-jaccard-pct hero-num">39%</span>
            <span className="dd-jaccard-label">兩年物種組成相似度</span>
          </div>
          <div className="dd-venn-wrap">
            <svg viewBox="0 0 680 320" className="dd-venn-svg" aria-hidden="true">
              {/* 2025 circle */}
              <ellipse cx="240" cy="160" rx="210" ry="140" className="dd-venn-left" />
              {/* 2026 circle */}
              <ellipse cx="440" cy="160" rx="210" ry="140" className="dd-venn-right" />
              {/* Labels: 2025-only */}
              <text x="120" y="148" className="dd-venn-count">1,580</text>
              <text x="120" y="172" className="dd-venn-sublabel">2025 獨有</text>
              {/* Labels: shared */}
              <text x="340" y="148" className="dd-venn-count dd-venn-count-shared">1,399</text>
              <text x="340" y="172" className="dd-venn-sublabel dd-venn-sublabel-shared">共有</text>
              {/* Labels: 2026-only */}
              <text x="558" y="148" className="dd-venn-count">610</text>
              <text x="558" y="172" className="dd-venn-sublabel">2026 獨有</text>
              {/* Year tags */}
              <text x="130" y="48" className="dd-venn-year">2025</text>
              <text x="540" y="48" className="dd-venn-year">2026</text>
            </svg>
          </div>
          <p className="dd-venn-note">近六成物種在兩年之間發生了更替</p>
        </div>
      </div>
    );
  }

  // ── Step 2: 物種集中度 ──
  if (step === 2) {
    const bars = [
      { label: "第 1 名", pct: 2.64,  highlight: true },
      { label: "第 2 名", pct: 2.41,  highlight: false },
      { label: "第 3 名", pct: 2.28,  highlight: false },
      { label: "第 4 名", pct: 2.18,  highlight: false },
      { label: "第 5 名", pct: 2.10,  highlight: false },
      { label: "第 6 名", pct: 2.05,  highlight: false },
      { label: "第 7 名", pct: 2.01,  highlight: false },
      { label: "第 8 名", pct: 1.98,  highlight: false },
      { label: "第 9 名", pct: 1.90,  highlight: false },
      { label: "第 10 名", pct: 1.83, highlight: false },
    ];
    const maxPct = 5; // axis max
    return (
      <div className="dd-stage">
        <div className="dd-s2">
          <span className="dd-section-label">物種記錄集中度 · 無霸主物種</span>
          <div className="dd-conc-hero-row">
            <div className="dd-conc-stat">
              <span className="dd-conc-num hero-num">21.8%</span>
              <span className="dd-conc-desc">前十名物種合計佔比</span>
            </div>
            <div className="dd-conc-divider" />
            <div className="dd-conc-stat">
              <span className="dd-conc-num hero-num">2.64%</span>
              <span className="dd-conc-desc">第一名物種最高佔比</span>
            </div>
          </div>
          <div className="dd-conc-chart">
            {bars.map((b) => (
              <div key={b.label} className="dd-conc-bar-row">
                <span className="dd-conc-bar-label">{b.label}</span>
                <div className="dd-conc-bar-track">
                  <div
                    className={`dd-conc-bar ${b.highlight ? "dd-conc-bar-hi" : ""}`}
                    style={{ width: `${(b.pct / maxPct) * 100}%` }}
                  />
                  <span className="dd-conc-bar-val">{b.pct}%</span>
                </div>
              </div>
            ))}
          </div>
          <p className="dd-conc-note">沒有霸主物種——澳門生態社群是一個高度分散的系統</p>
        </div>
      </div>
    );
  }

  // ── Step 3: 稀有物種結構 ──
  if (step === 3) {
    const taxa = [
      { name: "真菌 Fungi",      rate: 92.1 },
      { name: "蛛形綱 Arachnida", rate: 87.9 },
      { name: "魚類 Pisces",     rate: 86.8 },
    ];
    return (
      <div className="dd-stage">
        <div className="dd-s3">
          <span className="dd-section-label">稀有物種結構 · 2026 年數據</span>
          <div className="dd-rare-hero">
            <div className="dd-rare-stat dd-rare-stat-primary">
              <span className="dd-rare-num hero-num">720</span>
              <span className="dd-rare-unit">個 Singleton 物種</span>
              <span className="dd-rare-sub">僅有一條記錄</span>
              <div className="dd-rare-pct-badge">35.8%</div>
            </div>
            <div className="dd-rare-stat dd-rare-stat-secondary">
              <span className="dd-rare-num hero-num">1,426</span>
              <span className="dd-rare-unit">個 ≤5 條記錄物種</span>
              <div className="dd-rare-pct-badge dd-rare-pct-secondary">71%</div>
            </div>
          </div>
          <div className="dd-rare-taxa">
            <span className="dd-rare-taxa-title">各類群 Singleton 率</span>
            {taxa.map((t) => (
              <div key={t.name} className="dd-rare-taxa-row">
                <span className="dd-rare-taxa-name">{t.name}</span>
                <div className="dd-rare-taxa-bar-track">
                  <div className="dd-rare-taxa-bar" style={{ width: `${t.rate}%` }} />
                </div>
                <span className="dd-rare-taxa-val">{t.rate}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ── Step 4: 關鍵 Singleton 物種卡片 ──
  if (step === 4) {
    const species = [
      {
        cn: "黑臉琵鷺",
        la: "Platalea minor",
        iucn: "易危 VU",
        iucnClass: "vu",
        note: "全球受威脅水鳥",
        records: 1,
      },
      {
        cn: "黃胸鹀",
        la: "Emberiza aureola",
        iucn: "極危 CR",
        iucnClass: "cr",
        note: "種群急劇崩潰",
        records: 1,
      },
      {
        cn: "台北蛙",
        la: "Rana taipehensis",
        iucn: "近危 NT",
        iucnClass: "nt",
        note: "兩棲類唯一 singleton",
        records: 1,
      },
      {
        cn: "綠鷺",
        la: "Butorides striata",
        iucn: "無危 LC",
        iucnClass: "lc",
        note: "濕地敏感指示物種",
        records: 1,
      },
    ];
    return (
      <div className="dd-stage">
        <div className="dd-s4">
          <span className="dd-section-label">關鍵 Singleton 物種 · 各僅一條記錄</span>
          <div className="dd-sp-grid">
            {species.map((sp, i) => (
              <div
                key={sp.cn}
                className="dd-sp-card"
                style={{ animationDelay: `${i * 0.12}s` }}
              >
                <div className="dd-sp-header">
                  <span className="dd-sp-cn">{sp.cn}</span>
                  <span className={`dd-sp-iucn dd-iucn-${sp.iucnClass}`}>{sp.iucn}</span>
                </div>
                <span className="dd-sp-la">{sp.la}</span>
                <span className="dd-sp-note">{sp.note}</span>
                <div className="dd-sp-records">
                  <span className="dd-sp-records-num hero-num">1</span>
                  <span className="dd-sp-records-label">條記錄</span>
                </div>
              </div>
            ))}
          </div>
          <p className="dd-sp-quote">
            不再被看見，往往意味著——它們是第一批消失的
          </p>
        </div>
      </div>
    );
  }

  return null;
}
