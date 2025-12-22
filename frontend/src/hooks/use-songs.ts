"use client";

/**
 * 歌曲数据 React Hooks
 * 提供歌曲列表、搜索、详情等功能
 */

import { useState, useEffect, useCallback } from "react";
import { apiClient, type Song, SongStatus } from "@/lib/api";

// ============================================
// 歌曲列表 Hook
// ============================================

interface UseSongsOptions {
  skip?: number;
  limit?: number;
}

interface UseSongsResult {
  songs: Song[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useSongs(options: UseSongsOptions = {}): UseSongsResult {
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSongs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getSongs({ skip: options.skip, limit: options.limit });
      setSongs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取歌曲列表失败");
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [options.skip, options.limit]);

  useEffect(() => {
    fetchSongs();
  }, [fetchSongs]);

  return { songs, loading, error, refetch: fetchSongs };
}

// ============================================
// 最近歌曲 Hook
// ============================================

interface UseRecentSongsResult {
  songs: Song[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useRecentSongs(limit: number = 10): UseRecentSongsResult {
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSongs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getRecentSongs(limit);
      setSongs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取最近歌曲失败");
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchSongs();
  }, [fetchSongs]);

  return { songs, loading, error, refetch: fetchSongs };
}

// ============================================
// 搜索歌曲 Hook
// ============================================

interface UseSearchSongsResult {
  songs: Song[];
  loading: boolean;
  error: string | null;
  search: (query: string) => Promise<void>;
  clear: () => void;
}

export function useSearchSongs(limit: number = 20): UseSearchSongsResult {
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(
    async (query: string) => {
      if (!query.trim()) {
        setSongs([]);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.searchSongs(query, limit);
        setSongs(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "搜索失败");
      } finally {
        setLoading(false);
      }
    },
    [limit]
  );

  const clear = useCallback(() => {
    setSongs([]);
    setError(null);
  }, []);

  return { songs, loading, error, search, clear };
}

// ============================================
// 单首歌曲 Hook
// ============================================

interface UseSongResult {
  song: Song | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useSong(songId: string | null): UseSongResult {
  const [song, setSong] = useState<Song | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSong = useCallback(async () => {
    if (!songId) {
      setSong(null);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getSong(songId);
      setSong(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取歌曲详情失败");
    } finally {
      setLoading(false);
    }
  }, [songId]);

  useEffect(() => {
    fetchSong();
  }, [fetchSong]);

  return { song, loading, error, refetch: fetchSong };
}

// ============================================
// 工具函数
// ============================================

/**
 * 检查歌曲是否可播放
 */
export function isSongPlayable(song: Song): boolean {
  return song.status === SongStatus.READY || song.status === SongStatus.PARTIAL;
}

/**
 * 检查歌曲是否正在处理中
 */
export function isSongProcessing(song: Song): boolean {
  return (
    song.status === SongStatus.PENDING || song.status === SongStatus.PROCESSING
  );
}

/**
 * 检查歌曲是否处理失败
 */
export function isSongFailed(song: Song): boolean {
  return song.status === SongStatus.FAILED;
}

/**
 * 格式化歌曲时长
 */
export function formatDuration(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined) {
    return "--:--";
  }

  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

/**
 * 获取状态显示文本
 */
export function getStatusText(status: SongStatus): string {
  switch (status) {
    case SongStatus.PENDING:
      return "等待处理";
    case SongStatus.PROCESSING:
      return "AI 处理中";
    case SongStatus.READY:
      return "可播放";
    case SongStatus.PARTIAL:
      return "部分可用";
    case SongStatus.FAILED:
      return "处理失败";
    default:
      return "未知状态";
  }
}
