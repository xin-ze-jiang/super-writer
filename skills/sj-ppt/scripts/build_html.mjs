#!/usr/bin/env node
// sj-ppt HTML 生成器：deck.json -> 单文件 HTML 演示版
// 风格决策：meta.style（强制） > minimal-art 门槛 > 关键词 > 特征打分
import fs from "node:fs";
import path from "node:path";

const [, , inPath, outPath] = process.argv;
if (!inPath || !outPath) {
  console.error("用法: node build_html.mjs deck.json out/index.html");
  process.exit(1);
}

const deck = JSON.parse(fs.readFileSync(inPath, "utf8"));
const deckDir = path.dirname(path.resolve(inPath));

/* ---------- 共用 8pt 网格与字号阶梯（风格只覆盖变量） ---------- */
const BASE = {
  radius: "10px",
  shadow: "0 2px 12px rgba(26,26,24,.05)",
  serif: '"Source Serif Pro","Source Han Serif SC","Noto Serif CJK SC","Songti SC",Georgia,serif',
  sans: '"Inter","Source Han Sans SC","Noto Sans CJK SC","Microsoft YaHei","PingFang SC",system-ui,sans-serif',
  fsHero: "60px", fsTitle: "34px", fsH3: "20px", fsBody: "14px",
  fsSmall: "12px", fsMicro: "10px", fsKicker: "13px", fsKpi: "40px",
  padX: "96px", padY: "48px", lead: "1.7", tracking: "-0.01em",
  motion: "0.6s", stagger: "90ms"
};

const STYLES = {
  // 旧主题，保持兼容
  "claude-warm": { ...BASE, bg: "#FAF9F5", surface: "#FFFFFF", surfaceAlt: "#F3F1EA",
    ink: "#1A1A18", muted: "#6B6862", accent: "#D97757", line: "#E5E2DA", onAccent: "#FFFFFF" },
  "tech-dark": { ...BASE, bg: "#111315", surface: "#181B1E", surfaceAlt: "#1E2226",
    ink: "#F2F3F2", muted: "#8A9095", accent: "#3FBDB2", line: "#262A2E", onAccent: "#08110F" },

  keynote: { ...BASE, bg: "#0B0B0C", surface: "#131316", surfaceAlt: "#1D1D20",
    ink: "#F5F5F7", muted: "#86868B", accent: "#2997FF", line: "#232327", onAccent: "#FFFFFF",
    radius: "20px", shadow: "none", serif: '"SF Pro Display","Inter","PingFang SC",system-ui,sans-serif',
    fsHero: "104px", fsTitle: "46px", fsH3: "24px", fsBody: "16px", fsSmall: "13px",
    fsMicro: "11px", fsKicker: "12px", fsKpi: "64px", padX: "110px", padY: "60px",
    lead: "1.5", tracking: "-0.03em", motion: "1.1s", stagger: "120ms" },

  academic: { ...BASE, bg: "#FFFFFF", surface: "#FFFFFF", surfaceAlt: "#F4F6F8",
    ink: "#1B3A5C", muted: "#5D6B7A", accent: "#1B3A5C", line: "#D9DFE6", onAccent: "#FFFFFF",
    radius: "2px", shadow: "none",
    fsHero: "46px", fsTitle: "28px", fsH3: "18px", fsBody: "13px", fsSmall: "11px",
    fsMicro: "9.5px", fsKicker: "11px", fsKpi: "32px", padX: "88px", padY: "44px",
    lead: "1.65", tracking: "-0.01em", motion: "0.6s", stagger: "80ms" },

  consulting: { ...BASE, bg: "#F7F7F5", surface: "#FFFFFF", surfaceAlt: "#EFEFEC",
    ink: "#16181D", muted: "#6A6E73", accent: "#B0432F", line: "#DCDBD5", onAccent: "#FFFFFF",
    radius: "0", shadow: "none",
    fsHero: "44px", fsTitle: "24px", fsH3: "16px", fsBody: "12px", fsSmall: "10.5px",
    fsMicro: "9px", fsKicker: "10px", fsKpi: "30px", padX: "64px", padY: "40px",
    lead: "1.55", tracking: "-0.01em", motion: "0.55s", stagger: "80ms" },

  contest: { ...BASE, bg: "#FFFFFF", surface: "#FFFFFF", surfaceAlt: "#F3F2EE",
    ink: "#111114", muted: "#6B6E75", accent: "#FF3D00", line: "#E7E5DF", onAccent: "#FFFFFF",
    radius: "0", shadow: "none",
    fsHero: "88px", fsTitle: "42px", fsH3: "24px", fsBody: "15px", fsSmall: "12px",
    fsMicro: "10px", fsKicker: "12px", fsKpi: "76px", padX: "104px", padY: "56px",
    lead: "1.6", tracking: "-0.03em", motion: "0.85s", stagger: "110ms" },

  "minimal-art": { ...BASE, bg: "#F2EFE9", surface: "#F2EFE9", surfaceAlt: "#E8E3D9",
    ink: "#1E1C18", muted: "#7A736A", accent: "#A65C3B", line: "#D8D1C4", onAccent: "#F7F4EE",
    radius: "0", shadow: "none",
    serif: '"Instrument Serif","Source Han Serif SC","Songti SC",Georgia,serif',
    fsHero: "64px", fsTitle: "34px", fsH3: "22px", fsBody: "13px", fsSmall: "11px",
    fsMicro: "9px", fsKicker: "10px", fsKpi: "40px", padX: "96px", padY: "56px",
    lead: "1.75", tracking: "-0.02em", motion: "0.78s", stagger: "100ms" }
};

const LABEL = { keynote: "苹果发布会", academic: "学术答辩", consulting: "咨询研报",
  contest: "国赛获奖", "minimal-art": "极简美术", "claude-warm": "暖白", "tech-dark": "科技深色" };

const VAR_NAME = {
  surfaceAlt: "surface-alt", onAccent: "on-accent", fsHero: "fs-hero", fsTitle: "fs-title",
  fsH3: "fs-h3", fsBody: "fs-body", fsSmall: "fs-small", fsMicro: "fs-micro",
  fsKicker: "fs-kicker", fsKpi: "fs-kpi", padX: "pad-x", padY: "pad-y"
};
const VAR_KEYS = Object.keys(BASE).concat(["bg", "surface", "ink", "muted", "accent", "line"]);
function cssVars(t) {
  return VAR_KEYS.map((k) => `--${VAR_NAME[k] || k}:${t[k]}`).join(";");
}

