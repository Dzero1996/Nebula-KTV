"use client";

import { forwardRef, useCallback, useState, useRef } from "react";
import { cn } from "@/lib/utils";
import {
  Play,
  Pause,
  SkipForward,
  ChevronLeft,
} from "lucide-react";

// ============================================
// Types
// ============================================

export type VocalMode = "original" | "instrumental";

export interface ControlBarProps {
  /** 歌曲标题 */
  title: string;
  /** 歌手名 */
  artist?: string;
  /** 当前播放时间（秒） */
  currentTime: number;
  /** 总时长（秒） */
  duration: number;
  /** 是否正在播放 */
  isPlaying: boolean;
  /** 当前人声模式 */
  vocalMode: VocalMode;
  /** 伴奏是否可用 */
  instrumentalAvailable?: boolean;
  /** 是否显示控制栏 */
  isVisible: boolean;
  /** 播放/暂停回调 */
  onPlayPause: () => void;
  /** 跳转回调 */
  onSeek: (time: number) => void;
  /** 切换人声模式回调 */
  onVocalModeChange: (mode: VocalMode) => void;
  /** 下一首回调 */
  onNext?: () => void;
  /** 返回回调 */
  onBack?: () => void;
  /** 拖拽状态变化回调 - 用于暂停自动隐藏 */
  onDraggingChange?: (isDragging: boolean) => void;
  /** 自定义类名 */
  className?: string;
}

// ============================================
// Helper Functions
// ============================================

/**
 * 格式化时间为 mm:ss 格式
 */
function formatTime(seconds: number): string {
  if (!isFinite(seconds) || seconds < 0) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

// ============================================
// Sub-Components
// ============================================

/**
 * 顶部遮罩组件 - 返回按钮和歌曲标题
 * Requirements: 5.2
 */
interface TopOverlayProps {
  title: string;
  artist?: string;
  onBack?: () => void;
}

function TopOverlay({ title, artist, onBack }: TopOverlayProps) {
  return (
    <div
      className={cn(
        "absolute top-0 inset-x-0 z-30",
        "h-20",
        "bg-gradient-to-b from-black/70 to-transparent",
        "flex items-center px-6",
        "pointer-events-auto"
      )}
    >
      {/* 返回按钮 */}
      <button
        onClick={onBack}
        className={cn(
          "flex items-center justify-center",
          "w-14 h-14 min-w-[60px] min-h-[60px]",
          "rounded-full",
          "bg-white/10 hover:bg-white/20",
          "transition-all duration-150",
          "active:scale-95"
        )}
        aria-label="返回"
      >
        <ChevronLeft className="w-8 h-8 text-white" />
      </button>

      {/* 歌曲标题 */}
      <div className="ml-4 flex-1 min-w-0">
        <h1 className="text-xl font-semibold text-white truncate">{title}</h1>
        {artist && (
          <p className="text-sm text-white/70 truncate">{artist}</p>
        )}
      </div>
    </div>
  );
}

/**
 * 进度条组件 - 粗线条，加大滑块
 * Requirements: 5.4
 */
interface ProgressBarProps {
  currentTime: number;
  duration: number;
  onSeek: (time: number) => void;
  onDraggingChange?: (isDragging: boolean) => void;
}

function ProgressBar({ currentTime, duration, onSeek, onDraggingChange }: ProgressBarProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [dragValue, setDragValue] = useState(0);
  const trackRef = useRef<HTMLDivElement>(null);

  const progress = duration > 0 ? (isDragging ? dragValue : currentTime) / duration : 0;

  const handlePointerDown = useCallback(
    (e: React.PointerEvent) => {
      if (!trackRef.current || duration <= 0) return;

      const rect = trackRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percent = Math.max(0, Math.min(1, x / rect.width));
      const newTime = percent * duration;

      setIsDragging(true);
      setDragValue(newTime);
      onDraggingChange?.(true);

      (e.target as HTMLElement).setPointerCapture(e.pointerId);
    },
    [duration, onDraggingChange]
  );

  const handlePointerMove = useCallback(
    (e: React.PointerEvent) => {
      if (!isDragging || !trackRef.current || duration <= 0) return;

      const rect = trackRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percent = Math.max(0, Math.min(1, x / rect.width));
      const newTime = percent * duration;

      setDragValue(newTime);
    },
    [isDragging, duration]
  );

  const handlePointerUp = useCallback(() => {
    if (isDragging) {
      onSeek(dragValue);
      setIsDragging(false);
      onDraggingChange?.(false);
    }
  }, [isDragging, dragValue, onSeek, onDraggingChange]);

  return (
    <div className="w-full px-4">
      {/* 时间显示 */}
      <div className="flex justify-between text-sm text-white/70 mb-2">
        <span>{formatTime(isDragging ? dragValue : currentTime)}</span>
        <span>{formatTime(duration)}</span>
      </div>

      {/* 进度条轨道 */}
      <div
        ref={trackRef}
        className={cn(
          "relative w-full h-3 cursor-pointer",
          "touch-none select-none"
        )}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
      >
        {/* 背景轨道 */}
        <div className="absolute inset-y-0 inset-x-0 rounded-full bg-white/20" />

        {/* 已播放部分 */}
        <div
          className="absolute inset-y-0 left-0 rounded-full bg-cyan-400"
          style={{ width: `${progress * 100}%` }}
        />

        {/* 滑块 - 加大尺寸 */}
        <div
          className={cn(
            "absolute top-1/2 -translate-y-1/2 -translate-x-1/2",
            "w-7 h-7",
            "rounded-full bg-white",
            "shadow-lg shadow-black/30",
            "transition-transform duration-100",
            isDragging && "scale-110"
          )}
          style={{ left: `${progress * 100}%` }}
        />
      </div>
    </div>
  );
}

/**
 * 原唱/伴奏开关 - 胶囊形状 Toggle
 * Requirements: 5.4, 6.4
 */
interface VocalToggleProps {
  mode: VocalMode;
  disabled?: boolean;
  onChange: (mode: VocalMode) => void;
}

function VocalToggle({ mode, disabled, onChange }: VocalToggleProps) {
  const isInstrumental = mode === "instrumental";

  const handleClick = useCallback(() => {
    if (disabled) return;
    onChange(isInstrumental ? "original" : "instrumental");
  }, [disabled, isInstrumental, onChange]);

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        onClick={handleClick}
        disabled={disabled}
        className={cn(
          "relative w-20 h-10 rounded-full",
          "transition-all duration-300",
          disabled
            ? "bg-gray-600 cursor-not-allowed opacity-50"
            : isInstrumental
            ? "bg-cyan-500"
            : "bg-gray-500",
          "active:scale-95"
        )}
        aria-label={isInstrumental ? "切换到原唱" : "切换到伴奏"}
      >
        {/* 滑块 */}
        <div
          className={cn(
            "absolute top-1 w-8 h-8 rounded-full bg-white",
            "shadow-md",
            "transition-all duration-300",
            isInstrumental ? "left-11" : "left-1"
          )}
        />
      </button>
      <span className="text-xs text-white/70">
        {disabled ? "仅原唱" : isInstrumental ? "伴奏" : "原唱"}
      </span>
    </div>
  );
}

