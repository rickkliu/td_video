// Code-rendered motion-graphics ad for BEA Transaction Banking Applications Team.
// Palette derived from BEA brand: primary vermillion #EA4120 (logo red), coral #F49F8F,
// blush #FCE6E1, amber #FFA901, orange #F66E0E, warm neutrals.
// Style: flat bold color fields + kinetic typography + studio chrome.
const fs = require('fs');
const path = require('path');
const { Resvg } = require('@resvg/resvg-js');

const W = 1920, H = 1080, FPS = 30;
const args = Object.fromEntries(process.argv.slice(2).map(a => a.split('=')));
const LANG = (args.lang || 'zh').toLowerCase();

const C = {
  ink: '#1C100C',      // warm near-black
  ink2: '#2B1A14',
  paper: '#FFF6F1',    // warm off-white
  blush: '#FCE6E1',
  red: '#EA4120',      // BEA primary
  redD: '#B62E14',
  redDeep: '#7A1E0B',
  coral: '#F49F8F',
  amber: '#FFA901',
  orange: '#F66E0E',
  white: '#FFFFFF',
  muted: '#8A6F66',    // muted text on light
};
const FONT = 'Noto Sans TC';
const FONT_BLACK = 'Noto Sans TC Black';
const MONO = 'DejaVu Sans Mono';
const FONT_FILES = [
  '/usr/share/fonts/truetype/notocjk/NotoSansTC-Regular.otf',
  '/usr/share/fonts/truetype/notocjk/NotoSansTC-Medium.otf',
  '/usr/share/fonts/truetype/notocjk/NotoSansTC-Bold.otf',
  '/usr/share/fonts/truetype/notocjk/NotoSansTC-Black.otf',
  '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
  '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
];
const LOGO_WHITE = 'data:image/png;base64,' + fs.readFileSync('/workspace/ad_video/assets/bea_logo_white.png').toString('base64');
const LOGO_COLOR = 'data:image/png;base64,' + fs.readFileSync('/workspace/ad_video/assets/bea_logo_color.png').toString('base64');
const BPM = 120;
const TEAM1 = 'Transaction Banking', TEAM2 = 'Applications Team';

// ---------- copy ----------
const TEXT = {
  zh: {
    s1_head: '在數位浪潮中',
    s1_sub: '交易的每一次發生，都需要被看見、被守護、被信任。',
    s1_kw: ['被看見', '被守護', '被信任'],
    s2_eyebrow: '· 實力驗證 / THE PROOF',
    s2_head: '數字，會說話',
    s2_metrics: [
      { pre: '$', num: 1.28, dec: 2, suf: 'B', label: '日均交易處理量', sub: 'DAILY VALUE PROCESSED' },
      { pre: '', num: 99.99, dec: 2, suf: '%', label: '核心系統可用性', sub: 'PLATFORM UPTIME' },
      { pre: '<', num: 180, dec: 0, suf: 'ms', label: '平均交易回應', sub: 'AVG RESPONSE TIME' },
    ],
    s3_eyebrow: '· 產品全景 / THE SUITE',
    s3_head: '從支付，到貿易融資',
    s3_tail: '覆蓋企業客戶的日常交易流程',
    s3_cards: [
      { no: '01', big: '支付', tag: 'PAYMENTS', desc: '付款 · 清算 · 跨境' },
      { no: '02', big: '現金管理', tag: 'CASH MANAGEMENT', desc: '流動性 · 資金池 · 集團視圖' },
      { no: '03', big: '貿易融資', tag: 'TRADE FINANCE', desc: '信用狀 · 保理 · 供應鏈' },
    ],
    s4_eyebrow: '· CORE SYSTEMS',
    s4_head: '核心應用系統',
    s4_chips: ['01  規劃', '02  開發', '03  持續優化'],
    s4_caption: '無論多複雜的業務邏輯，我們都能讓它井然有序。',
    s5_eyebrow: '· 我們的承諾 / THE PROMISE',
    s5_pairs: [
      { k: '讓複雜變得', w: '順暢' },
      { k: '讓安全變得', w: '自然' },
      { k: '讓創新', w: '與時俱進' },
    ],
    s6_tag: '以科技為翼，讓信任與時並進',
    chapters: ['數位浪潮', '實力數據', '產品全景', '核心系統', '我們的承諾', '品牌落版'],
    wordmark: 'Transaction Banking Applications Team',
  },
  en: {
    s1_head: 'In a digital tide',
    s1_sub: 'every transaction must be seen, safeguarded, and trusted.',
    s1_kw: ['SEEN', 'SAFEGUARDED', 'TRUSTED'],
    s2_eyebrow: '· THE PROOF',
    s2_head: 'Proof, in numbers.',
    s2_metrics: [
      { pre: '$', num: 1.28, dec: 2, suf: 'B', label: 'Daily value processed', sub: 'VALUE / DAY' },
      { pre: '', num: 99.99, dec: 2, suf: '%', label: 'Platform uptime', sub: 'AVAILABILITY' },
      { pre: '<', num: 180, dec: 0, suf: 'ms', label: 'Avg response time', sub: 'LATENCY' },
    ],
    s3_eyebrow: '· THE SUITE',
    s3_head: 'From payments to trade finance',
    s3_tail: "Our clients\u2019 everyday transaction flow, covered end to end.",
    s3_cards: [
      { no: '01', big: 'Payments', tag: 'PAYMENT RAILS', desc: 'Instant clearing · Cross-border · 24/7' },
      { no: '02', big: 'Cash Management', tag: 'LIQUIDITY', desc: 'Pooling · Visibility · Control' },
      { no: '03', big: 'Trade Finance', tag: 'TRADE & SUPPLY CHAIN', desc: 'Letters of credit · Supply chain' },
    ],
    s4_eyebrow: '· CORE SYSTEMS',
    s4_head: 'Core application systems',
    s4_chips: ['01  PLAN', '02  BUILD', '03  OPTIMISE'],
    s4_caption: 'However complex the business logic, we keep it in order.',
    s5_eyebrow: '· THE PROMISE',
    s5_pairs: [
      { k: 'Complex, made', w: 'SMOOTH' },
      { k: 'Security, made', w: 'NATURAL' },
      { k: 'Innovation,', w: 'ALWAYS CURRENT' },
    ],
    s6_tag: 'Wings of technology, trust that moves with the times',
    chapters: ['THE TIDE', 'THE PROOF', 'THE SUITE', 'THE SYSTEMS', 'THE PROMISE', 'THE SIGN-OFF'],
    wordmark: 'Transaction Banking Applications Team',
  },
};
const Tx = TEXT[LANG];