/* ---------- 内容特征 ---------- */
function textLen(p) {
  const bits = [p.title, p.subtitle, p.kicker, p.caption, p.note, p.label, p.text]
    .concat((p.items || []).map((x) => (x.title || "") + (x.text || "")))
    .concat((p.cards || []).map((x) => (x.name || "") + (x.code || "") + (x.desc || "")))
    .concat((p.parts || []).map((x) => x.label || ""));
  return bits.filter(Boolean).join("").length;
}

function analyze(deck) {
  const pages = deck.slides || [];
  const n = pages.length;
  const chartPages = pages.filter((p) => p.chart && Array.isArray(p.chart.values) && p.chart.values.length).length;
  const chartRatio = n ? chartPages / n : 0;
  const avg = n ? pages.reduce((a, p) => a + textLen(p), 0) / n : 0;
  const density = avg < 120 ? "低" : avg < 240 ? "中" : "高";
  const hasConclusion = pages.some((p, i) => (p.title || "").includes("结论") || (p.title || "").includes("总结")
    || (i === n - 1 && p.type === "end"));
  return { pageCount: n, chartRatio, density, hasConclusion, avg };
}

const KEYWORD_RULES = [
  { name: "academic", words: ["答辩", "结题", "实验", "论文", "课程", "汇报", "大创"] },
  { name: "contest", words: ["路演", "创业", "挑战杯", "互联网+", "竞赛", "大赛", "比赛"] },
  { name: "keynote", words: ["发布", "新品", "产品", "创意", "demo", "Demo", "展示", "亮相"] },
  { name: "consulting", words: ["数据分析", "调研", "复盘", "评估", "报告", "研究"] }
];

function pickStyle(deck) {
  const m = deck.meta || {};
  const pages = deck.slides || [];
  const info = analyze(deck);
  const pageCount = Number(m.pageCount) || info.pageCount;
  const chartRatio = typeof m.chartRatio === "number" ? m.chartRatio : info.chartRatio;
  const density = m.textDensity || info.density;
  const purpose = m.purpose || "";
  const ratioTxt = chartRatio.toFixed(2);

  // 1. 强制指定
  const forced = (typeof m.style === "string" && STYLES[m.style] && m.style)
    || (typeof deck.style === "string" && STYLES[deck.style] && deck.style);
  if (forced) return { name: forced, reason: `meta.style=${forced} 已强制指定 → ${forced}（${LABEL[forced]}）` };
  if (typeof deck.theme === "string" && STYLES[deck.theme])
    return { name: deck.theme, reason: `旧字段 theme=${deck.theme} 直接采用` };
  if (deck.theme && typeof deck.theme === "object")
    return { name: "claude-warm", reason: "theme 为颜色覆盖对象，沿用 claude-warm 结构" };

  // 2. minimal-art 门槛（作品集/展示/汇报 + 低密度 + 页数少）
  const isShowcase = /作品集|展示|汇报/.test(purpose);
  if (isShowcase && density === "低" && pageCount <= 12)
    return { name: "minimal-art", reason: `purpose=${purpose}（命中「作品集/展示/汇报」）、文本密度 ${density}、${pageCount} 页 ≤ 12 → minimal-art（极简美术）` };

  // 3. 关键词
  const hay = [purpose, deck.title || "", ...pages.map((p) => p.title || ""), ...pages.map((p) => p.kicker || "")].join(" ");
  let best = null;
  for (const rule of KEYWORD_RULES) {
    for (const w of rule.words) {
      if (hay.includes(w)) { best = { name: rule.name, word: w }; break; }
    }
    if (best) break;
  }
  if (best)
    return { name: best.name, reason: `检测到 purpose=${purpose || "（未填）"}（关键词命中「${best.word}」）、图表占比 ${ratioTxt} → ${best.name}（${LABEL[best.name]}）` };

  // 4. 特征打分
  if (chartRatio > 0.4 && density === "高")
    return { name: "consulting", reason: `特征打分：图表占比 ${ratioTxt} > 0.4 且文本密度 ${density} → consulting（咨询研报）` };
  if (pageCount <= 10 && density === "低" && chartRatio >= 0.3)
    return { name: "keynote", reason: `特征打分：${pageCount} 页 ≤ 10、文本密度 ${density}、图表占比 ${ratioTxt} → keynote（苹果发布会）` };
  if (pageCount >= 15 && info.hasConclusion)
    return { name: "academic", reason: `特征打分：${pageCount} 页 ≥ 15 且有结论页 → academic（学术答辩）` };
  return { name: "contest", reason: `特征打分：图表占比 ${ratioTxt}、文本密度 ${density}、${pageCount} 页 → 默认 contest（国赛获奖）` };
}

const decision = pickStyle(deck);
const globalName = decision.name;
const globalTokens = STYLES[globalName];

function slideStyle(s) {
  return (typeof s.styleOverride === "string" && STYLES[s.styleOverride]) ? s.styleOverride : globalName;
}

/* ---------- 图片内联 ---------- */
const assetCache = new Map();
function inlineAsset(ref) {
  if (!ref) return "";
  const p = path.isAbsolute(ref) ? ref : path.resolve(deckDir, ref);
  if (assetCache.has(p)) return assetCache.get(p);
  let url = "";
  if (fs.existsSync(p)) {
    const ext = path.extname(p).toLowerCase();
    const mime = ext === ".png" ? "image/png" : ext === ".jpg" || ext === ".jpeg" ? "image/jpeg"
      : ext === ".webp" ? "image/webp" : "application/octet-stream";
    url = `data:${mime};base64,${fs.readFileSync(p).toString("base64")}`;
  } else {
    console.warn(`[sj-ppt] 找不到图片: ${p}`);
  }
  assetCache.set(p, url);
  return url;
}

const esc = (s = "") =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const slideCount = deck.slides.length;
const footLabel = esc(deck.footer || (deck.meta && deck.meta.audience) || "");