/**
 * 播放控制按钮组
 * Requirements: 5.4, 7.1, 7.2
 */
interface PlayControlsProps {
  isPlaying: boolean;
  onPlayPause: () => void;
  onNext?: () => void;
}

function PlayControls({ isPlaying, onPlayPause, onNext }: PlayControlsProps) {
  return (
    <div className="flex items-center justify-center gap-8">
      {/* 播放/暂停按钮 - 最大尺寸 */}
      <button
        onClick={onPlayPause}
        className={cn(
          "flex items-center justify-center",
          "w-20 h-20 min-w-[80px] min-h-[80px]",
          "rounded-full",
          "bg-white text-black",
          "shadow-lg shadow-black/30",
          "transition-all duration-150",
          "active:scale-90"
        )}
        aria-label={isPlaying ? "暂停" : "播放"}
      >
        {isPlaying ? (
          <Pause className="w-10 h-10" fill="currentColor" />
        ) : (
          <Play className="w-10 h-10 ml-1" fill="currentColor" />
        )}
      </button>

      {/* 下一首按钮 */}
      <button
        onClick={onNext}
        className={cn(
          "flex items-center justify-center",
          "w-16 h-16 min-w-[64px] min-h-[64px]",
          "rounded-full",
          "bg-white/20 hover:bg-white/30",
          "transition-all duration-150",
          "active:scale-90"
        )}
        aria-label="下一首"
      >
        <SkipForward className="w-8 h-8 text-white" fill="currentColor" />
      </button>
    </div>
  );
}

// ============================================
// Main Component
// ============================================

/**
 * 交互模式控制栏组件
 *
 * 功能：
 * - 底部控制栏，高度 >= 25%
 * - 玻璃拟态背景 (bg-black/60 backdrop-blur-md)
 * - 进度条、原唱/伴奏开关、播放控制
 * - 顶部遮罩（返回按钮、歌曲标题）
 *
 * Requirements: 5.2, 5.3, 5.4, 6.4, 7.1, 7.2
 */
export const ControlBar = forwardRef<HTMLDivElement, ControlBarProps>(
  function ControlBar(
    {
      title,
      artist,
      currentTime,
      duration,
      isPlaying,
      vocalMode,
      instrumentalAvailable = true,
      isVisible,
      onPlayPause,
      onSeek,
      onVocalModeChange,
      onNext,
      onBack,
      onDraggingChange,
      className,
    },
    ref
  ) {
    return (
      <div
        ref={ref}
        className={cn(
          "fixed inset-0 z-20",
          "pointer-events-none",
          "transition-opacity duration-300",
          isVisible ? "opacity-100" : "opacity-0",
          className
        )}
      >
        {/* 顶部遮罩 - Requirements: 5.2 */}
        {isVisible && (
          <TopOverlay title={title} artist={artist} onBack={onBack} />
        )}

        {/* 底部控制栏 - Requirements: 5.3 */}
        {isVisible && (
          <div
            className={cn(
              "absolute bottom-0 inset-x-0",
              "min-h-[25vh] h-auto",
              "bg-black/60 backdrop-blur-md",
              "flex flex-col justify-end",
              "pb-8 pt-6",
              "pointer-events-auto"
            )}
          >
            {/* 进度条 - Requirements: 5.4 */}
            <div className="mb-8">
              <ProgressBar
                currentTime={currentTime}
                duration={duration}
                onSeek={onSeek}
                onDraggingChange={onDraggingChange}
              />
            </div>

            {/* 控制按钮区域 */}
            <div className="flex items-center justify-between px-8">
              {/* 原唱/伴奏开关 - Requirements: 5.4, 6.4 */}
              <VocalToggle
                mode={vocalMode}
                disabled={!instrumentalAvailable}
                onChange={onVocalModeChange}
              />

              {/* 播放控制 - Requirements: 5.4, 7.1, 7.2 */}
              <PlayControls
                isPlaying={isPlaying}
                onPlayPause={onPlayPause}
                onNext={onNext}
              />

              {/* 占位，保持布局平衡 */}
              <div className="w-20" />
            </div>
          </div>
        )}
      </div>
    );
  }
);

export default ControlBar;
