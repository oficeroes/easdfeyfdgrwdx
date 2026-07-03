import "./DayClock.css";

interface Props {
  step: number;
}

const HOURS = Array.from({ length: 24 }, (_, i) => i);

function ClockBg({ highlightHour, color }: { highlightHour?: number; color?: string }) {
  const R = 130; const cx = 150; const cy = 150;
  const toRad = (h: number) => (h / 12) * Math.PI - Math.PI / 2;
  return (
    <svg className="dc-mini-clock" viewBox="0 0 300 300" fill="none">
      {/* 白天左半圓底色 */}
      <path d={`M ${cx} ${cy} L ${cx} ${cy - R} A ${R} ${R} 0 0 0 ${cx} ${cy + R} Z`}
        fill="var(--text)" opacity="0.06" />
      {/* 夜晚右半圓底色 */}
      <path d={`M ${cx} ${cy} L ${cx} ${cy - R} A ${R} ${R} 0 0 1 ${cx} ${cy + R} Z`}
        fill="var(--accent)" opacity="0.1" />
      <circle cx={cx} cy={cy} r={R} stroke="var(--rule)" strokeWidth="1.5" />
      {/* 高亮時段扇形 */}
      {highlightHour !== undefined && (() => {
        const a1 = toRad(highlightHour);
        const a2 = toRad(highlightHour + 1);
        const x1 = cx + R * Math.cos(a1); const y1 = cy + R * Math.sin(a1);
        const x2 = cx + R * Math.cos(a2); const y2 = cy + R * Math.sin(a2);
        return (
          <path d={`M ${cx} ${cy} L ${x1} ${y1} A ${R} ${R} 0 0 1 ${x2} ${y2} Z`}
            fill={color || "var(--accent)"} opacity="0.7"
            style={{ animation: "dc-sector-in 0.5s ease both" }} />
        );
      })()}
      {/* 刻度與時間標注 */}
      {[0,3,6,9,12,15,18,21].map(h => {
        const a = toRad(h);
        return (
          <g key={h}>
            <line x1={cx + (R-12)*Math.cos(a)} y1={cy + (R-12)*Math.sin(a)}
              x2={cx + R*Math.cos(a)} y2={cy + R*Math.sin(a)}
              stroke="var(--text-mute)" strokeWidth={h%6===0?2.5:1} />
            <text x={cx+(R+18)*Math.cos(a)} y={cy+(R+18)*Math.sin(a)}
              textAnchor="middle" dominantBaseline="middle"
              fill="var(--text-mute)" style={{ fontSize: 11, fontFamily: "var(--font-mono)" }}>
              {String(h).padStart(2,"0")}
            </text>
          </g>
        );
      })}
      <circle cx={cx} cy={cy} r={4} fill="var(--text)" opacity="0.5" />
    </svg>
  );
}