/* ---------- 页面 ---------- */
function slideCover(s, i) {
  const art = inlineAsset(s.art);
  if (art) {
    return `
  <section class="slide cover art-cover" data-idx="${i}" data-foot="${footLabel}">
    <img class="cover-art${s.artFit === "contain" ? " art-contain" : ""}" src="${art}" alt="${esc(s.title || "")}">
    <div class="page-no">${String(i + 1).padStart(2, "0")}</div>
  </section>`;
  }
  return `
  <section class="slide cover" data-idx="${i}" data-foot="${footLabel}">
    <div class="cover-inner">
      <p class="kicker a" style="--d:0">${esc(s.kicker || "")}</p>
      <h1 class="a" style="--d:1">${esc(s.title)}</h1>
      <div class="rule a" style="--d:2"></div>
      <p class="sub a" style="--d:3">${esc(s.subtitle || "")}</p>
    </div>
    <div class="cover-foot a" style="--d:4">
      ${(s.tags || []).map((x) => `<span class="tag">${esc(x)}</span>`).join("")}
      <span class="meta">${esc(s.presenter || deck.presenter || "")} ${esc(s.date || deck.date || "")}</span>
    </div>
    <div class="page-no">${String(i + 1).padStart(2, "0")}</div>
  </section>`;
}

function slideStatement(s, i) {
  const art = inlineAsset(s.art);
  if (art) {
    return `
  <section class="slide statement art-cover" data-idx="${i}" data-foot="${footLabel}">
    <img class="cover-art${s.artFit === "contain" ? " art-contain" : ""}" src="${art}" alt="${esc(s.title || "")}">
    <div class="page-no">${String(i + 1).padStart(2, "0")}</div>
  </section>`;
  }
  return `
  <section class="slide statement" data-idx="${i}" data-foot="${footLabel}">
    <div class="stmt-inner">
      ${s.kicker ? `<p class="kicker a" style="--d:0">${esc(s.kicker)}</p>` : ""}
      <h2 class="stmt-title a" style="--d:1">${esc(s.title).replace(/\n/g, "<br>")}</h2>
      ${s.subtitle ? `<p class="stmt-sub a" style="--d:2">${esc(s.subtitle)}</p>` : ""}
    </div>
    <div class="page-no">${String(i + 1).padStart(2, "0")}</div>
  </section>`;
}

function slideData(s, i) {
  const stats = (s.stats || []).slice(0, 3);
  const chart = s.chart;
  const max = chart ? Math.max(...chart.values.map(Number), 1) : 1;
  const bars = chart
    ? chart.values
        .map(
          (v, k) => `
      <div class="bar-col" style="--d:${k + 2}">
        <span class="bar-val">${esc(v)}${esc(chart.unit || "")}</span>
        <div class="bar" style="--h:${(Number(v) / max) * 100}%"></div>
        <span class="bar-lab">${esc(chart.labels[k] || "")}</span>
      </div>`
        )
        .join("")
    : "";
  return `
  <section class="slide data" data-idx="${i}" data-foot="${footLabel}">
    <header class="slide-head">
      <h2 class="a" style="--d:0">${esc(s.title)}</h2>
      <div class="rule short a" style="--d:1"></div>
    </header>
    <div class="data-body">
      <div class="kpis">
        ${stats
          .map(
            (x, k) => `
        <div class="kpi a" style="--d:${k + 1}">
          <span class="kpi-num"><span class="num" data-to="${esc(x.value)}">0</span><em>${esc(x.unit || "")}</em></span>
          <span class="kpi-lab">${esc(x.label)}</span>
        </div>`
          )
          .join("")}
      </div>
      <div class="chart">
        <div class="bars">${bars}</div>
        ${chart && chart.caption ? `<p class="chart-cap a" style="--d:3">${esc(chart.caption)}</p>` : ""}
      </div>
    </div>
    ${s.note ? `<footer class="note a" style="--d:5">${esc(s.note)}</footer>` : ""}
    <div class="page-no">${String(i + 1).padStart(2, "0")}</div>
  </section>`;
}

function slidePoints(s, i) {
  const items = (s.items || []).slice(0, 4);
  return `
  <section class="slide points" data-idx="${i}" data-foot="${footLabel}">
    <header class="slide-head">
      <h2 class="a" style="--d:0">${esc(s.title)}</h2>
      <div class="rule short a" style="--d:1"></div>
    </header>
    <div class="cards">
      ${items
        .map(
          (x, k) => `
      <article class="card a" style="--d:${k + 1}">
        <span class="idx">${String(k + 1).padStart(2, "0")}</span>
        <h3>${esc(x.title || "")}</h3>
        <p>${esc(x.text || "")}</p>
      </article>`
        )
        .join("")}
    </div>
    <div class="page-no">${String(i + 1).padStart(2, "0")}</div>
  </section>`;
}

/* ---------- 爆炸视图 ---------- */
const PART_SPEC = {
  endcap: { w: 70, h: 190, svg: `<rect x="-35" y="-95" width="70" height="190" rx="10" class="p-fill p-stroke"/><rect x="-18" y="-58" width="36" height="116" rx="6" class="p-hollow"/>` },
  flange: { w: 96, h: 210, svg: `<rect x="-48" y="-105" width="96" height="210" rx="8" class="p-fill p-stroke"/><circle cx="-28" cy="-74" r="7" class="p-hole"/><circle cx="28" cy="-74" r="7" class="p-hole"/><circle cx="-28" cy="74" r="7" class="p-hole"/><circle cx="28" cy="74" r="7" class="p-hole"/>` },
  gasket: { w: 14, h: 180, svg: `<rect x="-7" y="-90" width="14" height="180" rx="3" class="p-gasket"/><line x1="-7" y1="-60" x2="7" y2="-60" class="p-hatch"/><line x1="-7" y1="-20" x2="7" y2="-20" class="p-hatch"/><line x1="-7" y1="20" x2="7" y2="20" class="p-hatch"/><line x1="-7" y1="60" x2="7" y2="60" class="p-hatch"/>` },
  bolt: { w: 30, h: 160, svg: `<rect x="-8" y="-30" width="16" height="110" rx="4" class="p-bolt"/><circle cx="0" cy="-50" r="15" class="p-bolt"/><rect x="-22" y="-70" width="44" height="20" rx="4" class="p-bolt"/>` }
};

