# Implementation Plan

## Phase 1: 项目骨架与基础设施

- [x] 1. 初始化项目结构和 Docker 编排




  - [x] 1.1 创建项目目录结构 (frontend/, backend/, docker/)

    - 创建 frontend/、backend/、docker/ 目录
    - 创建 .env.example 环境变量模板
    - _Requirements: 技术架构设计 Stage 4.1_

  - [x] 1.2 编写 docker-compose.yml 配置
    - 配置 PostgreSQL + pgvector 容器
    - 配置 Redis 容器
    - 配置 API 和 Worker 容器
    - 配置 Web 前端容器
    - 配置卷映射和网络
    - _Requirements: 技术架构设计 Stage 4.1_

  - [x] 1.3 创建数据库初始化脚本
    - 编写 schema.sql 创建 songs 和 media_assets 表
    - 启用 pgvector 扩展
    - 创建索引 (HNSW, GIN)
    - _Requirements: 8.1, 8.2_

## Phase 2: 后端核心 API

- [x] 2. 搭建 FastAPI 后端框架
  - [x] 2.1 初始化 FastAPI 项目结构
    - 创建 main.py 入口文件
    - 配置 CORS 和中间件
    - 设置数据库连接池
    - _Requirements: 技术架构设计 Stage 4.2_

  - [x] 2.2 实现数据模型和 Pydantic Schema
    - 创建 Song 模型和 SongStatus 枚举
    - 创建 MediaAsset 模型和 AssetType 枚举
    - 实现 SongCreate、SongUpdate、SongResponse Schema
    - _Requirements: 1.1, 1.4_

  - [x] 2.3 编写属性测试：歌曲状态枚举约束
    - **Property 3: 歌曲状态枚举约束**
    - **Validates: Requirements 1.4**

  - [x] 2.4 实现拼音首字母转换工具
    - 使用 pypinyin 库实现中文转拼音首字母
    - 处理非中文字符（保留原字符）
    - _Requirements: 1.2_

  - [x] 2.5 编写属性测试：拼音首字母生成一致性
    - **Property 2: 拼音首字母生成一致性**
    - **Validates: Requirements 1.2**

  - [x] 2.6 实现 Song CRUD API
    - GET /api/songs - 列表查询（分页、搜索）
    - GET /api/songs/{id} - 单曲详情
    - POST /api/songs - 创建歌曲
    - PATCH /api/songs/{id} - 更新歌曲
    - DELETE /api/songs/{id} - 删除歌曲
    - GET /api/songs/recent - 最近添加
    - _Requirements: 1.1, 1.3_

  - [x] 2.7 编写属性测试：歌曲数据持久化 Round-Trip
    - **Property 1: 歌曲数据持久化 Round-Trip**
    - **Validates: Requirements 8.1**

  - [x] 2.8 实现搜索服务
    - 支持标题和歌手名模糊搜索
    - 支持拼音首字母搜索
    - _Requirements: 3.2_

  - [x] 2.9 编写属性测试：搜索结果相关性
    - **Property 4: 搜索结果相关性**
    - **Validates: Requirements 3.2**

- [x] 3. Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.

## Phase 3: 媒体流服务

- [x] 4. 实现媒体流 API
  - [x] 4.1 实现 HTTP Range Requests 支持
    - 解析 Range 请求头
    - 返回正确的 Content-Range 和 206 状态码
    - 支持视频和音频文件流式传输
    - _Requirements: 9.1, 9.2_

  - [x] 4.2 编写属性测试：HTTP Range 响应正确性
    - **Property 8: HTTP Range 响应正确性**
    - **Validates: Requirements 9.1, 9.2**

  - [x] 4.3 实现媒体资产查询 API
    - GET /api/stream/{asset_id} - 流式传输
    - 根据 asset_id 查找文件路径
    - 设置正确的 Content-Type
    - _Requirements: 9.3_

## Phase 4: Celery 任务队列

- [x] 5. 搭建 Celery Worker 框架
  - [x] 5.1 配置 Celery 应用
    - 创建 celery_app.py 配置文件
    - 连接 Redis broker
    - 配置任务序列化和结果后端
    - _Requirements: 技术架构设计 Stage 4.2_

  - [x] 5.2 实现空 Worker 任务（跑通流程）
    - 创建 process_song_task 任务骨架
    - 接收 song_id 和 file_path 参数
    - 更新歌曲状态为 PROCESSING -> READY
    - _Requirements: 2.1, 2.4_

  - [x] 5.3 编写属性测试：错误状态记录完整性
    - **Property 11: 错误状态记录完整性**
    - **Validates: Requirements 2.5**

- [x] 6. Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.

## Phase 5: 前端基础框架

- [x] 7. 初始化 Next.js 前端项目
  - [x] 7.1 创建 Next.js 14 项目
    - 使用 App Router
    - 配置 TypeScript
    - 安装 Tailwind CSS
    - _Requirements: 技术架构设计 Stage 4.3_

  - [x] 7.2 配置 Tailwind 主题和 shadcn/ui
    - 配置暗夜玻璃质感色板 (background, surface, primary, accent)
    - 配置车载字体大小 (text-5xl, text-3xl 等)
    - 安装 shadcn/ui 核心组件 (Button, Input, Card, Slider)
    - _Requirements: 视觉定义文档_

  - [x] 7.3 创建 API 客户端
    - 封装 fetch 请求
    - 定义 Song 和 MediaAsset TypeScript 类型
    - 实现歌曲列表、详情、搜索 API 调用
    - _Requirements: 1.3_

## Phase 6: 首页资源库

