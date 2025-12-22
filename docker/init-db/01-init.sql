-- Nebula KTV Database Initialization Script (Schema v4.0)
-- 基于元数据构建指南的终极架构

-- Enable pgvector extension for AI vector storage
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 核心歌曲表 (songs)
-- ============================================
CREATE TABLE songs (
    -- ==========================================
    -- 1. 基础身份信息 (Basic Identity)
    -- ==========================================
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,                -- 歌名 (e.g., "七里香")
    subtitle TEXT,                      -- 副标题/备注 (e.g., "Live at 无与伦比演唱会")
    artist TEXT NOT NULL,               -- 歌手 (e.g., "周杰伦")
    album TEXT,                         -- 专辑 (e.g., "七里香")
    year INTEGER,                       -- 发行年份 (e.g., 2004)
    cover_path TEXT,                    -- 封面相对路径
    
    -- ==========================================
    -- 2. 创作与版权信息 (Credits & Copyright)
    -- ==========================================
    lyricist TEXT,                      -- 作词 (e.g., "方文山")
    composer TEXT,                      -- 作曲 (e.g., "周杰伦")
    arranger TEXT,                      -- 编曲 (e.g., "钟兴民")
    publisher TEXT,                     -- 发行公司 (e.g., "杰威尔音乐")
    
    -- ==========================================
    -- 3. KTV 业务分类 (KTV Classification)
    -- ==========================================
    -- 语言与地区
    language_family VARCHAR(20),        -- 语系: 'Chinese', 'English', 'Japanese', 'Korean'
    language_dialect VARCHAR(20),       -- 方言: 'Mandarin', 'Cantonese', 'Hokkien'
    
    -- 演唱形式
    singing_type VARCHAR(20),           -- 'Solo', 'Duet', 'Group', 'Choir'
    gender_type VARCHAR(20),            -- 'Male', 'Female', 'Mix', 'Band'
    
    -- 风格与场景
    genre VARCHAR(30),                  -- 流派: 'Pop', 'Rock', 'R&B', 'Ballad', 'EDM'
    scenario JSONB,                     -- 场景标签: ["Wedding", "Driving", "Breakup"]
    
    -- ==========================================
    -- 4. 搜索优化 (Search Index)
    -- ==========================================
    title_pinyin TEXT,                  -- 'qi li xiang'
    title_abbr VARCHAR(50),             -- 'qlx'
    artist_pinyin TEXT,                 -- 'zhou jie lun'
    artist_abbr VARCHAR(50),            -- 'zjl'
    aliases JSONB,                      -- 别名: ["Common Jasmine Orange", "7里香"]
    
    -- ==========================================
    -- 5. AI 音频指纹 (AI Audio Analysis)
    -- ==========================================
    duration INTEGER,                   -- 时长 (秒)
    bpm INTEGER,                        -- 速度 (BPM)
    original_key VARCHAR(10),           -- 原调 (e.g., 'C#m')
    camelot_key VARCHAR(5),             -- 混音调式 (e.g., '12B')
    
    -- 能量值 (0.0 - 1.0)
    energy NUMERIC(3,2),                -- 能量感
    danceability NUMERIC(3,2),          -- 舞曲感
    valence NUMERIC(3,2),               -- 正能量指数
    
    -- 演唱难度
    vocal_range_low VARCHAR(5),         -- 最低音 (e.g., 'G3')
    vocal_range_high VARCHAR(5),        -- 最高音 (e.g., 'A5')
    difficulty_level INTEGER,           -- 综合难度 (1-5)
    
    -- AI 语义向量
    feature_vector vector(768),
    
    -- ==========================================
    -- 6. 状态与运营 (Operations)
    -- ==========================================
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSING', 'READY', 'PARTIAL', 'FAILED')),
    play_count INTEGER DEFAULT 0,
    last_played_at TIMESTAMPTZ,
    is_favorite BOOLEAN DEFAULT FALSE,
    quality_badge VARCHAR(10),          -- '4K', 'HD', 'SD'
    
    -- 兜底字段
    meta_json JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 媒体资产表 (media_assets)
-- ============================================
CREATE TABLE media_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    song_id UUID REFERENCES songs(id) ON DELETE CASCADE,
    
    -- 资产类型细分
    type VARCHAR(30) NOT NULL CHECK (type IN (
        'video_master',      -- 主视频文件
        'audio_original',    -- 原版立体声
        'audio_inst',        -- AI 分离的伴奏
        'audio_vocal',       -- AI 分离的人声
        'lyrics_vtt',        -- 时间轴歌词
        'lyrics_word_level', -- 逐字对齐歌词 (JSON)
        'waveform_json'      -- 音频波形数据
    )),
    
    path TEXT NOT NULL,
    
    -- 技术元数据
    file_size BIGINT,                   -- 字节
    duration NUMERIC(10, 2),            -- 精确时长
    codec VARCHAR(20),                  -- 'h264', 'hevc', 'aac', 'flac'
    bitrate INTEGER,                    -- 320000 (320kbps)
    resolution VARCHAR(20),             -- '1920x1080' (仅视频)
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 索引 (Indexes)
-- ============================================

-- 搜索优化索引
CREATE INDEX idx_search_full ON songs(title_abbr, artist_abbr);
CREATE INDEX idx_search_pinyin ON songs(title_pinyin, artist_pinyin);

-- 创作者索引
CREATE INDEX idx_credits ON songs(lyricist, composer);

-- 分类索引
CREATE INDEX idx_classification ON songs(language_family, language_dialect, singing_type, gender_type);
CREATE INDEX idx_genre ON songs(genre);

-- AI 音频匹配索引
CREATE INDEX idx_audio_match ON songs(bpm, energy);
CREATE INDEX idx_vocal_match ON songs(vocal_range_low, vocal_range_high, difficulty_level);

-- 场景标签 GIN 索引
CREATE INDEX idx_scenario ON songs USING GIN (scenario);
CREATE INDEX idx_aliases ON songs USING GIN (aliases);

-- HNSW 向量索引
CREATE INDEX idx_songs_feature_vector ON songs USING hnsw (feature_vector vector_cosine_ops);

-- JSONB 元数据索引
CREATE INDEX idx_songs_meta_json ON songs USING GIN (meta_json);

-- 状态和时间索引
CREATE INDEX idx_songs_status ON songs (status);
CREATE INDEX idx_songs_created_at ON songs (created_at DESC);
CREATE INDEX idx_songs_play_count ON songs (play_count DESC);
CREATE INDEX idx_songs_favorite ON songs (is_favorite) WHERE is_favorite = TRUE;

-- 媒体资产索引
CREATE INDEX idx_media_assets_song_id ON media_assets (song_id);
CREATE INDEX idx_media_assets_type ON media_assets (type);

-- ============================================
-- 触发器 (Triggers)
-- ============================================

-- updated_at 自动更新触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$ language 'plpgsql';

CREATE TRIGGER update_songs_updated_at 
    BEFORE UPDATE ON songs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 示例数据 (Sample Data)
-- ============================================
INSERT INTO songs (
    title, subtitle, artist, album, year, cover_path,
    lyricist, composer, arranger, publisher,
    language_family, language_dialect, singing_type, gender_type, genre, scenario,
    title_pinyin, title_abbr, artist_pinyin, artist_abbr, aliases,
    duration, bpm, original_key, camelot_key, energy, danceability, valence,
    vocal_range_low, vocal_range_high, difficulty_level,
    status, quality_badge, meta_json
) VALUES
(
    '告白气球', NULL, '周杰伦', '周杰伦的床边故事', 2016, '/covers/gbqq.jpg',
    '方文山', '周杰伦', '林迈可', '杰威尔音乐',
    'Chinese', 'Mandarin', 'Solo', 'Male', 'Pop', '["Wedding", "Romance", "Confession"]',
    'gao bai qi qiu', 'gbqq', 'zhou jie lun', 'zjl', '["Balloon", "告白氣球"]',
    215, 120, 'C', '8B', 0.65, 0.72, 0.85,
    'G3', 'D5', 2,
    'READY', 'HD', '{}'
),
(
    '稻香', NULL, '周杰伦', '魔杰座', 2008, '/covers/dx.jpg',
    '周杰伦', '周杰伦', '黄雨勋', '杰威尔音乐',
    'Chinese', 'Mandarin', 'Solo', 'Male', 'Pop', '["Nostalgia", "Countryside", "Healing"]',
    'dao xiang', 'dx', 'zhou jie lun', 'zjl', '["Rice Field"]',
    234, 85, 'G', '9B', 0.55, 0.45, 0.90,
    'E3', 'B4', 2,
    'READY', 'HD', '{}'
),
(
    '夜曲', NULL, '周杰伦', '十一月的萧邦', 2005, '/covers/yq.jpg',
    '方文山', '周杰伦', '林迈可', '杰威尔音乐',
    'Chinese', 'Mandarin', 'Solo', 'Male', 'Ballad', '["Night", "Melancholy", "Classical"]',
    'ye qu', 'yq', 'zhou jie lun', 'zjl', '["Nocturne"]',
    268, 78, 'Dm', '7A', 0.40, 0.30, 0.35,
    'D3', 'A4', 3,
    'PROCESSING', 'HD', '{}'
),
(
    '屋顶', NULL, '周杰伦/温岚', '温岚同名专辑', 2000, '/covers/wuding.jpg',
    '周杰伦', '周杰伦', '洪敬尧', '阿尔发音乐',
    'Chinese', 'Mandarin', 'Duet', 'Mix', 'Ballad', '["Romance", "Duet", "Classic"]',
    'wu ding', 'wd', 'zhou jie lun wen lan', 'zjlwl', '["Rooftop"]',
    312, 72, 'F', '7B', 0.45, 0.35, 0.60,
    'C3', 'F5', 3,
    'READY', 'HD', '{}'
);

-- 权限设置
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nebula_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nebula_user;
