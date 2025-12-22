"use client";

/**
 * 自动隐藏定时器 Hook
 * 
 * 功能：
 * - 5 秒无操作自动进入沉浸模式
 * - 拖拽进度条时暂停计时
 * - 任意点击唤起交互模式
 * 
 * Requirements: 4.1, 5.1, 5.5, 5.6
 */

import { useState, useCallback, useRef, useEffect } from "react";

// ============================================
// Types
// ============================================

export type PlayerMode = "immersive" | "interactive";

export interface UseAutoHideOptions {
  /** 自动隐藏延迟时间（毫秒），默认 5000ms */
  hideDelay?: number;
  /** 初始模式，默认 interactive */
  initialMode?: PlayerMode;
  /** 是否启用自动隐藏，默认 true */
  enabled?: boolean;
}

export interface UseAutoHideResult {
  /** 当前播放器模式 */
  mode: PlayerMode;
  /** 是否处于交互模式 */
  isInteractive: boolean;
  /** 是否处于沉浸模式 */
  isImmersive: boolean;
  /** 切换到交互模式（任意点击唤起） */
  showControls: () => void;
  /** 切换到沉浸模式 */
  hideControls: () => void;
  /** 暂停自动隐藏计时（拖拽进度条时调用） */
  pauseAutoHide: () => void;
  /** 恢复自动隐藏计时 */
  resumeAutoHide: () => void;
  /** 重置自动隐藏计时器（用户有操作时调用） */
  resetTimer: () => void;
  /** 是否暂停了自动隐藏 */
  isPaused: boolean;
}

// ============================================
// Constants
// ============================================

const DEFAULT_HIDE_DELAY = 5000; // 5 秒

// ============================================
// Hook Implementation
// ============================================

export function useAutoHide(options: UseAutoHideOptions = {}): UseAutoHideResult {
  const {
    hideDelay = DEFAULT_HIDE_DELAY,
    initialMode = "interactive",
    enabled = true,
  } = options;

  // 当前模式状态
  const [mode, setMode] = useState<PlayerMode>(initialMode);
  
  // 是否暂停自动隐藏
  const [isPaused, setIsPaused] = useState(false);
  
  // 定时器引用
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ============================================
  // 清除定时器
  // ============================================
  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  // ============================================
  // 启动自动隐藏定时器
  // ============================================
  const startTimer = useCallback(() => {
    // 如果禁用或暂停，不启动定时器
    if (!enabled || isPaused) return;

    // 清除现有定时器
    clearTimer();

    // 启动新定时器
    timerRef.current = setTimeout(() => {
      setMode("immersive");
    }, hideDelay);
  }, [enabled, isPaused, hideDelay, clearTimer]);

  // ============================================
  // 切换到交互模式（任意点击唤起）
  // Requirements: 5.1
  // ============================================
  const showControls = useCallback(() => {
    setMode("interactive");
    startTimer();
  }, [startTimer]);

  // ============================================
  // 切换到沉浸模式
  // Requirements: 4.1
  // ============================================
  const hideControls = useCallback(() => {
    clearTimer();
    setMode("immersive");
  }, [clearTimer]);

  // ============================================
  // 暂停自动隐藏计时（拖拽进度条时）
  // Requirements: 5.6
  // ============================================
  const pauseAutoHide = useCallback(() => {
    setIsPaused(true);
    clearTimer();
  }, [clearTimer]);

  // ============================================
  // 恢复自动隐藏计时
  // ============================================
  const resumeAutoHide = useCallback(() => {
    setIsPaused(false);
    // 恢复后重新启动定时器
    if (mode === "interactive") {
      startTimer();
    }
  }, [mode, startTimer]);

  // ============================================
  // 重置定时器（用户有操作时）
  // Requirements: 5.5
  // ============================================
  const resetTimer = useCallback(() => {
    if (mode === "interactive" && !isPaused) {
      startTimer();
    }
  }, [mode, isPaused, startTimer]);

  // ============================================
  // 模式变化时管理定时器
  // ============================================
  useEffect(() => {
    if (mode === "interactive" && enabled && !isPaused) {
      startTimer();
    } else {
      clearTimer();
    }

    return () => {
      clearTimer();
    };
  }, [mode, enabled, isPaused, startTimer, clearTimer]);

  // ============================================
  // 组件卸载时清理
  // ============================================
  useEffect(() => {
    return () => {
      clearTimer();
    };
  }, [clearTimer]);

  return {
    mode,
    isInteractive: mode === "interactive",
    isImmersive: mode === "immersive",
    showControls,
    hideControls,
    pauseAutoHide,
    resumeAutoHide,
    resetTimer,
    isPaused,
  };
}
