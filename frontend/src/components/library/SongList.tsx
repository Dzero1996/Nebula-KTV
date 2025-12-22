"use client";

/**
 * SongList 组件 - 歌曲列表
 * 列表项高度 > 100px，左侧封面 | 中间歌名+歌手+标签 | 右侧播放按钮
 * 处理中歌曲置灰显示
 * Requirements: 3.4, 3.5
 */

import * as React from "react";
import { Play, Music, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { Song } from "@/lib/api";
import { SongStatus } from "@/lib/api";
import {
  isSongPlayable,
  isSongProcessing,
  isSongFailed,
  getStatusText,
  formatDuration,
} from "@/hooks/use-songs";

interface SongListProps {
  /** 歌曲列表 */
  songs: Song[];
  /** 点击播放回调 */
  onPlay?: (song: Song) => void;
  /** 点击歌曲行回调 */
  onSongClick?: (song: Song) => void;
  /** 是否正在加载 */
  loading?: boolean;
  /** 空状态文本 */
  emptyText?: string;
  /** 自定义类名 */
  className?: string;
}

export function SongList({
  songs,
  onPlay,
  onSongClick,
  loading = false,
  emptyText = "暂无歌曲",
  className,
}: SongListProps) {
  if (loading) {
    return (
      <div className={cn("space-y-3", className)}>
        {/* 加载骨架屏 */}
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="h-[108px] rounded-xl bg-surface animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (songs.length === 0) {
    return (
      <div className={cn("py-12 text-center", className)}>
        <Music className="w-16 h-16 mx-auto text-text-muted opacity-50" />
        <p className="mt-4 text-song-meta text-text-muted">{emptyText}</p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-3", className)}>
      {songs.map((song) => (
        <SongListItem
          key={song.id}
          song={song}
          onPlay={() => onPlay?.(song)}
          onClick={() => onSongClick?.(song)}
        />
      ))}
    </div>
  );
}

interface SongListItemProps {
  song: Song;
  onPlay?: () => void;
  onClick?: () => void;
}

function SongListItem({ song, onPlay, onClick }: SongListItemProps) {
  const isPlayable = isSongPlayable(song);
  const isProcessing = isSongProcessing(song);
  const isFailed = isSongFailed(song);

  const handlePlayClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isPlayable && onPlay) {
      onPlay();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          onClick?.();
        }
      }}
      className={cn(
        // 列表项高度 > 100px
        "min-h-[108px] p-4 rounded-xl",
        "bg-surface border border-border",
        "flex items-center gap-4",
        "transition-all duration-200",
        "focus:outline-none focus-visible:ring-2 focus-visible:ring-primary",
        // 处理中或失败状态置灰
        (isProcessing || isFailed) && "opacity-60",
        // 可播放状态的悬停效果
        isPlayable && "hover:border-primary cursor-pointer press-effect"
      )}
    >
      {/* 左侧封面 */}
      <div
        className={cn(
          "flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden",
          "bg-muted"
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
            <Music className="w-8 h-8 text-text-muted" />
          </div>
        )}
      </div>

      {/* 中间歌曲信息 */}
      <div className="flex-1 min-w-0 space-y-1">
        <h3 className="text-song-title text-text-main text-truncate">
          {song.title}
        </h3>
        <p className="text-song-meta text-text-muted text-truncate">
          {song.artist}
        </p>
        
        {/* 标签区域 */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* 状态标签 */}
          <StatusBadge status={song.status} />
          
          {/* 画质标签 */}
          {song.quality_badge && (
            <span className="px-2 py-0.5 text-xs rounded bg-accent/20 text-accent">
              {song.quality_badge}
            </span>
          )}
          
          {/* 时长 */}
          {song.duration && (
            <span className="text-sm text-text-muted">
              {formatDuration(song.duration)}
            </span>
          )}
        </div>
      </div>

      {/* 右侧播放按钮 */}
      <div className="flex-shrink-0">
        <Button
          size="icon"
          variant={isPlayable ? "default" : "ghost"}
          disabled={!isPlayable}
          onClick={handlePlayClick}
          className={cn(
            "w-14 h-14 rounded-full",
            isPlayable && "bg-primary hover:bg-primary-glow glow-primary",
            !isPlayable && "bg-muted text-text-muted"
          )}
          aria-label={isPlayable ? "播放" : getStatusText(song.status)}
        >
          {isProcessing ? (
            <Loader2 className="w-6 h-6 animate-spin" />
          ) : (
            <Play className="w-6 h-6 ml-0.5" />
          )}
        </Button>
      </div>
    </div>
  );
}

interface StatusBadgeProps {
  status: SongStatus;
}

function StatusBadge({ status }: StatusBadgeProps) {
  const config = {
    [SongStatus.PENDING]: {
      text: "等待处理",
      className: "bg-muted text-text-muted",
    },
    [SongStatus.PROCESSING]: {
      text: "AI 处理中",
      className: "bg-accent/20 text-accent",
    },
    [SongStatus.READY]: {
      text: "",
      className: "",
    },
    [SongStatus.PARTIAL]: {
      text: "部分可用",
      className: "bg-yellow-500/20 text-yellow-400",
    },
    [SongStatus.FAILED]: {
      text: "处理失败",
      className: "bg-destructive/20 text-destructive",
    },
  };

  const { text, className } = config[status];

  // READY 状态不显示标签
  if (!text) {
    return null;
  }

  return (
    <span className={cn("px-2 py-0.5 text-xs rounded", className)}>
      {text}
    </span>
  );
}