- [x] 8. 实现首页资源库界面
  - [x] 8.1 实现 SearchBar 组件
    - 全局搜索框，高度 > 60px
    - 支持输入歌手或歌名
    - 防抖搜索 (300ms)
    - _Requirements: 3.1, 3.2_

  - [x] 8.2 实现 RecentSection 组件
    - 横向滚动容器
    - 正方形大封面卡片
    - 显示歌名和歌手
    - _Requirements: 3.3_

  - [x] 8.3 实现 SongList 组件
    - 列表项高度 > 100px
    - 左侧封面 | 中间歌名+歌手+标签 | 右侧播放按钮
    - 处理中歌曲置灰显示
    - _Requirements: 3.4, 3.5_

  - [x] 8.4 编写属性测试：处理中歌曲不可播放
    - **Property 5: 处理中歌曲不可播放**
    - **Validates: Requirements 3.5**

  - [x] 8.5 组装首页 page.tsx
    - 集成 SearchBar、RecentSection、SongList
    - 实现数据获取和状态管理
    - 处理加载和错误状态
    - _Requirements: 3.1, 3.3, 3.4_

- [x] 9. Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.

## Phase 7: 播放器核心

- [x] 10. 实现音频管理器
  - [x] 10.1 创建 AudioManager 组件
    - 使用 Web Audio API 创建 AudioContext
    - 同时加载视频、原唱、伴奏三个媒体源
    - 管理 GainNode 用于音量控制
    - _Requirements: 6.1_

  - [x] 10.2 实现三轨同步播放逻辑
    - 等待所有媒体源 canplaythrough 事件
    - 同步播放/暂停/跳转操作
    - 处理缓冲状态
    - _Requirements: 6.2, 6.3_

  - [x] 10.3 编写属性测试：三轨同步播放约束
    - **Property 6: 三轨同步播放约束**
    - **Validates: Requirements 6.2, 6.3**

  - [x] 10.4 实现 Crossfade 切换函数
    - 500ms 交叉渐变
    - 使用 linearRampToValueAtTime
    - 确保增益值平滑过渡
    - _Requirements: 6.4_

  - [x] 10.5 编写属性测试：Crossfade 增益值约束
    - **Property 7: Crossfade 增益值约束**
    - **Validates: Requirements 6.4**

  - [x] 10.6 实现降级策略
    - 检测伴奏加载失败
    - 自动切换到仅原唱模式
    - 禁用切换开关
    - _Requirements: 6.5_

## Phase 8: 播放器界面

- [x] 11. 实现沉浸模式
  - [x] 11.1 创建 ImmersiveMode 组件
    - 全屏视频背景
    - 底部歌词显示区域 (20%)
    - 当前句 48px+ 高亮，下一句半透明
    - _Requirements: 4.2, 4.3, 4.4, 4.5_

  - [x] 11.2 实现 LyricsDisplay 组件
    - 解析 JSON 格式歌词
    - 根据当前时间高亮对应歌词
    - 平滑滚动动画
    - _Requirements: 4.4, 4.5_

- [x] 12. 实现交互模式
  - [x] 12.1 创建 ControlBar 组件
    - 底部控制栏，高度 >= 25%
    - 玻璃拟态背景 (bg-black/60 backdrop-blur-md)
    - _Requirements: 5.3_

  - [x] 12.2 实现进度条
    - 粗线条进度条
    - 加大滑块尺寸
    - 支持拖拽跳转
    - _Requirements: 5.4_

  - [x] 12.3 实现原唱/伴奏开关
    - 胶囊形状 Toggle Switch
    - 关闭灰色，开启赛博青色
    - 点击触发 Crossfade
    - _Requirements: 5.4, 6.4_

  - [x] 12.4 实现播放控制按钮
    - 播放/暂停按钮 (最大尺寸)
    - 下一首按钮
    - 按下缩放反馈
    - _Requirements: 5.4, 7.1, 7.2_

  - [x] 12.5 实现顶部遮罩
    - 返回按钮
    - 歌曲标题显示
    - _Requirements: 5.2_

- [x] 13. 实现模式切换逻辑
  - [x] 13.1 实现自动隐藏定时器
    - 5 秒无操作自动进入沉浸模式
    - 拖拽进度条时暂停计时
    - 任意点击唤起交互模式
    - _Requirements: 4.1, 5.1, 5.5, 5.6_

  - [x] 13.2 组装播放器页面 player/[id]/page.tsx
    - 集成 AudioManager、ImmersiveMode、ControlBar
    - 管理播放状态和模式切换
    - 处理错误和降级
    - _Requirements: 4.1, 5.1_

- [x] 14. Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.

## Phase 9: 集成与完善

- [x] 15. 实现 JSONB 查询功能
  - [x] 15.1 扩展搜索 API 支持 JSONB 筛选
    - 支持按 BPM、Key、Tags 等字段筛选
    - 使用 PostgreSQL JSONB 操作符
    - _Requirements: 8.3_

  - [x] 15.2 编写属性测试：JSONB 查询正确性
    - **Property 10: JSONB 查询正确性**
    - **Validates: Requirements 8.3**

- [x] 16. 实现媒体资产记录
  - [x] 16.1 完善 Worker 任务的资产记录逻辑
    - 处理完成后创建 media_assets 记录
    - 记录 video_main、audio_original、audio_inst 路径
    - _Requirements: 8.2_

  - [x] 16.2 编写属性测试：媒体资产记录完整性
    - **Property 9: 媒体资产记录完整性**
    - **Validates: Requirements 8.2**

- [x] 17. Final Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.