export default function DayClock({ step }: Props) {
  // ── Step 0: 06:00 晨鳥 ──
  if (step === 0) {
    const birds = [
      { name: "珠頸斑鳩", count: 484, pct: "16.1%" },
      { name: "麻雀",     count: 435, pct: "14.5%" },
      { name: "紅耳鵯",   count: 246, pct: "8.2%"  },
      { name: "鵲鴝",     count: 236, pct: "7.9%"  },
    ];
    return (
      <div className="dc-stage">
        <div className="dc-s0">
          <div className="dc-left">
            <ClockBg highlightHour={6} color="var(--text)" />
            <span className="dc-time-label">06:00</span>
            <span className="dc-time-sub">128 條晨間記錄</span>
          </div>
          <div className="dc-right">
            <span className="dc-section-label">白天的時鐘 · 晨間</span>
            <h2 className="dc-title">鳥類最先出現</h2>
            <div className="dc-bird-list">
              {birds.map((b, i) => (
                <div key={i} className="dc-bird-row" style={{ animationDelay: `${i*0.08}s` }}>
                  <span className="dc-bird-name">{b.name}</span>
                  <div className="dc-bird-bar-wrap">
                    <div className="dc-bird-bar" style={{ width: `${(b.count/484)*100}%` }} />
                  </div>
                  <span className="dc-bird-count">{b.count}</span>
                  <span className="dc-bird-pct">{b.pct}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 1: 10:00 鳥類高峰 ──
  if (step === 1) {
    const birds = [
      { name: "珠頸斑鳩", count: 484 },
      { name: "麻雀",     count: 435 },
      { name: "紅耳鵯",   count: 246 },
      { name: "鵲鴝",     count: 236 },
      { name: "白頭鵯",   count: 198 },
      { name: "八哥",     count: 162 },
    ];
    const max = 484;
    return (
      <div className="dc-stage">
        <div className="dc-s1">
          <div className="dc-left">
            <ClockBg highlightHour={10} color="var(--text)" />
            <span className="dc-time-label">10:00</span>
            <div className="dc-peak-badge">
              <span className="dc-peak-num hero-num">378</span>
              <span className="dc-peak-unit">條／小時</span>
            </div>
          </div>
          <div className="dc-right">
            <span className="dc-section-label">鳥類高峰時段</span>
            <h2 className="dc-title">城市鳥類優勢種</h2>
            <div className="dc-bird-list">
              {birds.map((b, i) => (
                <div key={i} className="dc-bird-row" style={{ animationDelay: `${i*0.07}s` }}>
                  <span className="dc-bird-name">{b.name}</span>
                  <div className="dc-bird-bar-wrap">
                    <div className="dc-bird-bar" style={{ width: `${(b.count/max)*100}%` }} />
                  </div>
                  <span className="dc-bird-count">{b.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 2: 鳥類四時段對比 ──
  if (step === 2) {
    const periods = [
      { label: "白天", time: "09:00–16:59", count: 2215, pct: 75.3, color: "var(--text)", opacity: 0.75 },
      { label: "黃昏", time: "17:00–18:59", count: 510,  pct: 17.3, color: "var(--accent)", opacity: 0.6 },
      { label: "晨間", time: "07:00–08:59", count: 128,  pct: 4.3,  color: "var(--text-2)", opacity: 0.7 },
      { label: "夜間", time: "19:00–06:59", count: 90,   pct: 3.1,  color: "var(--text-mute)", opacity: 0.5 },
    ];
    return (
      <div className="dc-stage">
        <div className="dc-s2">
          <span className="dc-section-label">鳥類四時段分佈（2026 年 2,943 條有時間記錄）</span>
          <div className="dc-period-bars">
            {periods.map((p, i) => (
              <div key={i} className="dc-period-col" style={{ animationDelay: `${i*0.1}s` }}>
                <span className="dc-period-pct" style={{ color: p.color }}>{p.pct}%</span>
                <div className="dc-period-bar-wrap">
                  <div className="dc-period-bar"
                    style={{ height: `${p.pct * 2.8}px`, background: p.color, opacity: p.opacity }} />
                </div>
                <span className="dc-period-count">{p.count}</span>
                <span className="dc-period-label">{p.label}</span>
                <span className="dc-period-time">{p.time}</span>
              </div>
            ))}
          </div>
          <div className="dc-night-note">
            夜間比例 <strong>3.1%</strong> — 鳥類是白天和黃昏的生命
          </div>
        </div>
      </div>
    );
  }

  // ── Step 3: 15:00 昆蟲登場 ──
  if (step === 3) {
    return (
      <div className="dc-stage">
        <div className="dc-s3">
          <div className="dc-left">
            <ClockBg highlightHour={15} color="var(--accent)" />
            <span className="dc-time-label dc-time-accent">15:00</span>
            <div className="dc-peak-badge">
              <span className="dc-peak-num hero-num" style={{ color: "var(--accent)" }}>487</span>
              <span className="dc-peak-unit">條／小時</span>
            </div>
          </div>
          <div className="dc-right">
            <span className="dc-section-label">昆蟲高峰時段</span>
            <h2 className="dc-title">昆蟲年際增量</h2>
            <div className="dc-insect-compare">
              <div className="dc-insect-year">
                <span className="dc-insect-yr">2025</span>
                <span className="dc-insect-num">2,929 條</span>
                <span className="dc-insect-sp">475 物種</span>
              </div>
              <div className="dc-insect-arrow">→</div>
              <div className="dc-insect-year dc-insect-year-26">
                <span className="dc-insect-yr">2026</span>
                <span className="dc-insect-num">3,673 條</span>
                <span className="dc-insect-sp">574 物種</span>
              </div>
            </div>
            <div className="dc-insect-delta">
              <span>記錄 <strong>+744 條</strong>（+25.4%）</span>
              <span>物種 <strong>+99 種</strong>（+20.8%）</span>
            </div>
            <p className="dc-insect-note">夜間仍有 676 條（18.7%）——昆蟲沒有完全停下來</p>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 4: 黃昏交接 ──
  if (step === 4) {
    return (
      <div className="dc-stage">
        <div className="dc-s4">
          <div className="dc-left">
            <ClockBg highlightHour={18} color="var(--accent)" />
            <span className="dc-time-label dc-time-accent">18:00</span>
            <span className="dc-time-sub" style={{ color: "var(--accent)" }}>黃昏交接</span>
          </div>
          <div className="dc-right">
            <span className="dc-section-label">白天最後的高峰</span>
            <div className="dc-dusk-stat">
              <span className="dc-dusk-num hero-num">510</span>
              <span className="dc-dusk-unit">條黃昏鳥類記錄</span>
            </div>
            <div className="dc-dusk-wetland">
              <span className="dc-dusk-wt-label">濕地水鳥（另一條生態線）</span>
              <div className="dc-dusk-wt-row">
                <span className="dc-wt-sp">小白鷺</span><span className="dc-wt-n">162 條</span>
              </div>
              <div className="dc-dusk-wt-row">
                <span className="dc-wt-sp">黑水雞</span><span className="dc-wt-n">135 條</span>
              </div>
              <div className="dc-dusk-wt-row">
                <span className="dc-wt-sp">池鷺</span><span className="dc-wt-n">39 條</span>
              </div>
            </div>
            <p className="dc-dusk-note">黃昏過後，白天的主角退場——<br />夜班生命開始等待。</p>
          </div>
        </div>
      </div>
    );
  }

  // ── Step 5: 白天小結 ──
  if (step === 5) {
    const summary = [
      { time: "06:00", label: "晨鳥",   key: "128 條", cls: "dc-sum-day" },
      { time: "10:00", label: "鳥類峰", key: "378 條/h", cls: "dc-sum-day" },
      { time: "15:00", label: "昆蟲峰", key: "487 條/h", cls: "dc-sum-peak" },
      { time: "18:00", label: "黃昏交接", key: "510 條", cls: "dc-sum-dusk" },
    ];
    return (
      <div className="dc-stage">
        <div className="dc-s5">
          <span className="dc-section-label">白天時鐘 · 節律總覽</span>
          <div className="dc-timeline">
            {summary.map((s, i) => (
              <div key={i} className={`dc-tl-item ${s.cls}`} style={{ animationDelay: `${i*0.1}s` }}>
                <span className="dc-tl-time">{s.time}</span>
                <div className="dc-tl-dot" />
                <span className="dc-tl-label">{s.label}</span>
                <span className="dc-tl-key">{s.key}</span>
              </div>
            ))}
            <div className="dc-tl-line" />
          </div>
          <p className="dc-summary-quote">
            白天很熱鬧，屬於鳥和蟲。<br />節律清晰，記錄密集，高峰精準。<br />這是城市可見的部分。
          </p>
        </div>
      </div>
    );
  }

  return null;
}
