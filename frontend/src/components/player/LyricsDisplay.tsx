"use client";

import { useMemo, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

// ============================================
// Types
// ============================================

/**
 * 歌词行数据结构
 * JSON 格式歌词的单行数据
 */
export interface LyricLine {
  /** 开始时间（秒） */
  start: number;
  /** 结束时间（秒） */
  end: number;
  /** 歌词文本 */
  text: string;
}

export interface LyricsDisplayProps {
  /** JSON 格式歌词数据 */
  lyrics: LyricLine[];
  /** 当前播放时间（秒） */
  currentTime: number;
  /** 自定义类名 */
  className?: string;
}

// ============================================
// Helper Functions
// ============================================

/**
 * 根据当前时间找到当前歌词行索引
 */
function findCurrentLineIndex(lyrics: LyricLine[], currentTime: number): number {
  for (let i = lyrics.length - 1; i >= 0; i--) {
    if (currentTime >= lyrics[i].start) {
      return i;
    }
  }
  return -1;
}

// ============================================
// Component
// ============================================

export function LyricsDisplay({
  lyrics,
  currentTime,
  className,
}: LyricsDisplayProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const currentLineRef = useRef<HTMLDivElement>(null);

  // 计算当前歌词行索引
  const currentLineIndex = useMemo(
    () => findCurrentLineIndex(lyrics, currentTime),
    [lyrics, currentTime]
  );

  // 获取当前行和下一行歌词
  const currentLine = currentLineIndex >= 0 ? lyrics[currentLineIndex] : null;
  const nextLine =
    currentLineIndex >= 0 && currentLineIndex < lyrics.length - 1
      ? lyrics[currentLineIndex + 1]
      : null;

  // 平滑滚动到当前歌词行
  useEffect(() => {
    if (currentLineRef.current && containerRef.current) {
      currentLineRef.current.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [currentLineIndex]);

  // 如果没有歌词数据，显示占位符
  if (!lyrics || lyrics.length === 0) {
    return (
      <div
        className={cn(
          "flex items-center justify-center text-text-muted",
          className
        )}
      >
        <span className="text-lyrics-next">暂无歌词</span>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn(
        "flex flex-col items-center justify-end gap-4 overflow-hidden",
        className
      )}
    >
      {/* 当前歌词行 - 48px+ 高亮显示 */}
      <div
        ref={currentLineRef}
        className={cn(
          "text-lyrics-current text-center text-text-main",
          "transition-all duration-300 ease-out",
          "drop-shadow-[0_2px_8px_rgba(124,58,237,0.5)]",
          !currentLine && "opacity-0"
        )}
      >
        {currentLine?.text || "\u00A0"}
      </div>

      {/* 下一句歌词 - 较小字号半透明显示 */}
      <div
        className={cn(
          "text-lyrics-next text-center text-text-muted/60",
          "transition-all duration-300 ease-out",
          !nextLine && "opacity-0"
        )}
      >
        {nextLine?.text || "\u00A0"}
      </div>
    </div>
  );
}

// ============================================
// Utility: Parse JSON Lyrics
// ============================================

/**
 * 解析 JSON 格式歌词字符串
 * @param jsonString JSON 格式的歌词字符串
 * @returns 解析后的歌词行数组
 */
export function parseLyricsJson(jsonString: string): LyricLine[] {
  try {
    const parsed = JSON.parse(jsonString);
    
    // 验证数据格式
    if (!Array.isArray(parsed)) {
      console.error("Lyrics JSON is not an array");
      return [];
    }

    return parsed
      .filter(
        (line): line is LyricLine =>
          typeof line === "object" &&
          line !== null &&
          typeof line.start === "number" &&
          typeof line.end === "number" &&
          typeof line.text === "string"
      )
      .sort((a, b) => a.start - b.start);
  } catch (error) {
    console.error("Failed to parse lyrics JSON:", error);
    return [];
  }
}
