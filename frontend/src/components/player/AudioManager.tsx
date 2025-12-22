"use client";

import {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";

// ============================================
// Types
// ============================================

export type VocalMode = "original" | "instrumental";

export interface AudioError {
  type: "video" | "original" | "instrumental";
  message: string;
}

export interface AudioManagerState {
  isReady: boolean;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  vocalMode: VocalMode;
  isBuffering: boolean;
  instrumentalAvailable: boolean;
}

export interface AudioManagerProps {
  videoSrc: string;
  originalSrc: string;
  instrumentalSrc: string;
  onReady?: () => void;
  onError?: (error: AudioError) => void;
  onTimeUpdate?: (currentTime: number) => void;
  onEnded?: () => void;
  children?: ReactNode;
}

interface AudioManagerContextValue extends AudioManagerState {
  play: () => Promise<void>;
  pause: () => void;
  seek: (time: number) => void;
  setVocalMode: (mode: VocalMode) => void;
  videoRef: React.RefObject<HTMLVideoElement | null>;
}

// ============================================
// Context
// ============================================

const AudioManagerContext = createContext<AudioManagerContextValue | null>(null);

export function useAudioManager() {
  const context = useContext(AudioManagerContext);
  if (!context) {
    throw new Error("useAudioManager must be used within AudioManagerProvider");
  }
  return context;
}

// ============================================
// Constants
// ============================================

const CROSSFADE_DURATION = 500; // ms

// ============================================
// Component
// ============================================

export function AudioManager({
  videoSrc,
  originalSrc,
  instrumentalSrc,
  onReady,
  onError,
  onTimeUpdate,
  onEnded,
  children,
}: AudioManagerProps) {
  // Refs for media elements
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const originalAudioRef = useRef<HTMLAudioElement | null>(null);
  const instrumentalAudioRef = useRef<HTMLAudioElement | null>(null);

  // Web Audio API refs
  const audioContextRef = useRef<AudioContext | null>(null);
  const originalGainRef = useRef<GainNode | null>(null);
  const instrumentalGainRef = useRef<GainNode | null>(null);

  // State
  const [state, setState] = useState<AudioManagerState>({
    isReady: false,
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    vocalMode: "original",
    isBuffering: false,
    instrumentalAvailable: true,
  });

  // Track loading state
  const loadingStateRef = useRef({
    video: false,
    original: false,
    instrumental: false,
  });

  // ============================================
  // Initialize Web Audio API
  // ============================================

  const initAudioContext = useCallback(() => {
    if (audioContextRef.current) return;

    const AudioContextClass =
      window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    audioContextRef.current = new AudioContextClass();

    // Create gain nodes for volume control
    originalGainRef.current = audioContextRef.current.createGain();
    instrumentalGainRef.current = audioContextRef.current.createGain();

    // Connect gain nodes to destination
    originalGainRef.current.connect(audioContextRef.current.destination);
    instrumentalGainRef.current.connect(audioContextRef.current.destination);

    // Set initial gain values (original on, instrumental off)
    originalGainRef.current.gain.value = 1;
    instrumentalGainRef.current.gain.value = 0;
  }, []);

  // ============================================
  // Connect audio elements to Web Audio API
  // ============================================

  const connectAudioSources = useCallback(() => {
    if (!audioContextRef.current) return;

    // Connect original audio
    if (originalAudioRef.current && originalGainRef.current) {
      try {
        const originalSource = audioContextRef.current.createMediaElementSource(
          originalAudioRef.current
        );
        originalSource.connect(originalGainRef.current);
      } catch {
        // Already connected
      }
    }

    // Connect instrumental audio
    if (instrumentalAudioRef.current && instrumentalGainRef.current) {
      try {
        const instrumentalSource = audioContextRef.current.createMediaElementSource(
          instrumentalAudioRef.current
        );
        instrumentalSource.connect(instrumentalGainRef.current);
      } catch {
        // Already connected
      }
    }
  }, []);

  // ============================================
  // Check if all sources are ready
  // ============================================

  const checkAllReady = useCallback(() => {
    const { video, original, instrumental } = loadingStateRef.current;
    const allReady = video && original && (instrumental || !state.instrumentalAvailable);

    if (allReady && !state.isReady) {
      connectAudioSources();
      setState((prev) => ({
        ...prev,
        isReady: true,
        duration: videoRef.current?.duration || 0,
      }));
      onReady?.();
    }
  }, [state.isReady, state.instrumentalAvailable, connectAudioSources, onReady]);

  // ============================================
  // Media event handlers
  // ============================================

  const handleVideoCanPlayThrough = useCallback(() => {
    loadingStateRef.current.video = true;
    checkAllReady();
  }, [checkAllReady]);

  const handleOriginalCanPlayThrough = useCallback(() => {
    loadingStateRef.current.original = true;
    checkAllReady();
  }, [checkAllReady]);

  const handleInstrumentalCanPlayThrough = useCallback(() => {
    loadingStateRef.current.instrumental = true;
    checkAllReady();
  }, [checkAllReady]);

  const handleInstrumentalError = useCallback(() => {
    // Degrade to original-only mode
    setState((prev) => ({
      ...prev,
      instrumentalAvailable: false,
      vocalMode: "original",
    }));
    loadingStateRef.current.instrumental = true; // Mark as "loaded" to allow playback
    onError?.({
      type: "instrumental",
      message: "伴奏加载失败，已切换到仅原唱模式",
    });
    checkAllReady();
  }, [onError, checkAllReady]);

  const handleVideoError = useCallback(() => {
    onError?.({
      type: "video",
      message: "视频加载失败",
    });
  }, [onError]);

  const handleOriginalError = useCallback(() => {
    onError?.({
      type: "original",
      message: "原唱音轨加载失败",
    });
  }, [onError]);

  // ============================================
  // Buffering state handlers
  // ============================================

  const handleWaiting = useCallback(() => {
    setState((prev) => ({ ...prev, isBuffering: true }));
    // Pause all tracks when any is buffering
    videoRef.current?.pause();
    originalAudioRef.current?.pause();
    instrumentalAudioRef.current?.pause();
  }, []);

  const handleCanPlay = useCallback(() => {
    setState((prev) => {
      if (prev.isBuffering && prev.isPlaying) {
        // Resume playback when buffering ends
        videoRef.current?.play();
        originalAudioRef.current?.play();
        if (prev.instrumentalAvailable) {
          instrumentalAudioRef.current?.play();
        }
      }
      return { ...prev, isBuffering: false };
    });
  }, []);

  // ============================================
  // Time update handler
  // ============================================

  const handleTimeUpdate = useCallback(() => {
    const currentTime = videoRef.current?.currentTime || 0;
    setState((prev) => ({ ...prev, currentTime }));
    onTimeUpdate?.(currentTime);
  }, [onTimeUpdate]);

  // ============================================
  // Ended handler
  // ============================================

  const handleEnded = useCallback(() => {
    setState((prev) => ({ ...prev, isPlaying: false }));
    onEnded?.();
  }, [onEnded]);

  // ============================================
  // Playback controls
  // ============================================

  const play = useCallback(async () => {
    if (!state.isReady) return;

    // Resume AudioContext if suspended
    if (audioContextRef.current?.state === "suspended") {
      await audioContextRef.current.resume();
    }

    // Sync all tracks to video time
    const currentTime = videoRef.current?.currentTime || 0;
    if (originalAudioRef.current) {
      originalAudioRef.current.currentTime = currentTime;
    }
    if (instrumentalAudioRef.current && state.instrumentalAvailable) {
      instrumentalAudioRef.current.currentTime = currentTime;
    }

    // Play all tracks
    await Promise.all([
      videoRef.current?.play(),
      originalAudioRef.current?.play(),
      state.instrumentalAvailable ? instrumentalAudioRef.current?.play() : Promise.resolve(),
    ]);

    setState((prev) => ({ ...prev, isPlaying: true }));
  }, [state.isReady, state.instrumentalAvailable]);

  const pause = useCallback(() => {
    videoRef.current?.pause();
    originalAudioRef.current?.pause();
    instrumentalAudioRef.current?.pause();
    setState((prev) => ({ ...prev, isPlaying: false }));
  }, []);

  const seek = useCallback(
    (time: number) => {
      if (videoRef.current) {
        videoRef.current.currentTime = time;
      }
      if (originalAudioRef.current) {
        originalAudioRef.current.currentTime = time;
      }
      if (instrumentalAudioRef.current && state.instrumentalAvailable) {
        instrumentalAudioRef.current.currentTime = time;
      }
      setState((prev) => ({ ...prev, currentTime: time }));
    },
    [state.instrumentalAvailable]
  );

  // ============================================
  // Crossfade vocal mode switch
  // ============================================

  const setVocalMode = useCallback(
    (mode: VocalMode) => {
      if (!state.instrumentalAvailable && mode === "instrumental") {
        return; // Cannot switch to instrumental if not available
      }

      if (!audioContextRef.current || !originalGainRef.current || !instrumentalGainRef.current) {
        return;
      }

      const currentTime = audioContextRef.current.currentTime;
      const fadeDuration = CROSSFADE_DURATION / 1000; // Convert to seconds

      if (mode === "instrumental") {
        // Fade out original, fade in instrumental
        originalGainRef.current.gain.linearRampToValueAtTime(0, currentTime + fadeDuration);
        instrumentalGainRef.current.gain.linearRampToValueAtTime(1, currentTime + fadeDuration);
      } else {
        // Fade out instrumental, fade in original
        originalGainRef.current.gain.linearRampToValueAtTime(1, currentTime + fadeDuration);
        instrumentalGainRef.current.gain.linearRampToValueAtTime(0, currentTime + fadeDuration);
      }

      setState((prev) => ({ ...prev, vocalMode: mode }));
    },
    [state.instrumentalAvailable]
  );

  // ============================================
  // Initialize on mount
  // ============================================

  useEffect(() => {
    initAudioContext();

    return () => {
      // Cleanup
      audioContextRef.current?.close();
    };
  }, [initAudioContext]);

  // ============================================
  // Context value
  // ============================================

  const contextValue: AudioManagerContextValue = {
    ...state,
    play,
    pause,
    seek,
    setVocalMode,
    videoRef,
  };

  return (
    <AudioManagerContext.Provider value={contextValue}>
      {/* Hidden video element (audio muted, video displayed elsewhere) */}
      <video
        ref={videoRef}
        src={videoSrc}
        muted
        playsInline
        onCanPlayThrough={handleVideoCanPlayThrough}
        onError={handleVideoError}
        onWaiting={handleWaiting}
        onCanPlay={handleCanPlay}
        onTimeUpdate={handleTimeUpdate}
        onEnded={handleEnded}
        style={{ display: "none" }}
      />

      {/* Hidden audio elements */}
      <audio
        ref={originalAudioRef}
        src={originalSrc}
        preload="auto"
        onCanPlayThrough={handleOriginalCanPlayThrough}
        onError={handleOriginalError}
        onWaiting={handleWaiting}
        onCanPlay={handleCanPlay}
      />

      <audio
        ref={instrumentalAudioRef}
        src={instrumentalSrc}
        preload="auto"
        onCanPlayThrough={handleInstrumentalCanPlayThrough}
        onError={handleInstrumentalError}
        onWaiting={handleWaiting}
        onCanPlay={handleCanPlay}
      />

      {children}
    </AudioManagerContext.Provider>
  );
}
