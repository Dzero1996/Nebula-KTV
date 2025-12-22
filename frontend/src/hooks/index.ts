/**
 * Nebula KTV React Hooks
 * 统一导出所有自定义 Hooks
 */

export {
  useSongs,
  useRecentSongs,
  useSearchSongs,
  useSong,
  isSongPlayable,
  isSongProcessing,
  isSongFailed,
  formatDuration,
  getStatusText,
} from "./use-songs";

export {
  useAutoHide,
  type PlayerMode,
  type UseAutoHideOptions,
  type UseAutoHideResult,
} from "./use-auto-hide";
