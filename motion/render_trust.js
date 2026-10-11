// BEA Technology Division — TRUST vision ad.
// Structure inspired by Nike "Running Isn't Just Running":
// hook question -> turn -> five letter scenes (TRUST acronym) -> letter montage -> sign-off.
// Style: hard-cut kinetic typography, brand palette, studio chrome.
const fs = require('fs');
const path = require('path');
const { Resvg } = require('@resvg/resvg-js');

const W = 1920, H = 1080, FPS = 30;
const args = Object.fromEntries(process.argv.slice(2).map(a => a.split('=')));
const LANG = (args.lang || 'en').toLowerCase();

const C = {
  ink: '#1C100C', ink2: '#2B1A14', paper: '#FFF6F1', blush: '#FCE6E1',
  red: '#EA4120', redD: '#B62E14', redDeep: '#7A1E0B', coral: '#F49F8F',
  amber: '#FFA901', orange: '#F66E0E', white: '#FFFFFF', muted: '#8A6F66',
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
const BPM = 120;

// ---------- copy ----------
const TEXT = {
  zh: {
    hook1: '科技', hook2: '不只是', hook3: '科技。',
    turnA: '它是', turnB: 'TRUST.', turnEyebrow: '我們的新願景',
    letters: [
      { L: 'T', en: 'TRUSTED', zh: '值得信賴', ph: '可以放心託付的科技夥伴' },
      { L: 'R', en: 'RESILIENT', zh: '堅韌可靠', ph: '7×24 全天候，穩定運行' },
      { L: 'U', en: 'UNITED', zh: '團結一致', ph: '一個團隊，一個使命' },
      { L: 'S', en: 'SMART', zh: '智慧敏捷', ph: '數據驅動每個決策' },
      { L: 'T', en: 'TRANSFORMATIVE', zh: '變革創新', ph: '重新定義無限可能' },
    ],
    divZh: '科技部', divEn: 'TECHNOLOGY DIVISION',
    partner: '您值得信賴的科技夥伴',
    footerWords: 'TRUSTED · RESILIENT · UNITED · SMART · TRANSFORMATIVE',
    chapters: ['提問', '答案', 'TRUSTED', 'RESILIENT', 'UNITED', 'SMART', 'TRANSFORMATIVE', 'TRUST', '落版'],
  },
  en: {
    hook1: 'TECHNOLOGY', hook2: "ISN'T JUST", hook3: 'TECHNOLOGY.',
    turnA: "IT'S", turnB: 'TRUST.', turnEyebrow: 'OUR NEW VISION',
    letters: [
      { L: 'T', en: 'TRUSTED', zh: '', ph: 'The partner you can bank on.' },
      { L: 'R', en: 'RESILIENT', zh: '', ph: 'Always on. Every single day.' },
      { L: 'U', en: 'UNITED', zh: '', ph: 'One team. One mission.' },
      { L: 'S', en: 'SMART', zh: '', ph: 'Every decision, data-driven.' },
      { L: 'T', en: 'TRANSFORMATIVE', zh: '', ph: 'Reimagining what\u2019s possible.' },
    ],
    divZh: '', divEn: 'TECHNOLOGY DIVISION',
    partner: 'Your trusted technology partner.',
    footerWords: 'TRUSTED · RESILIENT · UNITED · SMART · TRANSFORMATIVE',
    chapters: ['THE QUESTION', 'THE ANSWER', 'TRUSTED', 'RESILIENT', 'UNITED', 'SMART', 'TRANSFORMATIVE', 'TRUST', 'SIGN-OFF'],
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
    else if ('-–—·×'.includes(ch)) s += 0.42;
    else s += 0.55;
  }
  return s;
}
const estW = (str, size) => estEm(str) * size;
const fitSize = (str, maxW, base) => Math.min(base, maxW / Math.max(estEm(str), 0.001));
const isCJK = str => /[\u4E00-\u9FFF]/.test(str);

function dotsGrid(fill, op, step = 72) {
  let s = '';
  for (let x = step; x < W; x += step) for (let y = step; y < H; y += step)
    s += `<circle cx="${x}" cy="${y}" r="2" fill="${fill}" opacity="${op}"/>`;
  return s;
}

// CJK per-character stagger
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
// latin mask reveal
function reveal(cx, baseY, str, o = {}) {
  const { size = 120, fill = C.ink, weight = 900, family = FONT_BLACK, t = 0, start = 0, durd = 0.7 } = o;
  const wd = estW(str, size), x0 = cx - wd / 2;
  const prog = eoc(seg(t, start, start + durd));
  const id = 'rv' + Math.random().toString(36).slice(2, 8);
  return `<clipPath id="${id}"><rect x="${x0 - 24}" y="${baseY - size}" width="${prog * (wd + 48)}" height="${size * 1.5}"/></clipPath>
    <g clip-path="url(#${id})">${T(cx, baseY, str, { size, fill, weight, anchor: 'middle', family })}</g>`;
}
function headline(cx, baseY, str, o = {}) {
  const maxW = (o.maxW || (W - 2 * 150));
  const base = o.size || 150;
  const size = fitSize(str, maxW, base);
  const common = { ...o, size };
  return isCJK(str) ? stagger(cx, baseY, str, common) : reveal(cx, baseY, str, common);
}

function beatPulse(gt, bpm = BPM) {
  const phase = ((gt * bpm / 60) % 1 + 1) % 1;
  return Math.pow(1 - phase, 3);
}
function logoMark(x, y, w) {
  return `<image href="${LOGO_WHITE}" x="${x}" y="${y}" width="${w}" height="${(w * 47 / 242).toFixed(1)}"/>`;
}

// ---------- studio chrome ----------
function chrome(gt, fg) {
  const pad = 56, pulse = beatPulse(gt);
  const br = rgba(fg, 0.32 + 0.38 * pulse);
  const tcol = rgba(fg, 0.62);
  const CR = 15;
  const cross = (x, y) => `<path d="M ${x - CR} ${y} L ${x + CR} ${y} M ${x} ${y - CR} L ${x} ${y + CR}" stroke="${br}" stroke-width="2.5"/>`;
  let s = cross(pad, pad) + cross(W - pad, pad) + cross(pad, H - pad) + cross(W - pad, H - pad);
  const label = 'BEA · TECHNOLOGY DIVISION';
  s += `<g>
    <circle cx="${pad + 34}" cy="${pad + 1}" r="${5 + 5 * pulse}" fill="${rgba(C.red, 0.35)}"/>
    <circle cx="${pad + 34}" cy="${pad + 1}" r="5" fill="${C.red}"/>
    ${T(pad + 52, pad + 8, label, { size: 22, fill: tcol, weight: 700, family: MONO, ls: 3 })}
  </g>`;
  const tc = 'T+' + gt.toFixed(3).padStart(6, '0') + 's';
  s += T(W - pad - 30, pad + 8, tc, { size: 22, fill: tcol, weight: 700, anchor: 'end', family: MONO, ls: 2 });
  const i = sceneIdx(gt);
  s += T(pad + 30, H - pad + 8, String(i + 1).padStart(2, '0') + ' / 09 — ' + Tx.chapters[i], { size: 22, fill: rgba(fg, 0.82), weight: 700, family: LANG === 'zh' && isCJK(Tx.chapters[i]) ? FONT : MONO, ls: 3 });
  s += T(W - pad - 30, H - pad + 8, `1920\u00d71080 · 30 FPS · ${BPM} BPM`, { size: 22, fill: tcol, weight: 700, anchor: 'end', family: MONO, ls: 2 });
  return s;
}

// ---------- shared pieces ----------
// giant letter slam (instant on + overshoot settle)
function letterSlam(cx, baseY, ch, size, fill, t0, t, accent) {
  const p = seg(t, t0, t0 + 0.18);
  if (p <= 0) return '';
  const sc = 1.12 - 0.12 * eob(p);
  const bar = eoc(seg(t, t0 - 0.12, t0 + 0.22));  // underline sweep just before
  const bw = estW(ch, size) + 120;
  return `<g>
    ${accent ? `<rect x="${cx - bw / 2}" y="${baseY + 36}" width="${bar * bw}" height="14" fill="${accent}"/>` : ''}
    <g transform="translate(${cx},${baseY}) scale(${sc})">
      ${T(0, 0, ch, { size, fill, weight: 900, family: FONT_BLACK, anchor: 'middle' })}
    </g>
  </g>`;
}

// scrolling word strip (editorial texture behind)
function wordStrip(word, y, t, col, op = 0.07) {
  const size = 150, gap = 120;
  const unit = estW(word + ' ', size) + gap;
  const off = ((t * 260) % unit);
  let s = '';
  for (let k = -1; k * unit - off < W + unit; k++) {
    s += T(k * unit - off, y, word, { size, fill: col, weight: 900, family: FONT_BLACK, ls: 4 });
  }
  return `<g opacity="${op}">${s}</g>`;
}

// TRUST progress indicator (five letters)
function trustProgress(t, upto, fg, accent) {
  const letters = ['T', 'R', 'U', 'S', 'T'];
  const cw = 64, gap = 26, x0 = W / 2 - (5 * cw + 4 * gap) / 2, y = 962;
  let s = `<line x1="${x0 - 60}" y1="${y + cw / 2}" x2="${x0 - 24}" y2="${y + cw / 2}" stroke="${rgba(fg, 0.35)}" stroke-width="2"/>`;
  s += `<line x1="${x0 + 5 * cw + 4 * gap + 24}" y1="${y + cw / 2}" x2="${x0 + 5 * cw + 4 * gap + 60}" y2="${y + cw / 2}" stroke="${rgba(fg, 0.35)}" stroke-width="2"/>`;
  letters.forEach((ch, i) => {
    const x = x0 + i * (cw + gap);
    const on = i < upto;
    const cur = i === upto - 1;
    const pulse = cur ? beatPulse(t) : 0;
    s += `<g>
      <rect x="${x}" y="${y}" width="${cw}" height="${cw}" rx="10" fill="${on ? accent : 'none'}" stroke="${on ? accent : rgba(fg, 0.4)}" stroke-width="${cur ? 4 + 2 * pulse : 3}"/>
      ${T(x + cw / 2, y + cw / 2 + 15, ch, { size: 34, fill: on ? (i === 4 && accent === C.orange ? C.ink : C.paper) : rgba(fg, 0.55), weight: 900, anchor: 'middle', family: FONT_BLACK })}
    </g>`;
  });
  return s;
}

// ---------- scenes ----------
// S1 hook: TECHNOLOGY / ISN'T JUST / TECHNOLOGY. (hard cuts)
function sHook(t) {
  let s = '';
  if (t < 2.5) {           // TECHNOLOGY (dark)
    s += `<rect width="${W}" height="${H}" fill="${C.ink}"/>` + dotsGrid(C.amber, 0.05);
    s += headline(W / 2, 590, Tx.hook1, { t, size: 230, fill: C.paper, start: 1.0, durd: 0.35, maxW: W - 200 });
    const p = eoc(seg(t, 1.5, 2.0));
    s += `<rect x="${W / 2 - 60 * p}" y="${660}" width="${120 * p}" height="10" fill="${C.red}"/>`;
  } else if (t < 4.0) {    // ISN'T JUST (paper)
    s += `<rect width="${W}" height="${H}" fill="${C.paper}"/>` + dotsGrid(C.ink, 0.05);
    s += headline(W / 2, 590, Tx.hook2, { t, size: 230, fill: C.ink, start: 2.5, durd: 0.35, maxW: W - 200 });
  } else {                 // TECHNOLOGY. (brand red — the Nike flip)
    s += `<rect width="${W}" height="${H}" fill="${C.red}"/>`;
    s += headline(W / 2, 590, Tx.hook3, { t, size: 230, fill: C.paper, start: 4.0, durd: 0.35, maxW: W - 200 });
  }
  return s;
}

// S2 turn: IT'S -> TRUST.
function sTurn(t) {
  let s = `<rect width="${W}" height="${H}" fill="${C.paper}"/>` + dotsGrid(C.ink, 0.05);
  s += stagger(W / 2, 420, Tx.turnA, { t, size: 100, fill: rgba(C.ink, 0.8), start: 0.5, stag: 0.06, rise: 40, durd: 0.4 });
  // TRUST. letters slam one by one
  const chars = [...Tx.turnB];
  const size = 300, x0 = W / 2 - estW(Tx.turnB, size) / 2;
  let acc = 0;
  chars.forEach((ch, i) => {
    acc += estW(ch, size);
    const cx = x0 + acc - estW(ch, size) / 2;
    const t0 = 1.0 + i * 0.07;
    const p = seg(t, t0, t0 + 0.16);
    if (p > 0) {
      const sc = 1.14 - 0.14 * eob(p);
      const isDot = ch === '.';
      s += `<g transform="translate(${cx},700) scale(${sc})">
        ${T(0, 0, ch, { size, fill: isDot ? C.red : C.ink, weight: 900, family: FONT_BLACK, anchor: 'middle' })}
      </g>`;
    }
  });
  const eb = eoc(seg(t, 1.9, 2.4));
  s += `<g opacity="${eb}">
    <circle cx="${W / 2 - estW(Tx.turnEyebrow, 26) / 2 - 28}" cy="${800}" r="7" fill="${C.red}"/>
    ${T(W / 2, 808, Tx.turnEyebrow, { size: 26, fill: C.muted, weight: 700, anchor: 'middle', family: LANG === 'zh' ? FONT : MONO, ls: 6 })}
  </g>`;
  return s;
}

// S3-S7 letter scenes
function letterScene(t, idx, bg, fg, accent, stripCol) {
  const L = Tx.letters[idx];
  const tSlam = 0.5;
  let s = `<rect width="${W}" height="${H}" fill="${bg}"/>`;
  s += dotsGrid(bg === C.paper || bg === C.orange ? C.ink : C.amber, 0.05);
  s += wordStrip(L.en, 520, t, stripCol, 0.06);
  // giant letter
  s += letterSlam(W / 2, 590, L.L, 660, fg, tSlam, t, accent);
  // word (zh: chinese big + latin small; en: latin big)
  const wordY = 812;
  if (LANG === 'zh') {
    const zhW = estEm(L.zh) * 108, tagW = estW(L.en, 40);
    const totalW = zhW + 44 + tagW;
    const zx = W / 2 - totalW / 2 + zhW / 2;
    s += stagger(zx, wordY, L.zh, { t, size: 108, fill: fg, start: tSlam + 0.45, stag: 0.07, rise: 46, durd: 0.45 });
    s += `<g opacity="${eoc(seg(t, tSlam + 0.75, tSlam + 1.05))}">${T(W / 2 - totalW / 2 + zhW + 44 + tagW / 2, wordY - 6, L.en, { size: 40, fill: accent, weight: 900, anchor: 'middle', family: FONT_BLACK, ls: 3 })}</g>`;
  } else {
    s += reveal(W / 2, wordY, L.en, { t, size: fitSize(L.en, W - 400, 120), fill: fg, start: tSlam + 0.45, durd: 0.5 });
  }
  // phrase
  const ph = eoc(seg(t, tSlam + 1.05, tSlam + 1.45));
  s += `<g opacity="${ph}" transform="translate(0,${(1 - ph) * 22})">
    ${T(W / 2, 892, L.ph, { size: 42, fill: rgba(fg, 0.75), weight: 500, anchor: 'middle', family: FONT })}
  </g>`;
  s += trustProgress(t, idx + 1, fg, accent === C.ink ? C.red : accent);
  return s;
}
const sT1 = t => letterScene(t, 0, C.ink, C.paper, C.amber, C.paper);
const sR = t => letterScene(t, 1, C.paper, C.ink, C.red, C.ink);
const sU = t => letterScene(t, 2, C.orange, C.ink, C.ink, C.ink);
const sS = t => letterScene(t, 3, C.paper, C.ink, C.red, C.ink);
const sT2 = t => letterScene(t, 4, C.ink, C.paper, C.red, C.paper);

// S8 montage: T-R-U-S-T letters slam on consecutive beats, then the word locks
function sMontage(t) {
  let s = `<rect width="${W}" height="${H}" fill="${C.redDeep}"/>`;
  s += `<rect width="${W}" height="${H}" fill="${C.red}" opacity="${0.18 + 0.10 * beatPulse(t)}"/>`;
  s += dotsGrid(C.paper, 0.06);
  const letters = ['T', 'R', 'U', 'S', 'T'];
  const size = 400, cx0 = W / 2 - 2 * 340;
  letters.forEach((ch, i) => {
    const t0 = 0.5 + i * 0.5;
    const p = seg(t, t0, t0 + 0.16);
    if (p > 0) {
      const sc = 1.18 - 0.18 * eob(p);
      s += `<g transform="translate(${cx0 + i * 340},${600}) scale(${sc})">
        ${T(0, 0, ch, { size, fill: C.paper, weight: 900, family: FONT_BLACK, anchor: 'middle' })}
      </g>`;
    }
  });
  // word lock + label
  const lock = eoc(seg(t, 3.1, 3.5));
  if (lock > 0) {
    const sc = 1.06 - 0.06 * lock;
    s += `<g opacity="${lock}">
      <rect x="${W / 2 - 520 * lock}" y="${720}" width="${1040 * lock}" height="12" fill="${C.amber}"/>
      ${T(W / 2, 830, 'T · R · U · S · T', { size: 54, fill: C.amber, weight: 900, anchor: 'middle', family: MONO, ls: 14 })}
    </g>`;
  }
  return s;
}

// S9 sign-off
function sEnd(t) {
  let s = `<rect width="${W}" height="${H}" fill="${C.ink}"/>` + dotsGrid(C.amber, 0.05);
  const t0 = 0.5;
  if (LANG === 'zh') {
    s += stagger(W / 2, 470, Tx.divZh, { t, size: 190, fill: C.paper, start: t0, stag: 0.09, rise: 60, durd: 0.5 });
    s += `<g opacity="${eoc(seg(t, t0 + 0.5, t0 + 0.9))}">${T(W / 2, 570, Tx.divEn, { size: 58, fill: C.red, weight: 900, anchor: 'middle', family: FONT_BLACK, ls: 10 })}</g>`;
  } else {
    s += reveal(W / 2, 520, Tx.divEn, { t, size: fitSize(Tx.divEn, W - 260, 165), fill: C.paper, start: t0, durd: 0.55 });
  }
  const pp = eoc(seg(t, 1.5, 2.0));
  s += `<g opacity="${pp}" transform="translate(0,${(1 - pp) * 26})">
    ${T(W / 2, 660, Tx.partner, { size: 46, fill: rgba(C.paper, 0.85), weight: 500, anchor: 'middle' })}
  </g>`;
  const ul = eoc(seg(t, 2.5, 3.0));
  s += `<rect x="${W / 2 - 330 * ul}" y="${700}" width="${660 * ul}" height="12" fill="${C.red}"/>`;
  const fw = eoc(seg(t, 3.1, 3.6));
  s += `<g opacity="${fw}">${T(W / 2, 790, Tx.footerWords, { size: 28, fill: C.amber, weight: 700, anchor: 'middle', family: MONO, ls: 4 })}</g>`;
  const lg = eoc(seg(t, 4.0, 4.5));
  s += `<g opacity="${lg}">
    ${logoMark(W / 2 - 170, 880, 340)}
  </g>`;
  // final fade
  const fd = clamp((t - 6.0) / 1.0, 0, 1);
  if (fd > 0) s += `<rect width="${W}" height="${H}" fill="${C.ink}" opacity="${fd}"/>`;
  return s;
}

// ---------- timeline ----------
const scenes = [
  { dur: 5.5, draw: sHook, mode: 'dark' },     // 0.0  hook
  { dur: 4.0, draw: sTurn, mode: 'light' },    // 5.0  turn
  { dur: 4.5, draw: sT1, mode: 'dark' },       // 8.5  T TRUSTED
  { dur: 4.5, draw: sR, mode: 'light' },       // 12.5 R RESILIENT
  { dur: 4.5, draw: sU, mode: 'accent' },      // 16.5 U UNITED
  { dur: 4.5, draw: sS, mode: 'light' },       // 20.5 S SMART
  { dur: 4.5, draw: sT2, mode: 'dark' },       // 24.5 T TRANSFORMATIVE
  { dur: 4.5, draw: sMontage, mode: 'dark' },  // 28.5 TRUST montage
  { dur: 7.5, draw: sEnd, mode: 'dark' },      // 32.5 sign-off -> 40.0
];
const TT = 0.35, starts = [];
{ let acc = 0; for (const sc of scenes) { starts.push(acc); acc += sc.dur - TT; } }
const TOTAL = starts[starts.length - 1] + scenes[scenes.length - 1].dur;

function sceneIdx(gt) { let i = 0; for (let k = 0; k < scenes.length; k++) if (gt >= starts[k]) i = k; return i; }
const fgFor = mode => (mode === 'dark' || mode === 'accent') ? C.white : C.ink;
const transTypes = ['slideleft', 'wipeup', 'slideleft', 'wipeup', 'slideleft', 'wipeup', 'wipeup', 'slideleft'];

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
  fs.writeFileSync(args.out || '/tmp/trust_frame.png', new Resvg(svg, resvgOpts).render().asPng());
  console.log('frame ->', args.out || '/tmp/trust_frame.png');
} else {
  const outDir = args.out || `/workspace/ad_video/motion/frames_trust_${LANG}`;
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
