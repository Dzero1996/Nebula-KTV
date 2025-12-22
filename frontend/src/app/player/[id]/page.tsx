"use client";

/**
 * 播放器页面
 * 
 * 功能：
 * - 集成 AudioManager、ImmersiveMode、ControlBar
 * - 管理播放状态和模式切换
 * - 处理错误和降级
 * 
 * Requirements: 4.1, 5.1
 */

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { AudioManager, useAudioManager, type AudioError } from "@/components/player/AudioManager";
import { ImmersiveMode } from "@/components/player/ImmersiveMode";
import { ControlBar, type VocalMode } from "@/components/player/ControlBar";
import { type LyricLine, parseLyricsJson } from "@/components/player/LyricsDisplay";
import { useAutoHide } from "@/hooks/use-auto-hide";
import { useSong } from "@/hooks/use-songs";
import { apiClient, SongStatus } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Loader2, AlertCircle } from "lucide-react";

// ============================================
// Types
// ============================================

interface MediaUrls {
  video: string;
  original: string;
  instrumental: string;
}

// ============================================
// Loading Component
// ============================================

function LoadingScreen() {
  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="w-12 h-12 text-cyan-400 animate-spin" />
        <p className="text-white/70 text-lg">加载中...</p>
      </div>
    </div>
  );
}

// ============================================
// Error Component
// ============================================

interface ErrorScreenProps {
  message: string;
  onBack: () => void;
}

function ErrorScreen({ message, onBack }: ErrorScreenProps) {
  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center">
      <div className="flex flex-col items-center gap-6 max-w-md px-8 text-center">
        <AlertCircle className="w-16 h-16 text-red-400" />
        <h1 className="text-2xl font-semibold text-white">播放失败</h1>
        <p className="text-white/70">{message}</p>
        <button
          onClick={onBack}
          className={cn(
            "px-8 py-3 rounded-full",
            "bg-white/10 hover:bg-white/20",
            "text-white font-medium",
            "transition-colors duration-200"
          )}
        >
          返回
        </button>
      </div>
    </div>
  );
}

// ============================================
// Buffering Overlay
// ============================================

function BufferingOverlay() {
  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center pointer-events-none">
      <div className="flex flex-col items-center gap-3">
        <Loader2 className="w-10 h-10 text-white animate-spin" />
        <p className="text-white/80 text-sm">缓冲中...</p>
      </div>
    </div>
  );
}

// ============================================
// Degradation Toast
// ============================================

interface DegradationToastProps {
  message: string;
  visible: boolean;
}

function DegradationToast({ message, visible }: DegradationToastProps) {
  if (!visible) return null;

  return (
    <div
      className={cn(
        "fixed top-4 left-1/2 -translate-x-1/2 z-50",
        "px-6 py-3 rounded-full",
        "bg-yellow-500/90 text-black font-medium",
        "shadow-lg",
        "animate-in fade-in slide-in-from-top-2 duration-300"
      )}
    >
      {message}
    </div>
  );
}


// ============================================
// Player Content Component
// ============================================

interface PlayerContentProps {
  title: string;
  artist: string;
  lyrics: LyricLine[];
  onBack: () => void;
  onNext?: () => void;
}

function PlayerContent({ title, artist, lyrics, onBack, onNext }: PlayerContentProps) {
  const {
    isReady,
    isPlaying,
    currentTime,
    duration,
    vocalMode,
    isBuffering,
    instrumentalAvailable,
    play,
    pause,
    seek,
    setVocalMode,
    videoRef,
  } = useAudioManager();

  // 自动隐藏定时器
  const {
    isInteractive,
    isImmersive,
    showControls,
    pauseAutoHide,
    resumeAutoHide,
  } = useAutoHide({
    hideDelay: 5000,
    initialMode: "interactive",
    enabled: isReady,
  });

  // ============================================
  // Handlers
  // ============================================

  const handlePlayPause = useCallback(() => {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }, [isPlaying, play, pause]);

  const handleSeek = useCallback(
    (time: number) => {
      seek(time);
    },
    [seek]
  );

  const handleVocalModeChange = useCallback(
    (newMode: VocalMode) => {
      setVocalMode(newMode);
    },
    [setVocalMode]
  );

  const handleDraggingChange = useCallback(
    (isDragging: boolean) => {
      if (isDragging) {
        pauseAutoHide();
      } else {
        resumeAutoHide();
      }
    },
    [pauseAutoHide, resumeAutoHide]
  );

  // 点击屏幕切换到交互模式
  const handleScreenClick = useCallback(() => {
    if (isImmersive) {
      showControls();
    }
  }, [isImmersive, showControls]);

  // ============================================
  // Render
  // ============================================

  return (
    <div className="fixed inset-0 bg-black">
      {/* 缓冲中遮罩 */}
      {isBuffering && <BufferingOverlay />}

      {/* 沉浸模式 - 全屏视频和歌词 */}
      <ImmersiveMode
        videoRef={videoRef}
        lyrics={lyrics}
        currentTime={currentTime}
        isVisible={isImmersive}
        isPlaying={isPlaying}
        onClick={handleScreenClick}
      />

      {/* 交互模式 - 控制栏 */}
      <ControlBar
        title={title}
        artist={artist}
        currentTime={currentTime}
        duration={duration}
        isPlaying={isPlaying}
        vocalMode={vocalMode}
        instrumentalAvailable={instrumentalAvailable}
        isVisible={isInteractive}
        onPlayPause={handlePlayPause}
        onSeek={handleSeek}
        onVocalModeChange={handleVocalModeChange}
        onNext={onNext}
        onBack={onBack}
        onDraggingChange={handleDraggingChange}
      />

      {/* 交互模式下的点击区域 - 用于切换到沉浸模式 */}
      {isInteractive && (
        <div
          className="fixed inset-0 z-10"
          onClick={handleScreenClick}
          style={{ pointerEvents: "none" }}
        />
      )}
    </div>
  );
}


