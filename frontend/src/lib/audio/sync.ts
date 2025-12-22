/**
 * 三轨同步播放工具
 * 确保视频、原唱、伴奏三个媒体源同步播放
 */

export interface MediaTrack {
  element: HTMLMediaElement;
  name: string;
  required: boolean;
}

export interface SyncState {
  allReady: boolean;
  anyBuffering: boolean;
  readyTracks: string[];
  bufferingTracks: string[];
}

/**
 * 检查所有必需的媒体轨道是否已就绪
 */
export function checkTracksReady(tracks: MediaTrack[]): SyncState {
  const readyTracks: string[] = [];
  const bufferingTracks: string[] = [];

  for (const track of tracks) {
    // readyState >= 3 means HAVE_FUTURE_DATA (enough data to play)
    // readyState === 4 means HAVE_ENOUGH_DATA (can play through)
    const isReady = track.element.readyState >= 3;
    const isBuffering = track.element.readyState < 3 && !track.element.paused;

    if (isReady) {
      readyTracks.push(track.name);
    }
    if (isBuffering) {
      bufferingTracks.push(track.name);
    }
  }

  const requiredTracks = tracks.filter((t) => t.required);
  const allRequiredReady = requiredTracks.every(
    (t) => t.element.readyState >= 3
  );

  return {
    allReady: allRequiredReady,
    anyBuffering: bufferingTracks.length > 0,
    readyTracks,
    bufferingTracks,
  };
}

/**
 * 同步所有轨道到指定时间
 */
export function syncTracksToTime(tracks: MediaTrack[], time: number): void {
  for (const track of tracks) {
    if (Math.abs(track.element.currentTime - time) > 0.1) {
      track.element.currentTime = time;
    }
  }
}

/**
 * 同步播放所有轨道
 */
export async function playAllTracks(tracks: MediaTrack[]): Promise<void> {
  const playPromises = tracks.map((track) => {
    if (track.element.paused) {
      return track.element.play().catch(() => {
        // Ignore play errors for non-required tracks
        if (track.required) {
          throw new Error(`Failed to play ${track.name}`);
        }
      });
    }
    return Promise.resolve();
  });

  await Promise.all(playPromises);
}

/**
 * 暂停所有轨道
 */
export function pauseAllTracks(tracks: MediaTrack[]): void {
  for (const track of tracks) {
    if (!track.element.paused) {
      track.element.pause();
    }
  }
}

/**
 * 检查轨道是否正在缓冲
 * 当任一媒体源正在缓冲时返回 true
 */
export function isAnyTrackBuffering(tracks: MediaTrack[]): boolean {
  return tracks.some((track) => {
    // Check if the track is waiting for data
    return (
      track.required &&
      !track.element.paused &&
      track.element.readyState < 3
    );
  });
}

/**
 * 获取所有轨道的最大时间差
 * 用于检测同步偏移
 */
export function getMaxTimeDrift(tracks: MediaTrack[]): number {
  if (tracks.length < 2) return 0;

  const times = tracks.map((t) => t.element.currentTime);
  const maxTime = Math.max(...times);
  const minTime = Math.min(...times);

  return maxTime - minTime;
}

/**
 * 如果时间偏移超过阈值，重新同步轨道
 */
export function resyncIfNeeded(
  tracks: MediaTrack[],
  referenceTime: number,
  threshold: number = 0.1
): boolean {
  const drift = getMaxTimeDrift(tracks);

  if (drift > threshold) {
    syncTracksToTime(tracks, referenceTime);
    return true;
  }

  return false;
}
