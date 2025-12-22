<p align="center">
  <img src="docs/logo.png" alt="Nebula KTV Logo" width="120" />
</p>

<h1 align="center">🌌 Nebula KTV 星云 KTV</h1>

<p align="center">
  <strong>AI 驱动的私有化车载 KTV 系统</strong>
</p>

<p align="center">
  <a href="#-特性亮点">特性</a> •
  <a href="#-系统架构">架构</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-技术栈">技术栈</a> •
  <a href="#-api-文档">API</a> •
  <a href="#-开发指南">开发</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Next.js-14-black?logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License" />
</p>

---

## 📖 项目简介

**Nebula KTV** 是一套部署在家用 NAS 上的私有化车载 KTV 系统。通过 AI 流水线自动处理视频文件，分离人声/伴奏、生成歌词，并通过 Web 播放器在车机浏览器上提供沉浸式 K 歌体验。

> 🎯 **设计目标**：为极氪等智能汽车打造专属的车载 K 歌体验，大触控区设计，驾驶时也能安全操作。


## ✨ 特性亮点

<table>
<tr>
<td width="50%">

### 🔒 私有化部署
- 数据完全自主掌控
- 不受版权下架影响
- 支持 NAS / 家庭服务器部署

</td>
<td width="50%">

### 🤖 AI 智能处理
- **UVR5** 自动分离人声/伴奏
- **Whisper** 智能生成时间轴歌词
- 一键导入，全自动处理

</td>
</tr>
<tr>
<td width="50%">

### 🚗 车载优先设计
- 超大触控区 (>60px)
- 极简交互层级
- 防误触优化

</td>
<td width="50%">

### 🎵 沉浸 K 歌体验
- 全屏 MV + 大字歌词
- 原唱/伴奏平滑切换
- 500ms Crossfade 渐变

</td>
</tr>
</table>

---

## 🏗 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户 / 车机浏览器                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Next.js 14 Web Player                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  资源库首页  │  │  沉浸播放器  │  │  AudioManager (三轨同步) │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐   │
│  │ Songs API│  │Stream API│  │Search Svc│  │ Pinyin Utils   │   │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘   │
└───────┬─────────────────────────────┬───────────────────────────┘
        │                             │
        ▼                             ▼
┌───────────────┐           ┌─────────────────┐
│  PostgreSQL   │           │  Celery Worker  │
│  + pgvector   │           │  (AI Pipeline)  │
└───────────────┘           └────────┬────────┘
                                     │
                            ┌────────┴────────┐
                            ▼                 ▼
                      ┌──────────┐      ┌──────────┐
                      │   UVR5   │      │ Whisper  │
                      │ 音频分离  │      │ 歌词生成  │
                      └──────────┘      └──────────┘
```

---

## 🚀 快速开始

### 环境要求

| 组件 | 版本要求 |
|------|----------|
| Docker | 20.10+ |
| Docker Compose | 2.0+ |
| Node.js | 18+ (开发时) |
| Python | 3.11+ (开发时) |

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/nebula-ktv.git
cd nebula-ktv

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库密码等

# 3. 启动所有服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps
```

### 访问服务

| 服务 | 地址 | 说明 |
|------|------|------|
| 🎤 Web 播放器 | http://localhost:3000 | 主界面 |
| 📡 API 服务 | http://localhost:8000 | 后端接口 |
| 📚 API 文档 | http://localhost:8000/docs | Swagger UI |


---

## 🛠 技术栈

<table>
<tr>
<th>层级</th>
<th>技术</th>
<th>说明</th>
</tr>
<tr>
<td><strong>前端</strong></td>
<td>
  <img src="https://img.shields.io/badge/Next.js-14-black?logo=next.js" /><br/>
  <img src="https://img.shields.io/badge/Tailwind-CSS-38B2AC?logo=tailwind-css" /><br/>
  <img src="https://img.shields.io/badge/shadcn/ui-Components-000" />
</td>
<td>App Router + RSC，暗夜玻璃质感 UI</td>
</tr>
<tr>
<td><strong>后端</strong></td>
<td>
  <img src="https://img.shields.io/badge/FastAPI-Python-009688?logo=fastapi" /><br/>
  <img src="https://img.shields.io/badge/Celery-Task_Queue-37814A?logo=celery" /><br/>
  <img src="https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis" />