function slideExploded(s, i) {
  const parts = (s.parts || []).slice(0, 6);
  const n = parts.length;
  const axis = s.axis === "y" ? "y" : s.axis === "d" ? "d" : "x";
  const gap = 150;
  const CY = 235;

  const widths = parts.map((p) => (PART_SPEC[p.kind] || PART_SPEC.flange).w);
  const total = widths.reduce((a, b) => a + b, 0) + 8 * (n - 1);
  let cursor = 560 - total / 2;

  const placed = parts.map((p, k) => {
    const spec = PART_SPEC[p.kind] || PART_SPEC.flange;
    const cx = cursor + spec.w / 2;
    cursor += spec.w + 8;
    const rel = k - (n - 1) / 2;
    let ex = 0, ey = 0;
    if (axis === "x") ex = rel * gap;
    if (axis === "y") ey = rel * 110;
    if (axis === "d") { ex = rel * 120; ey = -rel * 95; }
    const top = CY - spec.h / 2 + ey;
    const lx = cx + ex;
    return `
      <g class="part" style="--x:${cx}px;--y:${CY}px;--ex:${ex}px;--ey:${ey}px;--i:${k}">
        ${spec.svg}
      </g>
      <g class="callout" style="--i:${k}">
        <line x1="${lx}" y1="62" x2="${lx}" y2="${top - 12}" class="co-line"/>
        <circle cx="${lx}" cy="62" r="3" class="co-dot"/>
        <text x="${lx}" y="34" class="co-num">${String(k + 1).padStart(2, "0")}</text>
        <text x="${lx}" y="52" class="co-name">${esc(p.label || "")}</text>
      </g>`;
  });

  return `
  <section class="slide exploded" data-idx="${i}" data-type="exploded" data-foot="${footLabel}">
    <header class="slide-head tight">
      <h2 class="a" style="--d:0">${esc(s.title)}</h2>
      <div class="rule short a" style="--d:1"></div>
    </header>
    <div class="exp-wrap">
      <svg class="exp-svg" viewBox="0 0 1120 470" preserveAspectRatio="xMidYMid meet">
        <line x1="70" y1="${CY}" x2="1050" y2="${CY}" class="axis"/>
        ${placed.join("\n")}
      </svg>
    </div>
    <footer class="exp-foot a" style="--d:5">
      <p class="exp-cap">${esc(s.caption || "")}</p>
      <button class="btn exp-toggle" type="button">分解</button>
    </footer>
    <div class="page-no">${String(i + 1).padStart(2, "0")}</div>
  </section>`;
}

/* ---------- 材质页 ---------- */
const PCB_SVG = `
<svg class="tex tex-pcb" viewBox="0 0 320 200" preserveAspectRatio="none">
  <g class="pcb-a">
    <path d="M18 34 H118 V96 H252"/>
    <path d="M42 172 H98 V124 H208"/>
    <path d="M152 44 V148"/>
    <circle cx="252" cy="96" r="5"/><circle cx="208" cy="124" r="5"/><circle cx="152" cy="44" r="4"/>
  </g>
  <g class="pcb-b">
    <path d="M30 58 H142 V150 H272"/>
    <path d="M72 22 V88 H198"/>
    <circle cx="272" cy="150" r="5"/><circle cx="198" cy="88" r="5"/>
  </g>
</svg>`;

const MAT_KINDS = {
  brushed: {
    icon: `<path d="M3 8h18M3 12h18M3 16h18"/>`,
    layers: `<div class="tex tex-a t-brushed"></div><div class="tex tex-b t-mirror"></div>`,
    a: "拉丝面",
    b: "镜面"
  },
  anodized: {
    icon: `<circle cx="12" cy="12" r="8"/><path d="M12 4v16M4 12h16"/>`,
    layers: `<div class="tex tex-a t-anod"></div><div class="tex tex-b t-blast"></div>`,
    a: "哑光",
    b: "喷砂"
  },
  pcb: {
    icon: `<rect x="5" y="5" width="14" height="14"/><path d="M9 5v4M15 15v4M5 9h4M15 9h4"/>`,
    layers: PCB_SVG,
    a: "铜箔",
    b: "沉金"
  }
};

function slideMaterials(s, i) {
  const cards = (s.cards || []).slice(0, 3);
  return `
  <section class="slide materials" data-idx="${i}" data-foot="${footLabel}">
    <header class="slide-head tight">
      <h2 class="a" style="--d:0">${esc(s.title)}</h2>
      <div class="rule short a" style="--d:1"></div>
    </header>
    <div class="mats">
      ${cards
        .map((c, k) => {
          const m = MAT_KINDS[c.kind] || MAT_KINDS.brushed;
          return `
      <article class="mat-card a" style="--d:${k + 1};--i:${k}">
        <div class="mat-swatch">
          <div class="tex-wrap">${m.layers}</div>
          <div class="sheen"></div>
        </div>
        <div class="mat-info">
          <div class="mat-title">
            <span class="mat-icon"><svg viewBox="0 0 24 24">${m.icon}</svg></span>
            <span class="mat-idx">${String(k + 1).padStart(2, "0")}</span>
          </div>
          <h3>${esc(c.name || "")}</h3>
          <p class="mat-code">${esc(c.code || "")}</p>
          <p class="mat-desc">${esc(c.desc || "")}</p>
          <div class="mat-actions">
            <button class="btn mat-toggle" type="button" data-a="${esc(m.a)}" data-b="${esc(m.b)}">切换材质</button>
            <button class="btn zoom-toggle" type="button">局部放大</button>
          </div>
        </div>
      </article>`;
        })
        .join("")}
    </div>
    ${s.caption ? `<p class="mat-cap a" style="--d:4">${esc(s.caption)}</p>` : ""}
    <div class="page-no">${String(i + 1).padStart(2, "0")}</div>
  </section>`;
}

