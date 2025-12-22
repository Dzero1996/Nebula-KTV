# Requirements Document

## Introduction

Nebula KTV (星云 KTV) 是一套部署在家用 NAS 上的私有化车载 KTV 系统。系统通过 AI 流水线自动处理视频文件，分离人声/伴奏、生成歌词，并通过 Web 播放器在极氪车机浏览器上提供沉浸式 K 歌体验。

核心价值：
- **私有化**：数据完全自主，不受版权下架影响
- **AI 驱动**：自动分离音轨、生成歌词
- **车载优先**：大触控区、极简交互、防误触设计

## Glossary

- **Nebula Engine**: 运行在 NAS Docker 容器中的 AI 处理流水线
- **Source Crossfade**: 原唱/伴奏音轨的交叉渐变切换技术
- **UVR5**: Ultimate Vocal Remover 5，AI 人声分离模型
- **Whisper**: OpenAI 的语音识别模型，用于生成歌词
- **8155 芯片**: 极氪车机搭载的高通骁龙 8155 处理器
- **Immersive Mode**: 沉浸模式，无 UI 遮挡的纯 K 歌体验
- **Interactive Mode**: 交互模式，显示控制栏的操作界面
- **Media Asset**: 媒体资产，包括视频、原唱音轨、伴奏音轨、歌词文件

## Requirements

### Requirement 1: 歌曲元数据管理

**User Story:** As a 用户, I want 系统自动提取和管理歌曲的完整元数据, so that 我可以通过多种方式快速找到想唱的歌。

#### Acceptance Criteria

1. WHEN 一个视频文件被添加到系统 THEN Nebula Engine SHALL 提取并存储歌曲的基础信息（标题、歌手、时长）
2. WHEN 歌曲元数据被存储 THEN Nebula Engine SHALL 生成拼音首字母索引（title_abbr, artist_abbr）用于快速搜索
3. WHEN 用户查询歌曲列表 THEN Web Player SHALL 返回包含标题、歌手、状态、封面的完整信息
4. WHEN 歌曲处理状态变更 THEN Nebula Engine SHALL 更新 status 字段为 PENDING、PROCESSING、READY、PARTIAL 或 FAILED

### Requirement 2: AI 音频处理流水线

**User Story:** As a 用户, I want 系统自动将视频文件处理成可唱的 KTV 资源, so that 我不需要手动分离伴奏或制作歌词。

#### Acceptance Criteria

1. WHEN 新视频文件被检测到 THEN Nebula Engine SHALL 自动触发 AI 处理任务
2. WHEN AI 处理任务启动 THEN Nebula Engine SHALL 使用 UVR5 分离出人声轨道和伴奏轨道
3. WHEN 人声轨道分离完成 THEN Nebula Engine SHALL 使用 Whisper 生成时间轴对齐的歌词
4. WHEN 所有处理步骤完成 THEN Nebula Engine SHALL 将歌曲状态更新为 READY
5. IF 任一处理步骤失败 THEN Nebula Engine SHALL 将歌曲状态标记为 FAILED 并记录错误信息

### Requirement 3: 首页资源库界面

**User Story:** As a 车机用户, I want 在首页快速浏览和搜索歌曲, so that 我可以一键找到并播放想唱的歌。

#### Acceptance Criteria

1. WHEN 用户进入首页 THEN Web Player SHALL 显示全局搜索框（高度大于 60px）
2. WHEN 用户在搜索框输入文字 THEN Web Player SHALL 支持按歌名或歌手名模糊搜索
3. WHEN 首页加载完成 THEN Web Player SHALL 显示"最近添加"横向滚动区域
4. WHEN 首页加载完成 THEN Web Player SHALL 显示全部歌曲列表（列表项高度大于 100px）
5. WHEN 歌曲状态为 PROCESSING THEN Web Player SHALL 将该歌曲卡片置灰并显示处理中标签
6. WHEN 用户点击处理中的歌曲 THEN Web Player SHALL 显示 Toast 提示"AI 正在加工中，请稍候..."

### Requirement 4: 沉浸播放模式

**User Story:** As a K 歌用户, I want 在唱歌时看到全屏 MV 和大字歌词, so that 我可以专注于 K 歌体验而不被 UI 干扰。