</td>
<td>异步 API + 分布式任务队列</td>
</tr>
<tr>
<td><strong>数据库</strong></td>
<td>
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql" /><br/>
  <img src="https://img.shields.io/badge/pgvector-AI_Ready-336791" />
</td>
<td>向量搜索 + JSONB 扩展字段</td>
</tr>
<tr>
<td><strong>AI 模型</strong></td>
<td>
  <img src="https://img.shields.io/badge/UVR5-Audio_Separation-FF6B6B" /><br/>
  <img src="https://img.shields.io/badge/Whisper-Speech_Recognition-74AA9C" />
</td>
<td>人声分离 + 歌词生成</td>
</tr>
</table>

---

## 📁 项目结构

```
nebula-ktv/
├── 📂 frontend/                  # Next.js 前端应用
│   ├── 📂 src/
│   │   ├── 📂 app/              # 页面路由
│   │   │   ├── page.tsx         # 首页资源库
│   │   │   └── player/[id]/     # 播放器页面
│   │   ├── 📂 components/
│   │   │   ├── 📂 library/      # 资源库组件
│   │   │   │   ├── SearchBar    # 搜索框
│   │   │   │   ├── RecentSection# 最近添加
│   │   │   │   └── SongList     # 歌曲列表
│   │   │   ├── 📂 player/       # 播放器组件
│   │   │   │   ├── AudioManager # 三轨音频管理
│   │   │   │   ├── ImmersiveMode# 沉浸模式
│   │   │   │   ├── ControlBar   # 控制栏
│   │   │   │   └── LyricsDisplay# 歌词显示
│   │   │   └── 📂 ui/           # shadcn/ui 组件
│   │   ├── 📂 hooks/            # React Hooks
│   │   └── 📂 lib/
│   │       ├── 📂 api/          # API 客户端
│   │       └── 📂 audio/        # 音频处理 (Crossfade)
│   └── package.json
│
├── 📂 backend/                   # FastAPI 后端服务
│   ├── 📂 app/
│   │   ├── 📂 api/              # REST API 路由
│   │   │   ├── songs.py         # 歌曲 CRUD
│   │   │   └── stream.py        # 媒体流服务
│   │   ├── 📂 models/           # 数据模型
│   │   ├── 📂 services/         # 业务逻辑
│   │   └── 📂 utils/            # 工具函数
│   ├── 📂 worker/               # Celery 任务
│   │   └── 📂 tasks/            # AI 处理任务
│   ├── 📂 tests/                # 测试文件
│   └── requirements.txt
│
├── 📂 docker/                    # Docker 配置
│   └── 📂 init-db/              # 数据库初始化
├── 📂 docs/                      # 项目文档
├── docker-compose.yml            # 容器编排
└── .env.example                  # 环境变量模板
```

---

## 📡 API 文档

### 歌曲管理

| 方法 | 端点 | 描述 |
|:----:|------|------|
| `GET` | `/api/songs` | 获取歌曲列表 (分页、搜索、筛选) |
| `GET` | `/api/songs/{id}` | 获取单首歌曲详情 |
| `POST` | `/api/songs` | 创建歌曲记录 |
| `PATCH` | `/api/songs/{id}` | 更新歌曲信息 |
| `DELETE` | `/api/songs/{id}` | 删除歌曲 |
| `GET` | `/api/songs/recent` | 获取最近添加 |

### 媒体流服务

| 方法 | 端点 | 描述 |
|:----:|------|------|
| `GET` | `/api/stream/{asset_id}` | 媒体流 (支持 HTTP Range) |

### 请求示例

```bash
# 搜索歌曲
curl "http://localhost:8000/api/songs?q=周杰伦&limit=10"

# 获取歌曲详情
curl "http://localhost:8000/api/songs/550e8400-e29b-41d4-a716-446655440000"

# JSONB 筛选 (按 BPM 范围)
curl "http://localhost:8000/api/songs?bpm_min=100&bpm_max=140"
```


---

## 💻 开发指南

### 本地开发

```bash
# 前端开发
cd frontend
npm install
npm run dev          # http://localhost:3000

# 后端开发
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000

# 启动 Celery Worker
celery -A worker.celery_app worker --loglevel=info
```

### 运行测试

```bash
# 后端测试 (pytest + hypothesis 属性测试)
cd backend
python -m pytest -v

# 前端测试 (vitest + fast-check 属性测试)
cd frontend
npm run test
```

---

## 🧪 测试覆盖

