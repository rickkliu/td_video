# BEA 广告视频项目工作日志

> 项目：东亚银行 Technology Division 广告视频制作
> 仓库：https://github.com/rickkliu/td_video
> 环境恢复方式：`git clone https://github.com/rickkliu/td_video /workspace/ad_video && cd /workspace/ad_video/motion && npm install`
> gh 凭据不在仓库内，新沙箱需重新 `gh auth login`（设备码模式）

## 项目结构

```
ad_video/
├── assets/                  # BEA logo（白/彩色）、字幕文件
├── clips/                   # 第一代广告的 6 段视频素材（41M）
├── motion/                  # 代码驱动渲染管线
│   ├── render.js            # 第一代：交易银行团队广告渲染器（zh/en）
│   ├── render_trust.js      # 第二代：TRUST 愿景广告渲染器（zh/en）
│   ├── render_all_trust.sh  # 分块渲染脚本（规避 node 长进程 OOM）
│   ├── music*.py            # 全部 6 版配乐合成脚本（numpy 直接合成）
│   └── music*.wav           # 各版配乐成品（gitignore 之外，已入库）
├── BEA_TxnBanking_Brand_zh/en.mp4      # 第一代成品（zh/en）
├── BEA_TechDiv_TRUST_zh/en.mp4         # 第二代 TRUST 成品（zh/en）
├── BEA_TransactionBanking_Ad.mp4       # 最早版本（素材剪辑流水线）
└── build.sh                 # 早期 ffmpeg 剪辑合成脚本
```

## 迭代历史

### 第一代：Transaction Banking Applications Team 广告

- **v0**（`BEA_TransactionBanking_Ad.mp4`，`build.sh`）：素材剪辑 + 字幕 + xfade 流水线
- **v1**（`render.js`）：改为代码驱动动态图形——SVG → Resvg → PNG 帧 → ffmpeg
  - 6 幕结构：数位浪潮 → 实力数据（$1.28B / 99.99% / <180ms）→ 产品全景（支付/现金管理/贸易融资）→ 核心系统 → 承诺 → 品牌落版
  - 视觉：BEA 朱红 #EA4120 派生色板、暖色中性色、studio chrome HUD（十字准星、时间码、章节标签）
- **配乐迭代**（用户逐版反馈驱动）：
  1. `music_house.py` — tech-house，被否（"有点土"）
  2. `music_trap.py` — 808 trap，节奏感不足
  3. `music_cinematic.py` — 事件驱动电影感
  4. `music_deephouse.py` — 极简 deep house，"不够宏大"
  5. `music.py`（v9）— **最终版**：渐进式管弦编排（弦乐/太鼓/定音鼓/铜管/竖琴），单一贯穿主题 ✅
- **bug 修复**：修复"支付"关键词闪现两次；"以科技为翼"斜杠呈现改为更有节奏感的方式
- **增强**：加入 line chart 动画展示交易量上升趋势

### 第二代：Technology Division TRUST 愿景广告（当前主线）

- **需求**：参考 Nike "Running Isn't Just Running"（YouTube: uXlWYZ022zU）
- **结构**（41.2s，120 BPM，帧级音画同步）：
  1. 钩子 0–5.2s：TECHNOLOGY / ISN'T JUST / TECHNOLOGY.（科技/不只是/科技。）三连硬切，末拍翻红底
  2. 转折 5.2–8.8s：IT'S → **TRUST.** 字母逐个砸落
  3. 五字母 8.8–29.6s：**T**RUSTED / **R**ESILIENT / **U**NITED / **S**MART / **T**RANSFORMATIVE，每字母一景（巨字砸落 + 中英文 + TRUST 进度条点亮）
  4. 蒙太奇 29.6–33.7s：T-R-U-S-T 五连击（每半拍一击）+ 琥珀色锁定条
  5. 落版 33.7–41.2s：TECHNOLOGY DIVISION · 科技部 + "您值得信賴的科技夥伴" + 五词页脚 + logo
- **配乐**（`music_trust.py`）：心跳低频 → 三次鼓击钩子 → TRUST 全奏 → 字母段根音上行（Fm→Ab→Cm→Eb→Fm）配器逐层加厚 → F 大调全奏落版；25 个音乐事件与视觉砸落误差 <1 帧
- **踩坑记录**：
  - Resvg 不支持 `transform-origin` → 移除所有该声明，手动计算变换中心
  - node 长进程内存累积 → 渲染被 OOM kill（exit 137）→ 改用 `render_all_trust.sh` 每 80 帧重启进程
  - CJK + Latin 混排对齐 → 显式计算组合宽度居中

## 版本控制

- 仓库建于 2026-10-11（`838e563` 初始提交，含全部脚本/资产/音乐/成品视频）
- 排除：`motion/frames_*/`（152M 帧序列，脚本可再生）、`motion/node_modules/`
- 每次用户确认的迭代都会 commit + push

## 待办 / 下一步候选

- [ ] （无进行中任务——按需添加）
