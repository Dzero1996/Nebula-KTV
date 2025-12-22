/**
 * **Feature: nebula-ktv, Property 6: 三轨同步播放约束**
 * **Validates: Requirements 6.2, 6.3**
 *
 * *For any* 播放状态，当任一媒体源处于缓冲状态时，所有轨道必须暂停。
 */

import { describe, it, expect, vi } from "vitest";
import * as fc from "fast-check";
import {
  checkTracksReady,
  isAnyTrackBuffering,
  pauseAllTracks,
  syncTracksToTime,
  getMaxTimeDrift,
  resyncIfNeeded,
  type MediaTrack,
} from "./sync";

// Mock HTMLMediaElement
function createMockMediaElement(options: {
  readyState: number;
  paused: boolean;
  currentTime: number;
}): HTMLMediaElement {
  let _paused = options.paused;
  const element = {
    readyState: options.readyState,
    get paused() {
      return _paused;
    },
    currentTime: options.currentTime,
    pause: vi.fn(() => {
      _paused = true;
    }),
    play: vi.fn(() => Promise.resolve()),
  } as unknown as HTMLMediaElement;
  return element;
}

describe("Property 6: 三轨同步播放约束", () => {
  /**
   * Property test: When any track is buffering, all tracks should be paused
   */
  it("should pause all tracks when any required track is buffering", () => {
    fc.assert(
      fc.property(
        // Generate random ready states for 3 tracks (0-4)
        fc.integer({ min: 0, max: 4 }),
        fc.integer({ min: 0, max: 4 }),
        fc.integer({ min: 0, max: 4 }),
        // Generate random paused states
        fc.boolean(),
        fc.boolean(),
        fc.boolean(),
        (
          videoReadyState,
          originalReadyState,
          instrumentalReadyState,
          videoPaused,
          originalPaused,
          instrumentalPaused
        ) => {
          const tracks: MediaTrack[] = [
            {
              element: createMockMediaElement({
                readyState: videoReadyState,
                paused: videoPaused,
                currentTime: 0,
              }),
              name: "video",
              required: true,
            },
            {
              element: createMockMediaElement({
                readyState: originalReadyState,
                paused: originalPaused,
                currentTime: 0,
              }),
              name: "original",
              required: true,
            },
            {
              element: createMockMediaElement({
                readyState: instrumentalReadyState,
                paused: instrumentalPaused,
                currentTime: 0,
              }),
              name: "instrumental",
              required: false, // Instrumental is optional
            },
          ];

          const anyBuffering = isAnyTrackBuffering(tracks);

          // If any required track is buffering (readyState < 3 and not paused),
          // we should pause all tracks
          if (anyBuffering) {
            pauseAllTracks(tracks);

            // After pauseAllTracks, all tracks should be in paused state
            // The function only calls pause() on tracks that weren't already paused
            for (const track of tracks) {
              // The track should now be paused (either was already paused or pause() was called)
              expect(track.element.paused).toBe(true);
            }
          }

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property test: checkTracksReady correctly identifies ready state
   */
  it("should correctly identify when all required tracks are ready", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 4 }),
        fc.integer({ min: 0, max: 4 }),
        fc.integer({ min: 0, max: 4 }),
        (videoReadyState, originalReadyState, instrumentalReadyState) => {
          const tracks: MediaTrack[] = [
            {
              element: createMockMediaElement({
                readyState: videoReadyState,
                paused: true,
                currentTime: 0,
              }),
              name: "video",
              required: true,
            },
            {
              element: createMockMediaElement({
                readyState: originalReadyState,
                paused: true,
                currentTime: 0,
              }),
              name: "original",
              required: true,
            },
            {
              element: createMockMediaElement({
                readyState: instrumentalReadyState,
                paused: true,
                currentTime: 0,
              }),
              name: "instrumental",
              required: false,
            },
          ];

          const state = checkTracksReady(tracks);

          // All required tracks are ready when readyState >= 3
          const expectedAllReady =
            videoReadyState >= 3 && originalReadyState >= 3;

          expect(state.allReady).toBe(expectedAllReady);

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property test: syncTracksToTime synchronizes all tracks
   */
  it("should synchronize all tracks to the same time", () => {
    fc.assert(
      fc.property(
        fc.float({ min: 0, max: 300, noNaN: true }),
        fc.float({ min: 0, max: 300, noNaN: true }),
        fc.float({ min: 0, max: 300, noNaN: true }),
        fc.float({ min: 0, max: 300, noNaN: true }),
        (time1, time2, time3, targetTime) => {
          const tracks: MediaTrack[] = [
            {
              element: createMockMediaElement({
                readyState: 4,
                paused: false,
                currentTime: time1,
              }),
              name: "video",
              required: true,
            },
            {
              element: createMockMediaElement({
                readyState: 4,
                paused: false,
                currentTime: time2,
              }),
              name: "original",
              required: true,
            },
            {
              element: createMockMediaElement({
                readyState: 4,
                paused: false,
                currentTime: time3,
              }),
              name: "instrumental",
              required: false,
            },
          ];

          syncTracksToTime(tracks, targetTime);

          // All tracks should be synced to target time (within threshold)
          for (const track of tracks) {
            const drift = Math.abs(track.element.currentTime - targetTime);
            // Either synced or was already close enough (within 0.1s)
            expect(drift <= 0.1 || track.element.currentTime === targetTime).toBe(true);
          }

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property test: getMaxTimeDrift calculates correct drift
   */
  it("should calculate correct maximum time drift between tracks", () => {
    fc.assert(
      fc.property(
        fc.float({ min: 0, max: 300, noNaN: true }),
        fc.float({ min: 0, max: 300, noNaN: true }),
        fc.float({ min: 0, max: 300, noNaN: true }),
        (time1, time2, time3) => {
          const tracks: MediaTrack[] = [
            {
              element: createMockMediaElement({
                readyState: 4,
                paused: false,
                currentTime: time1,
              }),
              name: "video",
              required: true,
            },
            {
              element: createMockMediaElement({
                readyState: 4,
                paused: false,
                currentTime: time2,
              }),
              name: "original",
              required: true,
            },
            {
              element: createMockMediaElement({
                readyState: 4,
                paused: false,
                currentTime: time3,
              }),
              name: "instrumental",
              required: false,
            },
          ];

          const drift = getMaxTimeDrift(tracks);
          const times = [time1, time2, time3];
          const expectedDrift = Math.max(...times) - Math.min(...times);

          expect(Math.abs(drift - expectedDrift)).toBeLessThan(0.001);

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
});

describe("Sync utility unit tests", () => {
  it("should detect buffering when required track has low readyState", () => {
    const tracks: MediaTrack[] = [
      {
        element: createMockMediaElement({
          readyState: 2, // HAVE_CURRENT_DATA - not enough
          paused: false,
          currentTime: 0,
        }),
        name: "video",
        required: true,
      },
      {
        element: createMockMediaElement({
          readyState: 4,
          paused: false,
          currentTime: 0,
        }),
        name: "original",
        required: true,
      },
    ];

    expect(isAnyTrackBuffering(tracks)).toBe(true);
  });

  it("should not detect buffering when all required tracks are ready", () => {
    const tracks: MediaTrack[] = [
      {
        element: createMockMediaElement({
          readyState: 4,
          paused: false,
          currentTime: 0,
        }),
        name: "video",
        required: true,
      },
      {
        element: createMockMediaElement({
          readyState: 4,
          paused: false,
          currentTime: 0,
        }),
        name: "original",
        required: true,
      },
    ];

    expect(isAnyTrackBuffering(tracks)).toBe(false);
  });

  it("should resync tracks when drift exceeds threshold", () => {
    const tracks: MediaTrack[] = [
      {
        element: createMockMediaElement({
          readyState: 4,
          paused: false,
          currentTime: 10,
        }),
        name: "video",
        required: true,
      },
      {
        element: createMockMediaElement({
          readyState: 4,
          paused: false,
          currentTime: 10.5, // 0.5s drift
        }),
        name: "original",
        required: true,
      },
    ];

    const resynced = resyncIfNeeded(tracks, 10, 0.1);
    expect(resynced).toBe(true);
  });
});
