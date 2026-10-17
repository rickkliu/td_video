// Lower-third end card for the 15s TD people promo — mirrors the TRUST ad sign-off:
// BEA logo + "TECHNOLOGY DIVISION · 科技部" + partner tagline + five-word footer.
const fs = require('fs');
const { Resvg } = require('@resvg/resvg-js');

const W = 1280, H = 720; // matches the 720p generated footage
const LOGO_COLOR = 'data:image/png;base64,' +
  fs.readFileSync('/workspace/ad_video/assets/bea_logo_color.png').toString('base64');
const FONT_FILES = [
  '/usr/share/fonts/truetype/notocjk/NotoSansTC-Regular.otf',
  '/usr/share/fonts/truetype/notocjk/NotoSansTC-Medium.otf',
  '/usr/share/fonts/truetype/notocjk/NotoSansTC-Bold.otf',
  '/usr/share/fonts/truetype/notocjk/NotoSansTC-Black.otf',
  '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
  '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
];

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <defs>
    <linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#140B08" stop-opacity="0"/>
      <stop offset="0.42" stop-color="#140B08" stop-opacity="0.38"/>
      <stop offset="1" stop-color="#140B08" stop-opacity="0.94"/>
    </linearGradient>
  </defs>
  <rect x="0" y="430" width="${W}" height="290" fill="url(#scrim)"/>
  <image href="${LOGO_COLOR}" x="535" y="498" width="210" height="41"/>
  <rect x="618" y="560" width="44" height="3" fill="#EA4120"/>
  <text x="640" y="607" text-anchor="middle" font-family="Noto Sans TC" font-weight="700" font-size="30" fill="#FFF6F1">TECHNOLOGY DIVISION · 科技部</text>
  <text x="640" y="641" text-anchor="middle" font-family="Noto Sans TC" font-weight="500" font-size="19" fill="#F49F8F" letter-spacing="2">您值得信賴的科技夥伴</text>
  <text x="640" y="676" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="12" fill="#FFA901" fill-opacity="0.95" letter-spacing="2.5">TRUSTED · RESILIENT · UNITED · SMART · TRANSFORMATIVE</text>
</svg>`;

fs.writeFileSync(
  '/workspace/ad_video/assets/endcard_trust.png',
  new Resvg(svg, { font: { fontFiles: FONT_FILES, loadSystemFonts: true, defaultFontFamily: 'Noto Sans TC' }, fitTo: { mode: 'width', value: W } }).render().asPng()
);
console.log('endcard -> assets/endcard_trust.png');