#### Acceptance Criteria

1. WHEN 用户无操作超过 5 秒 THEN Web Player SHALL 自动进入沉浸模式
2. WHILE 处于沉浸模式 THEN Web Player SHALL 全屏显示 MV 视频画面
3. WHILE 处于沉浸模式 THEN Web Player SHALL 在屏幕下方 20% 区域显示歌词
4. WHEN 显示歌词 THEN Web Player SHALL 以 48px 以上字号高亮显示当前句
5. WHEN 显示歌词 THEN Web Player SHALL 以较小字号半透明显示下一句

### Requirement 5: 交互播放模式

**User Story:** As a 用户, I want 通过简单的触控操作控制播放, so that 我可以在驾驶时安全地切换原唱/伴奏或切歌。

#### Acceptance Criteria

1. WHEN 用户点击屏幕任意位置 THEN Web Player SHALL 从沉浸模式切换到交互模式
2. WHEN 进入交互模式 THEN Web Player SHALL 显示顶部遮罩（返回按钮、歌曲标题）
3. WHEN 进入交互模式 THEN Web Player SHALL 显示底部控制栏（高度至少占屏幕 25%）
4. WHEN 显示底部控制栏 THEN Web Player SHALL 包含进度条、原唱/伴奏开关、播放/暂停按钮、下一首按钮
5. WHEN 交互模式显示超过 5 秒且用户无操作 THEN Web Player SHALL 自动返回沉浸模式
6. WHILE 用户正在拖拽进度条 THEN Web Player SHALL 暂停自动隐藏倒计时

### Requirement 6: 音频播放与切换

**User Story:** As a K 歌用户, I want 在原唱和伴奏之间平滑切换, so that 我可以根据需要选择跟唱或独唱模式。

#### Acceptance Criteria

1. WHEN 播放器加载歌曲 THEN Web Player SHALL 同时加载视频、原唱音轨、伴奏音轨三个媒体源
2. WHEN 三个媒体源全部就绪 THEN Web Player SHALL 开始同步播放
3. IF 任一媒体源正在缓冲 THEN Web Player SHALL 显示 Loading 动画并暂停所有轨道
4. WHEN 用户点击原唱/伴奏开关 THEN Web Player SHALL 执行 500ms 交叉渐变切换
5. IF 伴奏音轨加载失败 THEN Web Player SHALL 自动降级为仅原唱模式并禁用切换开关

### Requirement 7: 触控反馈设计

**User Story:** As a 车机用户, I want 按钮有明显的视觉反馈, so that 我在没有震动反馈的情况下也能确认操作成功。

#### Acceptance Criteria

1. WHEN 用户按下任意按钮 THEN Web Player SHALL 显示明显的变色或缩放效果
2. WHEN 按钮处于激活状态 THEN Web Player SHALL 保持视觉反馈直到用户松开
3. WHEN 设计按钮尺寸 THEN Web Player SHALL 确保所有可点击区域大于 60px

### Requirement 8: 数据持久化

**User Story:** As a 系统管理员, I want 所有数据安全存储在 PostgreSQL 中, so that 系统重启后数据不会丢失。

#### Acceptance Criteria

1. WHEN 歌曲信息被创建或更新 THEN Nebula Engine SHALL 持久化到 PostgreSQL 数据库
2. WHEN 媒体资产被处理完成 THEN Nebula Engine SHALL 在 media_assets 表中记录文件路径和类型
3. WHEN 查询歌曲数据 THEN Nebula Engine SHALL 支持通过 JSONB 字段进行扩展属性筛选

### Requirement 9: 媒体流服务

**User Story:** As a Web 播放器, I want 通过 HTTP Range Requests 获取媒体流, so that 用户可以快速跳转到任意播放位置。

#### Acceptance Criteria

1. WHEN 请求媒体资产 THEN Nebula Engine SHALL 支持 HTTP Range Requests 协议
2. WHEN 提供视频流 THEN Nebula Engine SHALL 返回正确的 Content-Type 和 Content-Range 头
3. WHEN 提供音频流 THEN Nebula Engine SHALL 支持 MP3 和 WAV 格式的流式传输
