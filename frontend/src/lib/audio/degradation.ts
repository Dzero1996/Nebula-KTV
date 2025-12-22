/**
 * 音频降级策略工具
 * 处理伴奏加载失败时的降级逻辑
 */

export type DegradationMode = "full" | "original-only" | "instrumental-only" | "error";

export interface DegradationState {
  mode: DegradationMode;
  videoAvailable: boolean;
  originalAvailable: boolean;
  instrumentalAvailable: boolean;
  canSwitchVocal: boolean;
  errorMessage?: string;
}

export interface TrackAvailability {
  video: boolean;
  original: boolean;
  instrumental: boolean;
}

/**
 * 根据轨道可用性计算降级状态
 * 
 * @param availability - 各轨道的可用性
 * @returns 降级状态
 */
export function calculateDegradationState(
  availability: TrackAvailability
): DegradationState {
  const { video, original, instrumental } = availability;

  // Video is required for playback
  if (!video) {
    return {
      mode: "error",
      videoAvailable: false,
      originalAvailable: original,
      instrumentalAvailable: instrumental,
      canSwitchVocal: false,
      errorMessage: "视频加载失败，无法播放",
    };
  }

  // At least one audio track is required
  if (!original && !instrumental) {
    return {
      mode: "error",
      videoAvailable: true,
      originalAvailable: false,
      instrumentalAvailable: false,
      canSwitchVocal: false,
      errorMessage: "音频加载失败，无法播放",
    };
  }

  // Full mode: all tracks available
  if (original && instrumental) {
    return {
      mode: "full",
      videoAvailable: true,
      originalAvailable: true,
      instrumentalAvailable: true,
      canSwitchVocal: true,
    };
  }

  // Original-only mode: instrumental failed
  if (original && !instrumental) {
    return {
      mode: "original-only",
      videoAvailable: true,
      originalAvailable: true,
      instrumentalAvailable: false,
      canSwitchVocal: false,
      errorMessage: "伴奏加载失败，已切换到仅原唱模式",
    };
  }

  // Instrumental-only mode: original failed
  return {
    mode: "instrumental-only",
    videoAvailable: true,
    originalAvailable: false,
    instrumentalAvailable: true,
    canSwitchVocal: false,
    errorMessage: "原唱加载失败，已切换到仅伴奏模式",
  };
}

/**
 * 检查是否可以切换到指定的声音模式
 * 
 * @param targetMode - 目标模式 ("original" | "instrumental")
 * @param state - 当前降级状态
 * @returns 是否可以切换
 */
export function canSwitchToMode(
  targetMode: "original" | "instrumental",
  state: DegradationState
): boolean {
  if (!state.canSwitchVocal) {
    return false;
  }

  if (targetMode === "original") {
    return state.originalAvailable;
  }

  return state.instrumentalAvailable;
}

/**
 * 获取降级后的默认声音模式
 * 
 * @param state - 降级状态
 * @returns 默认声音模式
 */
export function getDefaultVocalMode(
  state: DegradationState
): "original" | "instrumental" | null {
  if (state.mode === "error") {
    return null;
  }

  if (state.originalAvailable) {
    return "original";
  }

  if (state.instrumentalAvailable) {
    return "instrumental";
  }

  return null;
}

/**
 * 生成用户友好的降级提示消息
 * 
 * @param state - 降级状态
 * @returns 提示消息
 */
export function getDegradationMessage(state: DegradationState): string | null {
  switch (state.mode) {
    case "full":
      return null;
    case "original-only":
      return "伴奏加载失败，已切换到仅原唱模式";
    case "instrumental-only":
      return "原唱加载失败，已切换到仅伴奏模式";
    case "error":
      return state.errorMessage || "播放器加载失败";
    default:
      return null;
  }
}
