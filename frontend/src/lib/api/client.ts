/**
 * Nebula KTV API 客户端
 * 封装所有后端 API 调用
 */

import type {
  Song,
  SongCreate,
  SongUpdate,
  MediaAsset,
  PaginationParams,
  ApiError,
} from "./types";

// ============================================
// 配置
// ============================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ============================================
// 基础请求封装
// ============================================

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const defaultHeaders: HeadersInit = {
      "Content-Type": "application/json",
    };

    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const errorData: ApiError = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // 忽略 JSON 解析错误
      }
      throw new Error(errorMessage);
    }

    // 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  // ============================================
  // 歌曲 API
  // ============================================

  /**
   * 获取歌曲列表
   */
  async getSongs(params: PaginationParams = {}): Promise<Song[]> {
    const searchParams = new URLSearchParams();
    if (params.skip !== undefined) {
      searchParams.set("skip", params.skip.toString());
    }
    if (params.limit !== undefined) {
      searchParams.set("limit", params.limit.toString());
    }

    const query = searchParams.toString();
    const endpoint = `/api/songs${query ? `?${query}` : ""}`;

    return this.request<Song[]>(endpoint);
  }

  /**
   * 获取最近添加的歌曲
   */
  async getRecentSongs(limit: number = 10): Promise<Song[]> {
    return this.request<Song[]>(`/api/songs/recent?limit=${limit}`);
  }

  /**
   * 搜索歌曲
   */
  async searchSongs(query: string, limit: number = 20): Promise<Song[]> {
    const searchParams = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });
    return this.request<Song[]>(`/api/songs/search?${searchParams}`);
  }

  /**
   * 获取单首歌曲详情
   */
  async getSong(songId: string): Promise<Song> {
    return this.request<Song>(`/api/songs/${songId}`);
  }

  /**
   * 创建歌曲
   */
  async createSong(data: SongCreate): Promise<Song> {
    return this.request<Song>("/api/songs/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  /**
   * 更新歌曲
   */
  async updateSong(songId: string, data: SongUpdate): Promise<Song> {
    return this.request<Song>(`/api/songs/${songId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  /**
   * 删除歌曲
   */
  async deleteSong(songId: string): Promise<void> {
    return this.request<void>(`/api/songs/${songId}`, {
      method: "DELETE",
    });
  }

  // ============================================
  // 媒体资产 API
  // ============================================

  /**
   * 获取歌曲的所有媒体资产
   */
  async getSongAssets(songId: string): Promise<MediaAsset[]> {
    return this.request<MediaAsset[]>(`/api/stream/song/${songId}/assets`);
  }

  /**
   * 获取歌曲的主视频资产
   */
  async getSongVideo(songId: string): Promise<MediaAsset> {
    return this.request<MediaAsset>(`/api/stream/song/${songId}/video`);
  }

  /**
   * 获取歌曲的原唱音频资产
   */
  async getSongOriginalAudio(songId: string): Promise<MediaAsset> {
    return this.request<MediaAsset>(`/api/stream/song/${songId}/audio/original`);
  }

  /**
   * 获取歌曲的伴奏音频资产
   */
  async getSongInstrumentalAudio(songId: string): Promise<MediaAsset> {
    return this.request<MediaAsset>(
      `/api/stream/song/${songId}/audio/instrumental`
    );
  }

  /**
   * 获取媒体资产信息
   */
  async getAssetInfo(assetId: string): Promise<MediaAsset> {
    return this.request<MediaAsset>(`/api/stream/asset/${assetId}/info`);
  }

  /**
   * 获取媒体流 URL
   */
  getStreamUrl(assetId: string): string {
    return `${this.baseUrl}/api/stream/${assetId}`;
  }
}

// ============================================
// 导出单例实例
// ============================================

export const apiClient = new ApiClient(API_BASE_URL);

// 导出类型以便扩展
export { ApiClient };
