"use client";

/**
 * RecentSection 组件 - 最近添加区域
 * 横向滚动容器，正方形大封面卡片
 * Requirements: 3.3
 */

import * as React from "react";
import { Music } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Song } from "@/lib/api";
import { isSongProcessing } from "@/hooks/use-songs";

interface RecentSectionProps {
  /** 歌曲列表 */
  songs: Song[];
  /** 点击歌曲回调 */
  onSongClick?: (song: Song) => void;
  /** 是否正在加载 */
  loading?: boolean;
  /** 自定义类名 */
  className?: string;
}

export function RecentSection({
  songs,
  onSongClick,
  loading = false,
  className,
}: RecentSectionProps) {
  if (loading) {
    return (
      <section className={cn("space-y-4", className)}>
        <h2 className="text-song-title text-text-main px-1">最近添加</h2>
        <div className="flex gap-4 overflow-x-auto scrollbar-hide pb-2">
          {/* 加载骨架屏 */}
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="flex-shrink-0 w-36 h-36 rounded-xl bg-surface animate-pulse"
            />
          ))}
        </div>
      </section>
    );
  }

  if (songs.length === 0) {
    return null;
  }

  return (
    <section className={cn("space-y-4", className)}>
      <h2 className="text-song-title text-text-main px-1">最近添加</h2>
      
      {/* 横向滚动容器 */}
      <div className="flex gap-4 overflow-x-auto scrollbar-hide pb-2 -mx-1 px-1">
        {songs.map((song) => (
          <RecentSongCard
            key={song.id}
            song={song}
            onClick={() => onSongClick?.(song)}
          />
        ))}
      </div>
    </section>
  );
}

interface RecentSongCardProps {
  song: Song;
  onClick?: () => void;
}

function RecentSongCard({ song, onClick }: RecentSongCardProps) {
  const isProcessing = isSongProcessing(song);

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={isProcessing}
      className={cn(
        "flex-shrink-0 w-36 group",
        "focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-xl",
        "press-effect",
        isProcessing && "opacity-50 cursor-not-allowed"
      )}
    >
      {/* 正方形封面 */}
      <div
        className={cn(
          "relative w-36 h-36 rounded-xl overflow-hidden",
          "bg-surface border border-border",
          "transition-all duration-200",
          !isProcessing && "group-hover:border-primary group-hover:glow-primary"
        )}
      >
        {song.cover_path ? (
          <img
            src={song.cover_path}
            alt={song.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/20 to-accent/20">
            <Music className="w-12 h-12 text-text-muted" />
          </div>
        )}

        {/* 处理中遮罩 */}
        {isProcessing && (
          <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
            <span className="text-sm text-text-muted">处理中...</span>
          </div>
        )}
      </div>

      {/* 歌曲信息 */}
      <div className="mt-2 text-left">
        <p className="text-song-meta text-text-main text-truncate">
          {song.title}
        </p>
        <p className="text-sm text-text-muted text-truncate">
          {song.artist}
        </p>
      </div>
    </button>
  );
}
