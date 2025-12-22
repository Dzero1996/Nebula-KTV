"use client";

import { forwardRef, useEffect, useRef, useCallback } from "react";
import { cn } from "@/lib/utils";
import { LyricsDisplay, type LyricLine } from "./LyricsDisplay";

// ============================================
// Types
// ============================================

export interface ImmersiveModeProps {
  /** 视频元素引用 - 用于全屏显示 */
  videoRef: React.RefObject<HTMLVideoElement | null>;
  /** 歌词数据 */
  lyrics: LyricLine[];
  /** 当前播放时间（秒） */
  currentTime: number;
  /** 是否显示沉浸模式 */
  isVisible: boolean;
  /** 是否正在播放 */
  isPlaying?: boolean;
  /** 点击事件回调 - 用于切换到交互模式 */
  onClick?: () => void;
  /** 自定义类名 */
  className?: string;
}

// ============================================
// Component
// ============================================

/**
 * 沉浸播放模式组件
 * 
 * 功能：
 * - 全屏视频背景
 * - 底部歌词显示区域 (20%)
 * - 当前句 48px+ 高亮，下一句半透明
 * 
 * Requirements: 4.2, 4.3, 4.4, 4.5
 */
export const ImmersiveMode = forwardRef<HTMLDivElement, ImmersiveModeProps>(
  function ImmersiveMode(
    { videoRef, lyrics, currentTime, isVisible, isPlaying = false, onClick, className },
    ref
  ) {
    const displayVideoRef = useRef<HTMLVideoElement>(null);

    // 同步视频播放状态
    const syncVideoState = useCallback(() => {
      const sourceVideo = videoRef.current;
      const displayVideo = displayVideoRef.current;

      if (!sourceVideo || !displayVideo) return;

      // 同步视频源
      if (displayVideo.src !== sourceVideo.src && sourceVideo.src) {
        displayVideo.src = sourceVideo.src;
      }

      // 同步播放时间（允许 0.1 秒误差）
      if (Math.abs(displayVideo.currentTime - sourceVideo.currentTime) > 0.1) {
        displayVideo.currentTime = sourceVideo.currentTime;
      }
    }, [videoRef]);

    // 同步播放/暂停状态
    useEffect(() => {
      const displayVideo = displayVideoRef.current;
      if (!displayVideo) return;

      if (isPlaying && displayVideo.paused) {
        displayVideo.play().catch(() => {
          // 忽略自动播放错误
        });
      } else if (!isPlaying && !displayVideo.paused) {
        displayVideo.pause();
      }
    }, [isPlaying]);

    // 定期同步视频状态
    useEffect(() => {
      if (!isVisible) return;

      syncVideoState();
      const interval = setInterval(syncVideoState, 100);

      return () => clearInterval(interval);
    }, [isVisible, syncVideoState]);

    return (
      <div
        ref={ref}
        className={cn(
          "fixed inset-0 z-10",
          "flex flex-col",
          "bg-black",
          "transition-opacity duration-300",
          isVisible ? "opacity-100" : "opacity-0 pointer-events-none",
          className
        )}
        onClick={onClick}
      >
        {/* 全屏视频背景 - 占据整个屏幕 */}
        <div className="absolute inset-0 z-0">
          <video
            ref={displayVideoRef}
            className="w-full h-full object-cover pointer-events-none"
            muted
            playsInline
          />
        </div>

        {/* 视频渐变遮罩 - 底部渐变，让歌词更清晰 */}
        <div
          className={cn(
            "absolute inset-x-0 bottom-0 z-10",
            "h-[40%]",
            "bg-gradient-to-t from-black/80 via-black/40 to-transparent",
            "pointer-events-none"
          )}
        />

        {/* 歌词显示区域 - 底部 20% */}
        <div
          className={cn(
            "absolute inset-x-0 bottom-0 z-20",
            "h-[20%] min-h-[120px]",
            "flex items-center justify-center",
            "px-8 pb-8"
          )}
        >
          <LyricsDisplay
            lyrics={lyrics}
            currentTime={currentTime}
            className="w-full max-w-4xl"
          />
        </div>
      </div>
    );
  }
);

export default ImmersiveMode;