function slideEnd(s, i) {
  const art = inlineAsset(s.art);
  if (art) {
    return `
  <section class="slide end art-cover" data-idx="${i}" data-foot="${footLabel}">
    <img class="cover-art${s.artFit === "contain" ? " art-contain" : ""}" src="${art}" alt="${esc(s.title || "")}">
    <div class="page-no">${String(i + 1).padStart(2, "0")}</div>
  </section>`;
  }
  return `
  <section class="slide end" data-idx="${i}" data-foot="${footLabel}">
    <div class="end-inner">
      <div class="ring"></div>
      <div class="rule a" style="--d:0"></div>
      <h2 class="a" style="--d:1">${esc(s.title)}</h2>
      <p class="sub a" style="--d:2">${esc(s.subtitle || "")}</p>
    </div>
    <div class="page-no">${String(i + 1).padStart(2, "0")}</div>
  </section>`;
}

const builders = {
  cover: slideCover,
  statement: slideStatement,
  data: slideData,
  points: slidePoints,
  exploded: slideExploded,
  materials: slideMaterials,
  end: slideEnd
};

const slidesHtml = deck.slides
  .map((s, i) => {
    const ps = slideStyle(s);
    const html = (builders[s.type] || slidePoints)(s, i);
    return html.replace('<section class="slide', `<section data-style="${ps}" class="slide`);
  })
  .join("\n");

const styleBlocks = Object.keys(STYLES)
  .map((k) => `.slide[data-style="${k}"]{${cssVars(STYLES[k])}}`)
  .join("\n");