// ---------- helpers ----------
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const eoc = t => { t = clamp(t, 0, 1); return 1 - Math.pow(1 - t, 3); };
const eob = t => { t = clamp(t, 0, 1); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
const seg = (t, a, b) => clamp((t - a) / (b - a), 0, 1);
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function T(x, y, str, o = {}) {
  const { size = 40, fill = C.ink, weight = 700, anchor = 'start', family = FONT, ls = 0, opacity = 1 } = o;
  return `<text x="${x}" y="${y}" font-family="${family}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}" letter-spacing="${ls}" opacity="${opacity}">${esc(str)}</text>`;
}
const parseHex = h => { h = h.replace('#', ''); return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; };
const rgba = (hex, a) => { const [r, g, b] = parseHex(hex); return `rgba(${r},${g},${b},${a})`; };

// rough advance-width estimate (em units) so latin text can be centred / fitted
function estEm(str) {
  let s = 0;
  for (const ch of str) {
    const c = ch.codePointAt(0);
    if ((c >= 0x4E00 && c <= 0x9FFF) || (c >= 0x3000 && c <= 0x303F) || (c >= 0xFF00 && c <= 0xFF60)) s += 1.0;
    else if (ch === ' ') s += 0.30;
    else if (ch >= '0' && ch <= '9') s += 0.58;
    else if (/[A-Z]/.test(ch)) s += 0.65;
    else if (/[a-z]/.test(ch)) s += 0.53;
    else if ('.,:;!?\'"\u2019\u2018'.includes(ch)) s += 0.28;
    else if ('-–—'.includes(ch)) s += 0.42;
    else s += 0.55;
  }
  return s;
}
const estW = (str, size) => estEm(str) * size;
const fitSize = (str, maxW, base) => Math.min(base, maxW / Math.max(estEm(str), 0.001));
const isCJK = str => /[\u4E00-\u9FFF]/.test(str);

let _uid = 0;

function dotsGrid(fill, op, step = 72) {
  let s = '';
  for (let x = step; x < W; x += step) for (let y = step; y < H; y += step)
    s += `<circle cx="${x}" cy="${y}" r="2" fill="${fill}" opacity="${op}"/>`;
  return s;
}

// CJK: per-character stagger (full-width glyphs => exact metrics)
function stagger(cx, baseY, str, o = {}) {
  const { size = 120, fill = C.ink, weight = 900, family = FONT_BLACK, t = 0, start = 0, stag = 0.055, rise = 70, durd = 0.5 } = o;
  const chars = [...str], x0 = cx - chars.length * size / 2;
  let s = '';
  chars.forEach((ch, i) => {
    const e = eoc(seg(t, start + i * stag, start + i * stag + durd));
    s += `<g opacity="${e}">${T(x0 + i * size, baseY + (1 - e) * rise, ch, { size, fill, weight, family })}</g>`;
  });
  return s;
}
// latin: left-to-right mask reveal (no hard metric dependency)
function reveal(cx, baseY, str, o = {}) {
  const { size = 120, fill = C.ink, weight = 900, family = FONT_BLACK, t = 0, start = 0, durd = 0.7 } = o;
  const wd = estW(str, size), x0 = cx - wd / 2;
  const prog = eoc(seg(t, start, start + durd));
  const id = 'rv' + (++_uid);
  return `<clipPath id="${id}"><rect x="${x0 - 24}" y="${baseY - size}" width="${prog * (wd + 48)}" height="${size * 1.5}"/></clipPath>
    <g clip-path="url(#${id})">${T(cx, baseY, str, { size, fill, weight, anchor: 'middle', family })}</g>`;
}
// language-aware headline
function headline(cx, baseY, str, o = {}) {
  const maxW = (o.maxW || (W - 2 * 150));
  const base = o.size || 150;
  const size = fitSize(str, maxW, base);
  const common = { ...o, size };
  return isCJK(str) ? stagger(cx, baseY, str, common) : reveal(cx, baseY, str, common);
}

function pill(cx, cy, str, o = {}) {
  const { size = 30, padX = 28, h = 66, stroke = C.ink, txt = C.ink, weight = 900, opacity = 1, fill = 'none' } = o;
  const w = estW(str, size) + padX * 2, x = cx - w / 2;
  return `<g opacity="${opacity}">
    <rect x="${x}" y="${cy - h / 2}" width="${w}" height="${h}" rx="${h / 2}" fill="${fill}" stroke="${stroke}" stroke-width="3"/>
    ${T(cx, cy + size * 0.35, str, { size, fill: txt, weight, anchor: 'middle' })}
  </g>`;
}

// beat-synced pulse (drives the "energy" feel)
function beatPulse(gt, bpm = BPM) {
  const phase = ((gt * bpm / 60) % 1 + 1) % 1;
  return Math.pow(1 - phase, 3);
}
function logoMark(x, y, w, white = true) {
  return `<image href="${white ? LOGO_WHITE : LOGO_COLOR}" x="${x}" y="${y}" width="${w}" height="${(w * 47 / 242).toFixed(1)}"/>`;
}

// ---------- studio chrome (editorial HUD) ----------
function chrome(gt, fg) {
  const pad = 56, pulse = beatPulse(gt);
  const br = rgba(fg, 0.32 + 0.38 * pulse);
  const tcol = rgba(fg, 0.62);
  const CR = 15;
  const cross = (x, y) => `<path d="M ${x - CR} ${y} L ${x + CR} ${y} M ${x} ${y - CR} L ${x} ${y + CR}" stroke="${br}" stroke-width="2.5"/>`;
  let s = cross(pad, pad) + cross(W - pad, pad) + cross(pad, H - pad) + cross(W - pad, H - pad);

  const label = 'TXN BANKING / APPS TEAM';
  s += `<g>
    <circle cx="${pad + 34}" cy="${pad + 1}" r="${5 + 5 * pulse}" fill="${rgba(C.red, 0.35)}"/>
    <circle cx="${pad + 34}" cy="${pad + 1}" r="5" fill="${C.red}"/>
    ${T(pad + 52, pad + 8, label, { size: 22, fill: tcol, weight: 700, family: MONO, ls: 3 })}
  </g>`;

  const tc = 'T+' + gt.toFixed(3).padStart(6, '0') + 's';
  s += T(W - pad - 30, pad + 8, tc, { size: 22, fill: tcol, weight: 700, anchor: 'end', family: MONO, ls: 2 });

  const i = sceneIdx(gt);
  s += T(pad + 30, H - pad + 8, String(i + 1).padStart(2, '0') + ' — ' + Tx.chapters[i], { size: 22, fill: rgba(fg, 0.82), weight: 700, family: LANG === 'zh' ? FONT : MONO, ls: 3 });
  s += T(W - pad - 30, H - pad + 8, `1920\u00d71080 · 30 FPS · ${BPM} BPM`, { size: 22, fill: tcol, weight: 700, anchor: 'end', family: MONO, ls: 2 });
  return s;
}

// ---------- scenes ----------
const M = 150;

// animated rising line chart (transaction volume)
function lineChart(x, y, w, h, t, o = {}) {
  const { start = 0.4, durd = 1.5, stroke = C.red, accent = C.amber, title = '', note = '', xlabels = null } = o;
  const n = 12;
  let seed = 11;
  const rnd = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
  const vals = [];
  for (let i = 0; i < n; i++) {
    const base = 0.10 + 0.80 * Math.pow(i / (n - 1), 1.5);
    vals.push(clamp(base + (i > 0 ? (rnd() - 0.45) * 0.06 : 0), 0.04, 0.96));
  }
  const px = i => x + i * (w / (n - 1));
  const py = v => y + h - v * h;
  let s = '';
  for (let k = 0; k <= 4; k++) {
    const yy = y + h * k / 4;
    s += `<line x1="${x}" y1="${yy}" x2="${x + w}" y2="${yy}" stroke="${rgba(C.ink, 0.1)}" stroke-width="1.5"/>`;
  }
  s += `<line x1="${x}" y1="${y + h}" x2="${x + w}" y2="${y + h}" stroke="${rgba(C.ink, 0.3)}" stroke-width="2"/>`;
  if (title) s += T(x, y - 28, title, { size: 24, fill: C.muted, weight: 700, family: MONO, ls: 3 });

  const line = 'M ' + vals.map((v, i) => `${px(i)} ${py(v)}`).join(' L ');
  const area = line + ` L ${px(n - 1)} ${y + h} L ${px(0)} ${y + h} Z`;
  const prog = eoc(seg(t, start, start + durd));
  const id = 'lc' + (++_uid);
  s += `<clipPath id="${id}"><rect x="${x - 8}" y="${y - 70}" width="${prog * (w + 16)}" height="${h + 140}"/></clipPath>`;
  s += `<g clip-path="url(#${id})">
    <path d="${area}" fill="${rgba(stroke, 0.13)}"/>
    <path d="${line}" fill="none" stroke="${stroke}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>
    ${vals.map((v, i) => `<circle cx="${px(i)}" cy="${py(v)}" r="6" fill="${stroke}"/>`).join('')}
  </g>`;
  if (prog > 0.02 && prog < 0.995) {
    const pos = prog * (n - 1), i0 = Math.min(n - 2, Math.floor(pos)), fr = pos - i0;
    const hx = px(i0) + (px(i0 + 1) - px(i0)) * fr;
    const hy = py(vals[i0]) + (py(vals[i0 + 1]) - py(vals[i0])) * fr;
    s += `<circle cx="${hx}" cy="${hy}" r="12" fill="${C.paper}" stroke="${stroke}" stroke-width="4"/>`;
  }
  const endp = eoc(seg(t, start + durd * 0.9, start + durd + 0.15));
  const ex = px(n - 1), ey = py(vals[n - 1]);
  s += `<g opacity="${endp}">
    <circle cx="${ex}" cy="${ey}" r="10" fill="${accent}"/>
    ${note ? T(ex - 16, ey - 24, note, { size: 30, fill: accent, weight: 900, anchor: 'end', family: LANG === 'zh' ? FONT : MONO }) : ''}
  </g>`;
  if (xlabels) xlabels.forEach((lb, i2) => {
    s += T(x + (i2 + 0.5) * (w / xlabels.length), y + h + 34, lb, { size: 20, fill: C.muted, weight: 700, anchor: 'middle', family: MONO, ls: 2 });
  });
  return s;
}

// faint rising trend line for background texture
function bgTrend(t) {
  const n = 26, x0 = 220, x1 = W - 220, yb = 1010, yt = 560;
  const pts = [];
  for (let i = 0; i < n; i++) {
    const v = Math.pow(i / (n - 1), 1.25) + 0.05 * Math.sin(i * 1.9);
    pts.push([x0 + (x1 - x0) * i / (n - 1), yb - (yb - yt) * clamp(v, 0, 1.05)]);
  }
  const prog = eoc(seg(t, 0.2, 5.4));
  const id = 'bt' + (++_uid);
  const d = pts.map((p, i) => `${i ? 'L' : 'M'} ${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  return `<clipPath id="${id}"><rect x="0" y="0" width="${prog * W}" height="${H}"/></clipPath>
    <g clip-path="url(#${id})" opacity="0.18"><path d="${d}" fill="none" stroke="${C.white}" stroke-width="4" stroke-linejoin="round"/></g>`;
}

function s1(t) { // digital tide / warm ink
  let s = `<rect width="${W}" height="${H}" fill="${C.ink}"/>`;
  s += dotsGrid(C.amber, 0.06);
  const N = 42, bw = 14, gap = 26, totalW = N * bw + (N - 1) * gap;
  const x0 = (W - totalW) / 2, baseY = H - 250;
  let bars = '';
  for (let i = 0; i < N; i++) {
    const h = 26 + 78 * (0.5 + 0.5 * Math.sin(t * 2.2 + i * 0.42)) * (0.6 + 0.4 * Math.sin(i));
    const op = 0.22 + 0.4 * (0.5 + 0.5 * Math.sin(t * 2.2 + i * 0.42));
    bars += `<rect x="${x0 + i * (bw + gap)}" y="${baseY - h}" width="${bw}" height="${h}" rx="4" fill="${i % 7 === 3 ? C.amber : C.red}" opacity="${op}"/>`;
  }
  s += `<g opacity="${seg(t, 0.1, 0.8)}">${bars}</g>`;
  s += `<line x1="${M}" y1="${baseY + 40}" x2="${W - M}" y2="${baseY + 40}" stroke="${rgba(C.paper, 0.2)}" stroke-width="2"/>`;

  s += headline(W / 2, 430, Tx.s1_head, { t, size: 150, fill: C.paper, start: 0.25, maxW: W - 260 });
  const p = seg(t, 1.35, 2.05);
  s += `<g opacity="${eoc(p)}" transform="translate(0,${(1 - eoc(p)) * 30})">
    ${T(W / 2, 540, Tx.s1_sub, { size: LANG === 'en' ? 42 : 50, fill: rgba(C.paper, 0.82), weight: 500, anchor: 'middle' })}
  </g>`;
  Tx.s1_kw.forEach((k, i) => {
    const pp = eoc(seg(t, 2.3 + i * 0.28, 2.8 + i * 0.28));
    s += `<g opacity="${pp}">${T(W / 2 - 340 + i * 340, 700, '· ' + k, { size: LANG === 'en' ? 30 : 42, fill: C.amber, weight: 900, anchor: 'middle', ls: 2 })}</g>`;
  });
  return s;
}

// mono number with coloured pre/suffix (tabular digits -> stable count-up)
function numText(x, y, pre, digits, suf, size) {
  return `<text x="${x}" y="${y}" font-family="${MONO}" font-size="${size}" font-weight="700" fill="${C.ink}">` +
    (pre ? `<tspan fill="${C.red}">${esc(pre)}</tspan>` : '') +
    `<tspan>${esc(digits)}</tspan>` +
    (suf ? `<tspan fill="${C.red}">${esc(suf)}</tspan>` : '') +
    `</text>`;
}

function s2(t) { // THE PROOF — count-up metrics / paper
  let s = `<rect width="${W}" height="${H}" fill="${C.paper}"/>`;
  s += T(M, 190, Tx.s2_eyebrow, { size: 26, fill: C.muted, weight: 700, family: MONO, ls: 3 });
  s += headline(W / 2, 350, Tx.s2_head, { t, size: 118, fill: C.ink, start: 0.2, maxW: W - 300 });
  Tx.s2_metrics.forEach((m, i) => {
    const st = 0.85 + i * 0.5;
    const inE = eoc(seg(t, st - 0.15, st + 0.3));
    if (inE <= 0.01) return;
    const ce = eoc(seg(t, st, st + 1.05));
    const cy = 520 + i * 190;
    const dy = (1 - inE) * 42;
    s += `<g opacity="${inE}" transform="translate(0,${dy.toFixed(1)})">`;
    const dw = eoc(seg(t, st - 0.1, st + 0.5)) * (W - 2 * M);
    s += `<rect x="${M}" y="${cy - 150}" width="${dw.toFixed(0)}" height="2" fill="${rgba(C.ink, 0.14)}"/>`;
    s += `<rect x="${M}" y="${cy - 18}" width="20" height="20" fill="${C.red}"/>`;
    s += numText(M + 62, cy + 55, m.pre, (m.num * ce).toFixed(m.dec), m.suf, 150);
    s += T(1240, cy - 4, m.label, { size: 46, fill: C.ink, weight: 900, family: LANG === 'zh' ? FONT_BLACK : FONT });
    s += T(1240, cy + 48, m.sub, { size: 24, fill: C.muted, weight: 700, family: MONO, ls: 3 });
    s += T(W - M, cy + 55, '0' + (i + 1), { size: 30, fill: C.muted, weight: 700, anchor: 'end', family: MONO });
    s += `</g>`;
  });
  return s;
}

function s3(t) { // THE SUITE — product cards / dark
  let s = `<rect width="${W}" height="${H}" fill="${C.ink}"/>`;
  s += dotsGrid(C.amber, 0.06);
  s += T(M, 200, Tx.s3_eyebrow, { size: 26, fill: rgba(C.paper, 0.55), weight: 700, family: MONO, ls: 3 });
  s += headline(W / 2, 330, Tx.s3_head, { t, size: 112, fill: C.paper, start: 0.25, maxW: W - 300 });
  s += T(W / 2, 424, Tx.s3_tail, { size: LANG === 'en' ? 30 : 34, fill: rgba(C.paper, 0.6), weight: 500, anchor: 'middle', opacity: eoc(seg(t, 1.0, 1.6)) });
  const cols = [C.red, C.amber, C.coral];
  Tx.s3_cards.forEach((c, i) => {
    const st = 1.15 + i * 0.3;
    const p = eoc(seg(t, st, st + 0.55));
    if (p <= 0.01) return;
    const cw = 460, ch = 350;
    const cx = W / 2 + (i - 1) * (cw + 50), x0 = cx - cw / 2, y0 = 486;
    const dy = (1 - p) * 60;
    s += `<g opacity="${p}" transform="translate(0,${dy.toFixed(1)})">`;
    s += `<rect x="${x0}" y="${y0}" width="${cw}" height="${ch}" rx="6" fill="${rgba(C.white, 0.045)}" stroke="${rgba(C.white, 0.14)}" stroke-width="2"/>`;
    s += `<rect x="${x0}" y="${y0}" width="${cw}" height="10" rx="5" fill="${cols[i]}"/>`;
    s += T(x0 + cw - 36, y0 + 128, c.no, { size: 120, fill: rgba(C.white, 0.09), weight: 700, anchor: 'end', family: MONO });
    s += T(x0 + 44, y0 + 86, c.tag, { size: 24, fill: cols[i], weight: 700, family: MONO, ls: 4 });
    if (LANG === 'zh') {
      s += T(x0 + 44, y0 + 205, c.big, { size: 92, fill: C.paper, weight: 900, family: FONT_BLACK });
    } else {
      const words = String(c.big).split(' ');
      if (words.length === 1) {
        s += T(x0 + 44, y0 + 215, words[0], { size: 60, fill: C.paper, weight: 900, family: FONT_BLACK });
      } else {
        words.forEach((wd, j) => { s += T(x0 + 44, y0 + 172 + j * 70, wd, { size: 60, fill: C.paper, weight: 900, family: FONT_BLACK }); });
      }
    }
    s += T(x0 + 44, y0 + 292, c.desc, { size: LANG === 'en' ? 27 : 30, fill: rgba(C.paper, 0.62), weight: 500 });
    s += T(x0 + 44, y0 + ch - 36, '\u2192', { size: 34, fill: cols[i], weight: 900, family: MONO });
    s += `</g>`;
  });
  return s;
}

function s4(t) { // core systems + rising transaction volume / paper
  let s = `<rect width="${W}" height="${H}" fill="${C.paper}"/>`;
  s += T(M, 200, Tx.s4_eyebrow, { size: 26, fill: C.muted, weight: 700, family: MONO, ls: 3 });
  s += headline(W / 2, 378, Tx.s4_head, { t, size: 132, fill: C.ink, start: 0.3, maxW: W - 300 });
  Tx.s4_chips.forEach((c, i) => {
    const pp = seg(t, 0.9 + i * 0.2, 1.2 + i * 0.2);
    s += `<g opacity="${eoc(pp)}" transform="translate(0,${(1 - eoc(pp)) * 20})">${pill(W / 2 - 340 + i * 340, 520, c, { size: 32, stroke: C.ink, txt: C.ink, h: 72, padX: 32 })}</g>`;
  });
  s += lineChart(300, 648, W - 600, 214, t, {
    start: 1.3, durd: 1.5, stroke: C.red, accent: C.amber,
    title: LANG === 'en' ? 'TRANSACTION VOLUME' : '交易處理量 / TRANSACTION VOLUME',
    note: LANG === 'en' ? '▲ ON THE RISE' : '▲ 節節上升',
    xlabels: ['Q1', 'Q2', 'Q3', 'Q4'],
  });
  s += T(W / 2, 962, Tx.s4_caption, { size: 30, fill: C.muted, weight: 500, anchor: 'middle', opacity: eoc(seg(t, 2.6, 3.2)) });
  return s;
}

function s5(t) { // THE PROMISE — kinetic word slams on the beat / accent
  let s = `<rect width="${W}" height="${H}" fill="${C.orange}"/>`;
  s += `<rect width="${W}" height="${H}" fill="${C.red}" opacity="0.22"/>`;
  s += bgTrend(t);
  s += T(W / 2, 250, Tx.s5_eyebrow, { size: 28, fill: rgba(C.white, 0.9), weight: 700, anchor: 'middle', family: MONO, ls: 8 });

  const pairs = Tx.s5_pairs, per = 2.0;
  pairs.forEach((p, k) => {
    const st = 0.5 + k * per, lt = t - st;
    const last = k === pairs.length - 1;
    if (lt < -0.05 || (!last && lt > per + 0.1) || lt > 6.4) return;
    const kp = eoc(seg(lt, 0.0, 0.3));                  // kicker first
    const slam = eob(seg(lt, 0.5, 1.0));                // word lands ON the beat
    const opIn = clamp(seg(lt, 0.45, 0.62), 0, 1);
    const opOut = last ? 1 : 1 - eoc(seg(lt, per - 0.15, per + 0.05));
    const op = opIn * opOut;
    if (op <= 0.01) return;
    const wordY = 640, scale = 1 + 0.55 * (1 - slam);
    s += `<g opacity="${op}">
      <g opacity="${kp}" transform="translate(0,${((1 - kp) * 24).toFixed(1)})">
        ${T(W / 2, 430, p.k, { size: 46, fill: rgba(C.white, 0.85), weight: 700, anchor: 'middle', ls: 6 })}
      </g>
      <g transform="translate(${W / 2},${wordY}) scale(${scale.toFixed(3)}) translate(${-W / 2},${-wordY})">
        ${T(W / 2, wordY, p.w, { size: fitSize(p.w, W - 320, LANG === 'en' ? 185 : 240), fill: C.white, weight: 900, anchor: 'middle', family: FONT_BLACK })}
      </g>`;
    const uw = eoc(seg(lt, 0.6, 1.1));
    if (uw > 0) {
      const wW = Math.min(480, isCJK(p.w) ? [...p.w].length * 130 : 380);
      s += `<rect x="${(W / 2 - (wW * uw) / 2).toFixed(0)}" y="${wordY + 44}" width="${(wW * uw).toFixed(0)}" height="12" fill="${C.red}"/>`;
    }
    s += `</g>`;
  });
  // progress ticks
  let active = -1;
  pairs.forEach((p, k) => { if (t >= 0.5 + k * per + 0.5) active = k; });
  pairs.forEach((p, k) => {
    const on = k === active;
    s += `<rect x="${W / 2 - 120 + k * 90}" y="${on ? 796 : 799}" width="${on ? 64 : 40}" height="${on ? 8 : 5}" fill="${on ? C.white : rgba(C.white, 0.35)}"/>`;
  });
  return s;
}

function s6(t) { // THE SIGN-OFF — team lockup / warm ink
  let s = `<rect width="${W}" height="${H}" fill="${C.ink}"/>`;
  s += dotsGrid(C.amber, 0.06);
  const kp = eoc(seg(t, 0.1, 0.6));
  s += `<g opacity="${kp}">${T(W / 2, 370, 'WE ARE', { size: 30, fill: C.coral, weight: 700, anchor: 'middle', family: MONO, ls: 14 })}</g>`;
  s += reveal(W / 2, 530, TEAM1, { t, start: 0.55, durd: 0.7, size: 132, fill: C.paper, weight: 900, family: FONT_BLACK });
  s += reveal(W / 2, 680, TEAM2, { t, start: 0.95, durd: 0.7, size: 132, fill: C.paper, weight: 900, family: FONT_BLACK });
  const rp = eoc(seg(t, 1.7, 2.3));
  if (rp > 0) s += `<rect x="${(W / 2 - 190 * rp).toFixed(0)}" y="728" width="${(380 * rp).toFixed(0)}" height="6" fill="${C.red}"/>`;
  s += T(W / 2, 810, Tx.s6_tag, { size: LANG === 'en' ? 34 : 42, fill: C.coral, weight: 700, anchor: 'middle', ls: 3, opacity: eoc(seg(t, 2.1, 2.7)) });
  s += `<g opacity="${eoc(seg(t, 2.5, 3.1)) * 0.95}">${logoMark(W / 2 - 105, 860, 210, true)}</g>`;
  return s;
}

const scenes = [
  { dur: 5.5, draw: s1, mode: 'dark' },
  { dur: 5.0, draw: s2, mode: 'light' },
  { dur: 5.0, draw: s3, mode: 'dark' },
  { dur: 5.5, draw: s4, mode: 'light' },
  { dur: 6.0, draw: s5, mode: 'accent' },
  { dur: 7.0, draw: s6, mode: 'dark' },
];
const TT = 0.5, starts = [];
{ let acc = 0; for (const sc of scenes) { starts.push(acc); acc += sc.dur - TT; } }
const TOTAL = starts[starts.length - 1] + scenes[scenes.length - 1].dur;

function sceneIdx(gt) { let i = 0; for (let k = 0; k < scenes.length; k++) if (gt >= starts[k]) i = k; return i; }
const fgFor = mode => (mode === 'dark' || mode === 'accent') ? C.white : C.ink;
const transTypes = ['slideleft', 'wipeup', 'slideup', 'slideleft', 'wipeup'];

function frame(gt) {
  const i = sceneIdx(gt), sc = scenes[i], ti = gt - starts[i];
  const body = sc.draw(ti, sc.dur);
  const nextStart = starts[i + 1];
  let blended;
  if (i + 1 < scenes.length && gt >= nextStart) {
    const p = clamp((gt - nextStart) / TT, 0, 1);
    const nBody = scenes[i + 1].draw(gt - nextStart, scenes[i + 1].dur);
    const type = transTypes[i];
    if (type === 'slideleft') blended = `<g transform="translate(${-p * W},0)">${body}</g><g transform="translate(${(1 - p) * W},0)">${nBody}</g>`;
    else if (type === 'slideup') blended = `<g transform="translate(0,${-p * H})">${body}</g><g transform="translate(0,${(1 - p) * H})">${nBody}</g>`;
    else { const cy = H * (1 - p); blended = `${body}<clipPath id="wi"><rect x="0" y="${cy}" width="${W}" height="${H - cy}"/></clipPath><g clip-path="url(#wi)">${nBody}</g>`; }
  } else blended = body;
  const mode = (i + 1 < scenes.length && gt >= nextStart && (gt - nextStart) / TT > 0.5) ? scenes[i + 1].mode : sc.mode;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${blended}${chrome(gt, fgFor(mode))}</svg>`;
}

// ---------- main ----------
const resvgOpts = { font: { fontFiles: FONT_FILES, loadSystemFonts: true, defaultFontFamily: FONT }, fitTo: { mode: 'width', value: W } };

if (args.frame !== undefined) {
  const svg = frame(parseFloat(args.frame));
  if (args.svg) fs.writeFileSync(args.svg, svg);
  fs.writeFileSync(args.out || '/tmp/motion_frame.png', new Resvg(svg, resvgOpts).render().asPng());
  console.log('frame ->', args.out || '/tmp/motion_frame.png');
} else {
  const outDir = args.out || '/workspace/ad_video/motion/frames';
  fs.mkdirSync(outDir, { recursive: true });
  const total = Math.round(TOTAL * FPS);
  const from = args.from ? parseInt(args.from, 10) : 0;
  const to = args.to ? Math.min(parseInt(args.to, 10), total) : total;
  console.log(`lang=${LANG} total=${TOTAL.toFixed(2)}s frames=${total} range=${from}-${to}`);
  for (let f = from; f < to; f++) {
    fs.writeFileSync(path.join(outDir, `f_${String(f).padStart(5, '0')}.png`), new Resvg(frame(f / FPS), resvgOpts).render().asPng());
  }
  console.log('done');
}