// ============================================
// Main Page Component
// ============================================

export default function PlayerPage() {
  const params = useParams();
  const router = useRouter();
  const songId = params.id as string;

  // 歌曲数据
  const { song, loading: songLoading, error: songError } = useSong(songId);

  // 媒体 URL 状态
  const [mediaUrls, setMediaUrls] = useState<MediaUrls | null>(null);
  const [mediaLoading, setMediaLoading] = useState(true);
  const [mediaError, setMediaError] = useState<string | null>(null);

  // 歌词数据
  const [lyrics, setLyrics] = useState<LyricLine[]>([]);

  // 降级提示
  const [degradationMessage, setDegradationMessage] = useState<string | null>(null);
  const [showDegradation, setShowDegradation] = useState(false);

  // ============================================
  // 加载媒体资产
  // ============================================

  useEffect(() => {
    if (!songId) return;

    async function loadMediaAssets() {
      setMediaLoading(true);
      setMediaError(null);

      try {
        // 获取所有媒体资产
        const assets = await apiClient.getSongAssets(songId);

        // 查找各类型资产
        const videoAsset = assets.find((a) => a.type === "video_master");
        const originalAsset = assets.find((a) => a.type === "audio_original");
        const instrumentalAsset = assets.find((a) => a.type === "audio_inst");
        const lyricsAsset = assets.find(
          (a) => a.type === "lyrics_word_level" || a.type === "lyrics_vtt"
        );

        // 验证必需资产
        if (!videoAsset) {
          throw new Error("视频资源不存在");
        }
        if (!originalAsset) {
          throw new Error("原唱音轨不存在");
        }

        // 构建媒体 URL
        setMediaUrls({
          video: apiClient.getStreamUrl(videoAsset.id),
          original: apiClient.getStreamUrl(originalAsset.id),
          instrumental: instrumentalAsset
            ? apiClient.getStreamUrl(instrumentalAsset.id)
            : "", // 空字符串表示不可用
        });

        // 加载歌词（如果有）
        if (lyricsAsset) {
          try {
            const response = await fetch(apiClient.getStreamUrl(lyricsAsset.id));
            const lyricsText = await response.text();
            const parsedLyrics = parseLyricsJson(lyricsText);
            setLyrics(parsedLyrics);
          } catch {
            // 歌词加载失败不影响播放
            console.warn("歌词加载失败");
          }
        }
      } catch (err) {
        setMediaError(err instanceof Error ? err.message : "加载媒体资源失败");
      } finally {
        setMediaLoading(false);
      }
    }

    loadMediaAssets();
  }, [songId]);

  // ============================================
  // 处理音频错误（降级）
  // ============================================

  const handleAudioError = useCallback((error: AudioError) => {
    if (error.type === "instrumental") {
      // 伴奏加载失败 - 降级到仅原唱模式
      setDegradationMessage(error.message);
      setShowDegradation(true);

      // 3 秒后隐藏提示
      setTimeout(() => {
        setShowDegradation(false);
      }, 3000);
    } else if (error.type === "video" || error.type === "original") {
      // 视频或原唱加载失败 - 显示错误
      setMediaError(error.message);
    }
  }, []);

  // ============================================
  // 导航处理
  // ============================================

  const handleBack = useCallback(() => {
    router.push("/");
  }, [router]);

  const handleNext = useCallback(() => {
    // TODO: 实现下一首功能
    // 目前只是返回首页
    router.push("/");
  }, [router]);

  // ============================================
  // 渲染
  // ============================================

  // 加载中
  if (songLoading || mediaLoading) {
    return <LoadingScreen />;
  }

  // 歌曲加载错误
  if (songError) {
    return <ErrorScreen message={songError} onBack={handleBack} />;
  }

  // 媒体加载错误
  if (mediaError) {
    return <ErrorScreen message={mediaError} onBack={handleBack} />;
  }

  // 歌曲不存在
  if (!song) {
    return <ErrorScreen message="歌曲不存在" onBack={handleBack} />;
  }

  // 歌曲未就绪
  if (song.status !== SongStatus.READY && song.status !== SongStatus.PARTIAL) {
    return (
      <ErrorScreen
        message={
          song.status === SongStatus.PROCESSING
            ? "AI 正在处理中，请稍候..."
            : song.status === SongStatus.PENDING
            ? "歌曲等待处理中..."
            : "歌曲处理失败"
        }
        onBack={handleBack}
      />
    );
  }

  // 媒体 URL 未加载
  if (!mediaUrls) {
    return <ErrorScreen message="媒体资源加载失败" onBack={handleBack} />;
  }

  return (
    <>
      {/* 降级提示 */}
      <DegradationToast message={degradationMessage || ""} visible={showDegradation} />

      {/* 播放器 */}
      <AudioManager
        videoSrc={mediaUrls.video}
        originalSrc={mediaUrls.original}
        instrumentalSrc={mediaUrls.instrumental}
        onError={handleAudioError}
      >
        <PlayerContent
          title={song.title}
          artist={song.artist}
          lyrics={lyrics}
          onBack={handleBack}
          onNext={handleNext}
        />
      </AudioManager>
    </>
  );
}