const html = `<!DOCTYPE html>
<html lang="zh-CN" data-sj-style="${esc(globalName)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="sj-style" content="${esc(globalName)}">
<meta name="sj-style-reason" content="${esc(decision.reason)}">
<title>${esc(deck.title)}</title>
<style>
:root{${cssVars(globalTokens)}}
${styleBlocks}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:var(--bg);font-family:var(--sans);color:var(--ink);overflow:hidden}
body{display:flex;align-items:center;justify-content:center}
#stage{width:1280px;height:720px;position:relative;transform-origin:center center;overflow:hidden;background:var(--bg)}
.slide{position:absolute;inset:0;padding:var(--pad-y) var(--pad-x) 56px;opacity:0;visibility:hidden;
  transition:opacity .45s ease;background:var(--bg)}
.slide.active{opacity:1;visibility:visible}
.page-no{position:absolute;right:var(--pad-x);bottom:40px;font-size:var(--fs-micro);letter-spacing:.16em;color:var(--muted);font-variant-numeric:tabular-nums}
.a{opacity:0;transform:translateY(16px)}
.slide.active .a{opacity:1;transform:none;transition:opacity .55s ease,transform var(--motion) cubic-bezier(.22,1,.36,1);
  transition-delay:calc(var(--d,0) * var(--stagger))}

/* 封面 */
.cover{padding:0}
.cover-inner{position:absolute;left:var(--pad-x);top:calc(var(--pad-y) + 90px);width:900px}
.kicker{font-size:var(--fs-kicker);letter-spacing:.24em;color:var(--accent);text-transform:uppercase}
.cover h1{font-family:var(--serif);font-size:var(--fs-hero);line-height:1.2;font-weight:600;
  letter-spacing:var(--tracking);margin-top:26px;white-space:pre-line}
.rule{position:relative;width:120px;height:1px;background:var(--line);margin:30px 0 24px}
.rule::after{content:"";position:absolute;left:0;top:0;width:32px;height:1px;background:var(--accent)}
.rule.short{width:48px;margin:18px 0 0}
.rule.short::after{width:16px}
.cover .sub{font-size:calc(var(--fs-body) * 1.35);line-height:var(--lead);color:var(--muted);max-width:640px}
.cover-foot{position:absolute;left:var(--pad-x);bottom:56px;display:flex;align-items:center;gap:10px}
.tag{font-size:var(--fs-micro);letter-spacing:.06em;color:var(--ink);border:1px solid var(--line);border-radius:999px;padding:6px 13px}
.meta{font-size:var(--fs-micro);color:var(--muted);margin-left:8px}

/* 满版图片（封面 / 转场 / 封底） */
.cover-art{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
.art-contain{object-fit:contain}
.art-cover .page-no{display:none}
.statement{padding:0;display:flex;align-items:center;justify-content:center}
.stmt-inner{width:1000px;text-align:center}
.stmt-title{font-family:var(--serif);font-size:calc(var(--fs-hero) * .78);line-height:1.12;font-weight:600;letter-spacing:var(--tracking)}
.stmt-sub{font-size:calc(var(--fs-body) * 1.2);color:var(--muted);margin-top:26px;line-height:var(--lead)}
.stmt-inner .kicker{margin-bottom:24px}

/* 页头 */
.slide-head{position:relative;margin-bottom:36px}
.slide-head.tight{margin-bottom:18px}
.slide h2{font-family:var(--serif);font-size:var(--fs-title);font-weight:600;letter-spacing:var(--tracking);line-height:1.25;color:var(--ink)}

/* 数据页 */
.data-body{display:grid;grid-template-columns:320px 1fr;gap:44px;align-items:start}
.kpis{display:flex;flex-direction:column;gap:16px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:20px 22px;box-shadow:var(--shadow)}
.kpi-num{display:block;font-size:var(--fs-kpi);font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;line-height:1.1}
.kpi-num em{font-size:calc(var(--fs-kpi) * .45);font-style:normal;color:var(--accent);margin-left:4px}
.kpi-lab{display:block;font-size:var(--fs-small);color:var(--muted);margin-top:8px}
.chart{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:28px 30px 22px;box-shadow:var(--shadow)}
.bars{height:290px;display:flex;align-items:flex-end;justify-content:space-around;gap:24px;border-bottom:1px solid var(--line)}
.bar-col{flex:1;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;position:relative}
.bar-val{font-size:var(--fs-small);font-weight:600;color:var(--ink);margin-bottom:8px;font-variant-numeric:tabular-nums}
.bar{width:72%;background:var(--accent);border-radius:6px 6px 0 0;height:0;transition:height 1s cubic-bezier(.22,1,.36,1);transition-delay:calc(var(--d,0) * 120ms)}
.slide.active .bar{height:var(--h)}
.bar-lab{position:absolute;bottom:-30px;font-size:var(--fs-small);color:var(--muted)}
.chart-cap{font-size:var(--fs-micro);color:var(--muted);text-align:center;margin-top:42px}
.note{position:absolute;left:var(--pad-x);bottom:40px;font-size:var(--fs-micro);color:var(--muted)}

/* 要点页 */
.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:26px 28px;box-shadow:var(--shadow);position:relative;min-height:150px}
.card .idx{font-size:var(--fs-micro);letter-spacing:.16em;color:var(--accent);font-weight:600}
.card h3{font-size:var(--fs-h3);font-weight:600;color:var(--ink);margin:10px 0 10px}
.card p{font-size:var(--fs-body);line-height:var(--lead);color:var(--muted)}

/* 爆炸视图 */
.exp-wrap{margin-top:2px}
.exp-svg{width:100%;height:456px;display:block;overflow:visible}
.axis{stroke:var(--line);stroke-width:1;stroke-dasharray:7 7}
.part{transform:translate(var(--x),var(--y));transition:transform 1.5s cubic-bezier(.22,1,.36,1) calc(var(--i)*100ms),opacity .45s ease calc(var(--i)*100ms)}
.slide.exploded .part{transform:translate(calc(var(--x) + var(--ex)),calc(var(--y) + var(--ey)))}
.p-fill{fill:var(--surface-alt)}
.p-stroke{stroke:var(--ink);stroke-width:1.2;stroke-opacity:.55}
.p-hollow{fill:var(--surface);stroke:var(--line);stroke-width:1}
.p-hole{fill:none;stroke:var(--ink);stroke-opacity:.5;stroke-width:1.2}
.p-gasket{fill:var(--accent);fill-opacity:.14;stroke:var(--accent);stroke-width:1.2}
.p-hatch{stroke:var(--accent);stroke-opacity:.45;stroke-width:1}
.p-bolt{fill:var(--surface);stroke:var(--ink);stroke-opacity:.6;stroke-width:1.2}
.callout{opacity:0;transition:opacity .5s ease;transition-delay:calc(1.45s + var(--i)*110ms)}
.slide.exploded .callout{opacity:1}
.co-line{stroke:var(--line);stroke-width:1}
.co-dot{fill:var(--accent)}
.co-num{fill:var(--accent);font-family:var(--sans);font-size:13px;font-weight:600;letter-spacing:.12em;text-anchor:middle}
.co-name{fill:var(--ink);font-family:var(--sans);font-size:15px;text-anchor:middle}
.exp-foot{position:absolute;left:var(--pad-x);right:var(--pad-x);bottom:36px;display:flex;align-items:center;justify-content:space-between;gap:24px}
.exp-cap{font-size:var(--fs-small);color:var(--muted);max-width:720px}
.btn{font-family:var(--sans);font-size:var(--fs-micro);letter-spacing:.06em;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:7px 16px;cursor:pointer;transition:background .3s ease,color .3s ease,border-color .3s ease}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn.on{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}

/* 材质页 */
.mats{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.mat-card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column}
.mat-swatch{height:196px;position:relative;overflow:hidden;border-bottom:1px solid var(--line)}
.tex-wrap{position:absolute;inset:0;transition:transform .9s cubic-bezier(.22,1,.36,1)}
.mat-card.zoom .tex-wrap{transform:scale(1.55)}
.tex{position:absolute;inset:0}
.tex-b{opacity:0;transition:opacity .6s ease}
.mat-card.alt .tex-b{opacity:1}
.t-brushed{background:repeating-linear-gradient(90deg,#D9D4CA 0 1px,#EDEAE2 1px 3px,#E1DDD3 3px 4px)}
.t-mirror{background:linear-gradient(115deg,#F7F5F0 0%,#C8C4BA 38%,#F2F0EA 55%,#A7A39A 78%,#E6E3DA 100%)}
.t-anod{background:linear-gradient(155deg,#3B4147 0%,#23272B 72%)}
.t-blast{background-color:#2A2F34;background-image:radial-gradient(circle at 15% 25%,rgba(255,255,255,.22) 0 1px,transparent 1.6px),radial-gradient(circle at 65% 65%,rgba(255,255,255,.16) 0 1px,transparent 1.6px),radial-gradient(circle at 40% 85%,rgba(0,0,0,.28) 0 1px,transparent 1.6px);background-size:11px 11px,9px 9px,13px 13px}
.tex-pcb{background:#0E372A}
.tex-pcb path{fill:none;stroke-width:3;stroke-linejoin:round}
.pcb-a path{stroke:#C9A05A}
.pcb-a circle{fill:#C9A05A}
.pcb-b path{stroke:#C7D2DA}
.pcb-b circle{fill:#C7D2DA}
.pcb-b{opacity:0;transition:opacity .6s ease}
.mat-card.alt .pcb-a{opacity:0}
.mat-card.alt .pcb-b{opacity:1}
.pcb-a{transition:opacity .6s ease}
.sheen{position:absolute;inset:-30% -60%;pointer-events:none;background:linear-gradient(105deg,transparent 42%,rgba(255,255,255,.45) 50%,transparent 58%);transform:translateX(-130%)}
.slide.active .mat-card .sheen{animation:sweep 1.05s cubic-bezier(.22,1,.36,1) forwards;animation-delay:calc(.85s + var(--i)*120ms)}
@keyframes sweep{to{transform:translateX(130%)}}
.mat-info{padding:16px 18px 18px;display:flex;flex-direction:column;flex:1}
.mat-title{display:flex;align-items:center;justify-content:space-between}
.mat-icon{width:18px;height:18px;display:inline-flex;color:var(--accent)}
.mat-icon svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.mat-idx{font-size:var(--fs-micro);letter-spacing:.16em;color:var(--muted)}
.mat-info h3{font-size:var(--fs-h3);font-weight:600;color:var(--ink);margin:8px 0 2px}
.mat-code{font-size:var(--fs-micro);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.mat-desc{font-size:var(--fs-small);line-height:1.6;color:var(--muted);margin-top:10px;flex:1}
.mat-actions{display:flex;gap:8px;margin-top:14px}
.mat-actions .btn{font-size:var(--fs-micro);padding:6px 12px}
.mat-cap{font-size:var(--fs-micro);color:var(--muted);margin-top:16px}

/* 结尾 */
.end{display:flex;align-items:center;justify-content:center}
.end-inner{text-align:center;position:relative}
.end .rule{margin:0 auto 28px}
.end h2{font-family:var(--serif);font-size:calc(var(--fs-hero) * .8);font-weight:600;color:var(--ink);letter-spacing:var(--tracking)}
.end .sub{font-size:var(--fs-body);color:var(--muted);margin-top:14px}
.ring{display:none}

/* ---------- 风格差异：只覆盖变量与少量结构 ---------- */
/* keynote：超大字号、满版光、缓慢推移 */
.slide[data-style="keynote"]::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(ellipse at 68% 24%,rgba(41,151,255,.16),transparent 58%),radial-gradient(ellipse at 18% 92%,rgba(255,255,255,.05),transparent 46%)}
.slide[data-style="keynote"] .cover-inner{left:var(--pad-x);top:50%;transform:translateY(-50%);width:1010px}
.slide[data-style="keynote"].active .cover-inner{animation:kdRise 5.5s cubic-bezier(.22,1,.36,1) both}
@keyframes kdRise{from{transform:translateY(-50%) translateY(12px)}to{transform:translateY(-50%)}}
.slide[data-style="keynote"] .cover h1{font-weight:700;line-height:1.06}
.slide[data-style="keynote"] .kicker{letter-spacing:.3em}
.slide[data-style="keynote"] .cover .sub{color:var(--muted);max-width:760px}
.slide[data-style="keynote"] .card{background:transparent;border:0;border-top:1px solid var(--line);border-radius:0;padding:22px 0}
.slide[data-style="keynote"] .card .idx{font-size:var(--fs-micro);letter-spacing:.2em}
.slide[data-style="keynote"] .slide-head{margin-bottom:44px}
.slide[data-style="keynote"] .data-body .kpi{background:transparent;border:1px solid var(--line);border-radius:0}
.slide[data-style="keynote"] .chart{background:transparent;border:0;box-shadow:none;padding-left:0;padding-right:0}

/* academic：深蓝、严谨、页脚 */
.slide[data-style="academic"]::after{content:attr(data-foot);position:absolute;left:var(--pad-x);bottom:26px;
  font-size:var(--fs-micro);letter-spacing:.08em;color:var(--muted)}
.slide[data-style="academic"] .page-no{bottom:26px;font-size:var(--fs-micro)}
.slide[data-style="academic"] .card{box-shadow:none}
.slide[data-style="academic"] .chart{box-shadow:none}
.slide[data-style="academic"] .bars{border-bottom:1px solid var(--line)}
.slide[data-style="academic"] .rule.short{width:56px;margin-top:14px}
.slide[data-style="academic"] .cover h1{font-weight:600}

/* consulting：结论先行、左竖线、角标编号、强网格 */
.slide[data-style="consulting"] .slide-head .rule{display:none}
.slide[data-style="consulting"] h2{border-left:3px solid var(--accent);padding-left:14px;font-family:var(--sans);font-weight:700;line-height:1.22}
.slide[data-style="consulting"] .page-no::before{content:"EXHIBIT ";letter-spacing:.14em}
.slide[data-style="consulting"] .page-no{font-size:var(--fs-micro)}
.slide[data-style="consulting"] .kpi{border-radius:0;border:0;border-top:1px solid var(--line);padding:14px 0}
.slide[data-style="consulting"] .chart{border-radius:0;box-shadow:none}
.slide[data-style="consulting"] .card{border-radius:0}
.slide[data-style="consulting"] .rule{width:56px;height:3px;background:var(--ink)}
.slide[data-style="consulting"] .rule::after{display:none}
.slide[data-style="consulting"] .cover-inner{width:1000px}
.slide[data-style="consulting"] .cover h1{font-family:var(--sans);font-weight:700;letter-spacing:-.025em}

/* contest：强对比、巨大数字、单强调色 */
.slide[data-style="contest"] .kpi{border-radius:0;border:0;border-left:4px solid var(--accent);padding:10px 0 10px 20px;background:transparent}
.slide[data-style="contest"] .kpi-num{font-size:var(--fs-kpi);font-weight:800;letter-spacing:-.04em}
.slide[data-style="contest"] .chart{border:0;border-top:2px solid var(--ink);border-radius:0;box-shadow:none;padding-left:0;padding-right:0}
.slide[data-style="contest"] .bar{border-radius:0}
.slide[data-style="contest"] .card{border:0;border-top:3px solid var(--ink);border-radius:0;box-shadow:none;padding:22px 0}
.slide[data-style="contest"] .cover h1{font-weight:800;line-height:1.08}
.slide[data-style="contest"] .rule{width:64px;height:6px;background:var(--accent)}
.slide[data-style="contest"] .rule::after{display:none}
.slide[data-style="contest"] .cover-inner{top:calc(var(--pad-y) + 66px)}

/* minimal-art：纸感、细线、无卡片阴影、极慢极轻 */
.slide[data-style="minimal-art"] .a{transform:translateY(24px)}
.slide[data-style="minimal-art"].active .a{transition:opacity .72s ease,transform .72s cubic-bezier(.22,1,.36,1);transition-delay:calc(var(--d,0) * 100ms)}
.slide[data-style="minimal-art"] .card{background:transparent;border:0;border-bottom:1px solid var(--line);border-radius:0;box-shadow:none;padding:22px 0;min-height:auto}
.slide[data-style="minimal-art"] .card h3{font-weight:400}
.slide[data-style="minimal-art"] .kpi{background:transparent;border:0;border-left:1px solid var(--line);border-radius:0;box-shadow:none;padding:6px 0 6px 18px}
.slide[data-style="minimal-art"] .chart{background:transparent;border:0;border-radius:0;box-shadow:none;padding-left:0;padding-right:0}
.slide[data-style="minimal-art"] .bar{background:transparent;border:1px solid var(--ink);border-bottom:0;border-radius:0}
.slide[data-style="minimal-art"] .bar-val{color:var(--accent)}
.slide[data-style="minimal-art"] .kicker{letter-spacing:.28em;color:var(--accent)}
.slide[data-style="minimal-art"] .rule{background:var(--line)}
.slide[data-style="minimal-art"] .rule::after{width:24px}
.slide[data-style="minimal-art"] .cover-inner{top:calc(var(--pad-y) + 96px)}
.slide[data-style="minimal-art"] .cover h1{font-weight:400;line-height:1.14}
.slide[data-style="minimal-art"] .end-inner::before{content:"";position:absolute;left:50%;top:-118px;width:96px;height:96px;margin-left:-48px;
  border:1px solid var(--accent);border-radius:50%;opacity:.55}
.slide[data-style="minimal-art"] .page-no{letter-spacing:.24em}
.slide[data-style="minimal-art"] .tag{border:0;border-bottom:1px solid var(--line);border-radius:0;padding:4px 2px}
.slide[data-style="minimal-art"] .mat-swatch,.slide[data-style="minimal-art"] .mat-card{border-radius:0}

/* HUD */
.progress{position:fixed;left:0;right:0;bottom:0;height:3px;background:rgba(120,120,120,.15);pointer-events:none}
.progress span{display:block;height:100%;width:0;background:var(--accent);transition:width .45s ease}
.pager{position:fixed;right:20px;bottom:14px;font-size:var(--fs-micro);letter-spacing:.14em;color:var(--muted);font-variant-numeric:tabular-nums}
.hint{position:fixed;left:20px;top:12px;font-size:10px;color:var(--muted);letter-spacing:.06em;transition:opacity .4s ease}
.hint.hide{opacity:0}
</style>
</head>
<body>
<div id="stage">
${slidesHtml}
</div>
<div class="progress"><span id="bar"></span></div>
<div class="pager"><span id="cur">01</span> / ${String(slideCount).padStart(2, "0")}</div>
<div class="hint">← → / 空格 翻页 · F 全屏 · R 合拢/分解</div>
<script>
window.__SJ_STYLE__={name:${JSON.stringify(globalName)},label:${JSON.stringify(LABEL[globalName])},reason:${JSON.stringify(decision.reason)}};
(function(){
  var slides=Array.prototype.slice.call(document.querySelectorAll('.slide'));
  var bar=document.getElementById('bar'),cur=document.getElementById('cur');
  var i=0,locked=false,autoTimer=null;
  function scale(){
    var s=Math.min(innerWidth/1280,innerHeight/720);
    document.getElementById('stage').style.transform='scale('+s+')';
  }
  function countUp(slide){
    slide.querySelectorAll('.num').forEach(function(el){
      var to=Number(el.dataset.to)||0; if(!to) return;
      var dur=900,st=performance.now(); el.textContent='0';
      function tick(now){
        var p=Math.min(1,(now-st)/dur),e=1-Math.pow(1-p,3);
        el.textContent=String(Math.round(to*e));
        if(p<1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  }
  function resetFx(sl){
    sl.classList.remove('exploded');
    sl.querySelectorAll('.mat-card').forEach(function(c){ c.classList.remove('alt','zoom'); });
    var tg=sl.querySelector('.exp-toggle'); if(tg) tg.textContent='分解';
    tg && tg.classList.remove('on');
  }
  function go(n){
    if(locked) return;
    n=Math.max(0,Math.min(slides.length-1,n));
    if(n===i&&slides[i].classList.contains('active')) return;
    locked=true;
    if(autoTimer){clearTimeout(autoTimer);autoTimer=null;}
    slides.forEach(function(s,k){
      if(k!==n&&s.classList.contains('active')) resetFx(s);
      s.classList.toggle('active',k===n);
    });
    i=n; bar.style.width=((i+1)/slides.length*100)+'%';
    cur.textContent=String(i+1).padStart(2,'0');
    var sl=slides[i];
    var hintEl=document.querySelector('.hint');
    if(hintEl) hintEl.classList.toggle('hide', sl.classList.contains('art-cover'));
    setTimeout(function(){countUp(sl);},160);
    if(sl.dataset.type==='exploded'){
      autoTimer=setTimeout(function(){
        sl.classList.add('exploded');
        var tg=sl.querySelector('.exp-toggle');
        if(tg){tg.textContent='合拢';tg.classList.add('on');}
      },420);
    }
    setTimeout(function(){locked=false;},520);
  }
  function toggleExplode(sl){
    var on=sl.classList.toggle('exploded');
    var tg=sl.querySelector('.exp-toggle');
    if(tg){tg.textContent=on?'合拢':'分解';tg.classList.toggle('on',on);}
  }
  document.addEventListener('click',function(e){
    var tg=e.target.closest('.exp-toggle');
    if(tg){e.stopPropagation();toggleExplode(tg.closest('.slide'));return;}
    var mt=e.target.closest('.mat-toggle');
    if(mt){
      e.stopPropagation();
      var card=mt.closest('.mat-card');
      var on=card.classList.toggle('alt');
      mt.textContent=on?(mt.dataset.b||'还原'):'切换材质';
      mt.classList.toggle('on',on);
      return;
    }
    var zt=e.target.closest('.zoom-toggle');
    if(zt){
      e.stopPropagation();
      var c2=zt.closest('.mat-card');
      var z=c2.classList.toggle('zoom');
      zt.textContent=z?'复位':'局部放大';
      zt.classList.toggle('on',z);
      return;
    }
    var mc=e.target.closest('.mat-swatch');
    if(mc){e.stopPropagation();var c3=mc.closest('.mat-card');c3.classList.toggle('alt');return;}
    go(i+1);
  });
  addEventListener('resize',scale); scale();
  addEventListener('keydown',function(e){
    if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown'){e.preventDefault();go(i+1);}
    if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();go(i-1);}
    if(e.key==='Home'){go(0);} if(e.key==='End'){go(slides.length-1);}
    if(e.key==='r'||e.key==='R'){
      var sl=slides[i]; if(sl.dataset.type==='exploded'){e.preventDefault();toggleExplode(sl);}
    }
    if(e.key==='f'||e.key==='F'){
      if(!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen();
    }
  });
  go(0);
})();
</script>
</body>
</html>`;

fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, html, "utf8");
console.log(`HTML 已生成: ${outPath}（${slideCount} 页，风格 ${globalName}｜${LABEL[globalName]}）`);
console.log(`风格理由: ${decision.reason}`);
