/**
 * Nebula KTV API 类型定义
 * 基于后端 Pydantic Schema 生成
 */

// ============================================
// 枚举类型
// ============================================

/** 歌曲处理状态 */
export enum SongStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  READY = "READY",
  PARTIAL = "PARTIAL",
  FAILED = "FAILED",
}

/** 媒体资产类型 */
export enum AssetType {
  VIDEO_MASTER = "video_master",
  AUDIO_ORIGINAL = "audio_original",
  AUDIO_INST = "audio_inst",
  AUDIO_VOCAL = "audio_vocal",
  LYRICS_VTT = "lyrics_vtt",
  LYRICS_WORD_LEVEL = "lyrics_word_level",
  WAVEFORM_JSON = "waveform_json",
}

/** 语系 */
export enum LanguageFamily {
  CHINESE = "Chinese",
  ENGLISH = "English",
  JAPANESE = "Japanese",
  KOREAN = "Korean",
  OTHER = "Other",
}

/** 方言 */
export enum LanguageDialect {
  MANDARIN = "Mandarin",
  CANTONESE = "Cantonese",
  HOKKIEN = "Hokkien",
  OTHER = "Other",
}

/** 演唱形式 */
export enum SingingType {
  SOLO = "Solo",
  DUET = "Duet",
  GROUP = "Group",
  CHOIR = "Choir",
}

/** 性别类型 */
export enum GenderType {
  MALE = "Male",
  FEMALE = "Female",
  MIX = "Mix",
  BAND = "Band",
}

/** 音乐流派 */
export enum Genre {
  POP = "Pop",
  ROCK = "Rock",
  RNB = "R&B",
  BALLAD = "Ballad",
  EDM = "EDM",
  JAZZ = "Jazz",
  CLASSICAL = "Classical",
  HIPHOP = "HipHop",
  FOLK = "Folk",
  OTHER = "Other",
}

/** 画质标签 */
export enum QualityBadge {
  QUALITY_4K = "4K",
  HD = "HD",
  SD = "SD",
}

// ============================================
// 歌曲类型
// ============================================

/** 歌曲响应 */
export interface Song {
  id: string;
  title: string;
  artist: string;
  subtitle?: string | null;
  album?: string | null;
  year?: number | null;
  cover_path?: string | null;

  // 创作信息
  lyricist?: string | null;
  composer?: string | null;
  arranger?: string | null;
  publisher?: string | null;

  // 分类信息
  language_family?: string | null;
  language_dialect?: string | null;
  singing_type?: string | null;
  gender_type?: string | null;
  genre?: string | null;
  scenario?: string[] | null;
  aliases?: string[] | null;

  // 搜索优化
  title_pinyin?: string | null;
  title_abbr?: string | null;
  artist_pinyin?: string | null;
  artist_abbr?: string | null;

  // AI 音频指纹
  duration?: number | null;
  bpm?: number | null;
  original_key?: string | null;
  camelot_key?: string | null;
  energy?: number | null;
  danceability?: number | null;
  valence?: number | null;
  vocal_range_low?: string | null;
  vocal_range_high?: string | null;
  difficulty_level?: number | null;
  feature_vector?: number[] | null;

  // 状态与运营
  status: SongStatus;
  play_count: number;
  last_played_at?: string | null;
  is_favorite: boolean;
  quality_badge?: string | null;
  meta_json: Record<string, unknown>;

  created_at: string;
  updated_at: string;
}

/** 创建歌曲请求 */
export interface SongCreate {
  title: string;
  artist: string;
  subtitle?: string | null;
  album?: string | null;
  year?: number | null;
  cover_path?: string | null;
  lyricist?: string | null;
  composer?: string | null;
  arranger?: string | null;
  publisher?: string | null;
  language_family?: string | null;
  language_dialect?: string | null;
  singing_type?: string | null;
  gender_type?: string | null;
  genre?: string | null;
  scenario?: string[] | null;
  aliases?: string[] | null;
  meta_json?: Record<string, unknown>;
}

/** 更新歌曲请求 */
export interface SongUpdate {
  title?: string | null;
  artist?: string | null;
  subtitle?: string | null;
  album?: string | null;
  year?: number | null;
  cover_path?: string | null;
  lyricist?: string | null;
  composer?: string | null;
  arranger?: string | null;
  publisher?: string | null;
  language_family?: string | null;
  language_dialect?: string | null;
  singing_type?: string | null;
  gender_type?: string | null;
  genre?: string | null;
  scenario?: string[] | null;
  aliases?: string[] | null;
  duration?: number | null;
  bpm?: number | null;
  original_key?: string | null;
  camelot_key?: string | null;
  energy?: number | null;
  danceability?: number | null;
  valence?: number | null;
  vocal_range_low?: string | null;
  vocal_range_high?: string | null;
  difficulty_level?: number | null;
  feature_vector?: number[] | null;
  status?: SongStatus | null;
  is_favorite?: boolean | null;
  quality_badge?: string | null;
  meta_json?: Record<string, unknown> | null;
}

// ============================================
// 媒体资产类型
// ============================================

/** 媒体资产响应 */
export interface MediaAsset {
  id: string;
  song_id: string;
  type: AssetType;
  path: string;
  file_size?: number | null;
  duration?: number | null;
  codec?: string | null;
  bitrate?: number | null;
  resolution?: string | null;
  created_at: string;
}

/** 创建媒体资产请求 */
export interface MediaAssetCreate {
  song_id: string;
  type: AssetType;
  path: string;
  file_size?: number | null;
  duration?: number | null;
  codec?: string | null;
  bitrate?: number | null;
  resolution?: string | null;
}

// ============================================
// API 响应类型
// ============================================

/** API 错误响应 */
export interface ApiError {
  detail: string;
}

/** 分页参数 */
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

/** 搜索参数 */
export interface SearchParams extends PaginationParams {
  q: string;
}
