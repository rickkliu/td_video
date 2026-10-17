# BEA 广告视频项目工作日志

> 项目：东亚银行 Technology Division 广告视频制作
> 仓库：https://github.com/rickkliu/td_video
> 环境恢复方式：`git clone https://github.com/rickkliu/td_video /workspace/ad_video && cd /workspace/ad_video/motion && npm install && mkdir -p /usr/share/fonts/truetype/notocjk && cp ../assets/fonts/NotoSansTC-*.otf /usr/share/fonts/truetype/notocjk/`
> gh 凭据不在仓库内，新沙箱需重新 `gh auth login`（设备码模式）
> ⚠️ 沙箱可能被重建：/workspace 有快照恢复，但系统目录（字体、gh 凭据）会丢——字体已备份到 assets/fonts/，恢复命令见上

## 项目结构

```
ad_video/
├── assets/                  # BEA logo（白/彩色）、字幕文件
│   ├── endcard_trust.png    # 15s 人物宣传片的品牌落版贴片（RGBA）
│   └── fonts/               # Noto Sans TC 四字重备份（防沙箱重建丢字体）
├── clips/                   # 第一代广告的 6 段视频素材（41M）
├── motion/                  # 代码驱动渲染管线
│   ├── render.js            # 第一代：交易银行团队广告渲染器（zh/en）
│   ├── render_trust.js      # 第二代：TRUST 愿景广告渲染器（zh/en）
│   ├── render_endcard.js    # 落版贴片渲染器（720p，SVG→PNG）
│   ├── render_all_trust.sh  # 分块渲染脚本（规避 node 长进程 OOM）
│   ├── music*.py            # 全部 6 版配乐合成脚本（numpy 直接合成）
│   └── music*.wav           # 各版配乐成品（gitignore 之外，已入库）
├── BEA_TD_people_raw.mp4               # 第三代 AI 生成原始素材（含水印）
├── BEA_TechDiv_People_15s.mp4          # 第三代成品（去水印+配乐+落版）
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
  - **沙箱重建**（2026-10-17 实测）：/workspace 从旧快照恢复（本地 git 停在旧提交，需 `git pull --ff-only` 同步远端），系统目录全新——`/usr/share/fonts/truetype/notocjk/` 消失导致 resvg 渲染中文全部变豆腐块；gh 凭据失效需重新登录。字体现已备份至 `assets/fonts/`（来源：Google Fonts API 静态 TTF，家族名 "Noto Sans TC" 与脚本一致；注意 googlefonts/noto-cjk 仓库里是 "Noto Sans CJK TC"，家族名不同不能用）
  - AI 生成视频右下角有静态"AI生成"水印：多帧边缘检测取交集可精确定位（静态元素 vs 运动背景），ffmpeg `delogo` 去除

### 第三代：15 秒人物实景宣传片（2026-10-17）

- **需求**：有真实人物的 15 秒专业 TD 部门宣传片，与 TRUST campaign 保持视听一致
- **素材**：AI 视频生成（5 镜头：中环晨景 → 团队看板讨论 → 工程师编程 → 上线击掌 → 黄昏团队走向镜头），720p24，`BEA_TD_people_raw.mp4`
- **后期管线**（一次 ffmpeg 合成 → `BEA_TechDiv_People_15s.mp4`）：
  - 去水印：右下角"AI生成"静态徽章，用三帧边缘检测交集定位 bbox `x[1163-1251] y[663-691]`，`delogo=x=1150:y=650:w=118:h=50`
  - 配乐：复用 `music_trust.wav` 尾段 26.2–41.2s（渐进 → T-R-U-S-T 五连击 → F 大调落版全奏），与画面情绪弧线吻合
  - 落版：`render_endcard.js` 生成 720p RGBA 贴片（底部渐变 scrim + BEA logo + "TECHNOLOGY DIVISION · 科技部" + 您值得信賴的科技夥伴 + 五词页脚），11.6s 淡入
- **注意**：AI 生成内容含平台水印（原始素材未去除，保留在 raw 文件中）；对外发布请遵循所在机构对 AI 生成内容的披露要求

## 版本控制

- 仓库建于 2026-10-11（`838e563` 初始提交，含全部脚本/资产/音乐/成品视频）
- 排除：`motion/frames_*/`（152M 帧序列，脚本可再生）、`motion/node_modules/`
- 每次用户确认的迭代都会 commit + push

## 待办 / 下一步候选

- [ ] （无进行中任务——按需添加）