项目采用 **属性测试 (Property-Based Testing)** 验证核心正确性，确保系统在各种输入下都能正确运行。

| # | 属性名称 | 描述 | 验证需求 |
|:-:|----------|------|:--------:|
| 1 | 歌曲数据持久化 | 创建后查询返回等价数据 (Round-Trip) | 8.1 |
| 2 | 拼音首字母一致性 | 中文转拼音结果稳定且格式正确 | 1.2 |
| 3 | 状态枚举约束 | 状态值必须是有效枚举成员 | 1.4 |
| 4 | 搜索结果相关性 | 返回结果必须匹配查询条件 | 3.2 |
| 5 | 处理中歌曲不可播放 | PROCESSING 状态歌曲禁止播放 | 3.5 |
| 6 | 三轨同步播放 | 缓冲时所有轨道同步暂停 | 6.2, 6.3 |
| 7 | Crossfade 增益约束 | 切换时增益和接近 1.0 | 6.4 |
| 8 | HTTP Range 正确性 | Range 响应头与请求匹配 | 9.1, 9.2 |
| 9 | 媒体资产完整性 | 处理完成后三种资产记录齐全 | 8.2 |
| 10 | JSONB 查询正确性 | 筛选结果满足查询条件 | 8.3 |
| 11 | 错误状态完整性 | 失败时记录错误信息 | 2.5 |

**测试结果**: ✅ 89 tests passed (Backend: 56, Frontend: 33)

---

## 🎨 界面预览

### 首页资源库

```
┌────────────────────────────────────────────────────────┐
│  🔍 搜索歌曲或歌手...                                    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  📀 最近添加                                    ← 滑动 → │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐          │
│  │  封面  │ │  封面  │ │  封面  │ │  封面  │          │
│  │        │ │        │ │        │ │        │          │
│  │ 歌名   │ │ 歌名   │ │ 歌名   │ │ 歌名   │          │
│  │ 歌手   │ │ 歌手   │ │ 歌手   │ │ 歌手   │          │
│  └────────┘ └────────┘ └────────┘ └────────┘          │
│                                                        │
│  🎵 全部歌曲                                            │
│  ┌──────────────────────────────────────────────┐     │
│  │ 🖼 │ 晴天                              │  ▶️  │     │
│  │    │ 周杰伦 · 华语 · 流行               │      │     │
│  └──────────────────────────────────────────────┘     │
│  ┌──────────────────────────────────────────────┐     │
│  │ 🖼 │ 七里香                            │  ▶️  │     │
│  │    │ 周杰伦 · 华语 · 流行               │      │     │
│  └──────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────┘
```

### 沉浸播放模式

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│                                                        │
│                    🎬 全屏 MV 视频                      │
│                                                        │
│                                                        │
│                                                        │
│                                                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│              故事的小黄花                               │
│                从出生那年就飘着                          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 交互控制模式

```
┌────────────────────────────────────────────────────────┐
│  ←  晴天 - 周杰伦                                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│                    🎬 MV 视频                          │
│                                                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  1:23                                           4:30   │
│                                                        │
│        ┌─────────────────────────────────┐            │
│        │  原唱 ●────────────○ 伴奏      │            │
│        └─────────────────────────────────┘            │
│                                                        │
│              ⏮️      ▶️      ⏭️                        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 📋 环境变量

```bash
# 数据库配置
POSTGRES_DB=nebula_ktv
POSTGRES_USER=nebula
POSTGRES_PASSWORD=your_secure_password

# Redis 配置
REDIS_PASSWORD=your_redis_password

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your_secret_key

# AI 模型配置
UVR5_MODEL_PATH=/app/models/uvr5
WHISPER_MODEL_SIZE=large-v3
WHISPER_DEVICE=cuda  # 或 cpu

# 媒体存储
MEDIA_ROOT=/app/media
```

---

## 🗺 路线图

- [x] 核心播放器功能
- [x] AI 音频分离 (UVR5)
- [x] 歌词生成 (Whisper)
- [x] 原唱/伴奏切换
- [x] 属性测试覆盖
- [ ] 歌单管理
- [ ] 多用户支持
- [ ] 语音点歌
- [ ] 评分系统

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

---

<p align="center">
  Made with ❤️ for KTV lovers
</p>

<p align="center">
  <a href="#-nebula-ktv-星云-ktv">回到顶部 ⬆️</a>
</p>
