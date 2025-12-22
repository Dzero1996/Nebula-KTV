/**
 * SongList 组件属性测试
 * **Feature: nebula-ktv, Property 5: 处理中歌曲不可播放**
 * **Validates: Requirements 3.5**
 */

import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import * as fc from "fast-check";
import { SongList } from "./SongList";
import { SongStatus, type Song } from "@/lib/api";

// 每次测试后清理 DOM
afterEach(() => {
  cleanup();
});

// 生成随机歌曲数据的 Arbitrary
const songArbitrary = (status: SongStatus): fc.Arbitrary<Song> =>
  fc.record({
    id: fc.uuid(),
    title: fc.string({ minLength: 1, maxLength: 50 }),
    artist: fc.string({ minLength: 1, maxLength: 30 }),
    subtitle: fc.option(fc.string(), { nil: null }),
    album: fc.option(fc.string(), { nil: null }),
    year: fc.option(fc.integer({ min: 1900, max: 2030 }), { nil: null }),
    cover_path: fc.option(fc.webUrl(), { nil: null }),
    lyricist: fc.option(fc.string(), { nil: null }),
    composer: fc.option(fc.string(), { nil: null }),
    arranger: fc.option(fc.string(), { nil: null }),
    publisher: fc.option(fc.string(), { nil: null }),
    language_family: fc.option(fc.string(), { nil: null }),
    language_dialect: fc.option(fc.string(), { nil: null }),
    singing_type: fc.option(fc.string(), { nil: null }),
    gender_type: fc.option(fc.string(), { nil: null }),
    genre: fc.option(fc.string(), { nil: null }),
    scenario: fc.option(fc.array(fc.string()), { nil: null }),
    aliases: fc.option(fc.array(fc.string()), { nil: null }),
    title_pinyin: fc.option(fc.string(), { nil: null }),
    title_abbr: fc.option(fc.string(), { nil: null }),
    artist_pinyin: fc.option(fc.string(), { nil: null }),
    artist_abbr: fc.option(fc.string(), { nil: null }),
    duration: fc.option(fc.integer({ min: 0, max: 600 }), { nil: null }),
    bpm: fc.option(fc.integer({ min: 60, max: 200 }), { nil: null }),
    original_key: fc.option(fc.string(), { nil: null }),
    camelot_key: fc.option(fc.string(), { nil: null }),
    energy: fc.option(fc.float({ min: 0, max: 1 }), { nil: null }),
    danceability: fc.option(fc.float({ min: 0, max: 1 }), { nil: null }),
    valence: fc.option(fc.float({ min: 0, max: 1 }), { nil: null }),
    vocal_range_low: fc.option(fc.string(), { nil: null }),
    vocal_range_high: fc.option(fc.string(), { nil: null }),
    difficulty_level: fc.option(fc.integer({ min: 1, max: 10 }), { nil: null }),
    feature_vector: fc.option(fc.array(fc.float()), { nil: null }),
    status: fc.constant(status),
    play_count: fc.integer({ min: 0, max: 10000 }),
    last_played_at: fc.constant(null),
    is_favorite: fc.boolean(),
    quality_badge: fc.option(fc.constantFrom("4K", "HD", "SD"), { nil: null }),
    meta_json: fc.constant({}),
    created_at: fc.constant("2024-01-01T00:00:00.000Z"),
    updated_at: fc.constant("2024-01-01T00:00:00.000Z"),
  });

// 不可播放状态
const nonPlayableStatuses = [SongStatus.PENDING, SongStatus.PROCESSING];

// 可播放状态
const playableStatuses = [SongStatus.READY, SongStatus.PARTIAL];

describe("SongList - Property 5: 处理中歌曲不可播放", () => {
  /**
   * **Feature: nebula-ktv, Property 5: 处理中歌曲不可播放**
   * *For any* 状态为 PROCESSING 或 PENDING 的歌曲，播放按钮应该被禁用
   */
  it("should disable play button for songs with PROCESSING or PENDING status", () => {
    fc.assert(
      fc.property(
        fc.constantFrom(...nonPlayableStatuses).chain((status) =>
          songArbitrary(status)
        ),
        (song) => {
          // 清理之前的渲染
          cleanup();
          
          const onPlay = vi.fn();
          render(<SongList songs={[song]} onPlay={onPlay} />);

          // 查找播放按钮 - 使用 getAllByRole 然后取第一个
          const playButtons = screen.getAllByRole("button");
          const playButton = playButtons.find(btn => 
            btn.getAttribute("aria-label")?.includes("播放") ||
            btn.getAttribute("aria-label")?.includes("处理") ||
            btn.getAttribute("aria-label")?.includes("等待")
          );

          // 验证按钮存在且被禁用
          expect(playButton).toBeDefined();
          expect(playButton).toBeDisabled();

          // 尝试点击按钮
          if (playButton) {
            fireEvent.click(playButton);
          }

          // 验证 onPlay 回调未被调用
          expect(onPlay).not.toHaveBeenCalled();
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * 对比测试：可播放状态的歌曲应该可以点击播放
   */
  it("should enable play button for songs with READY or PARTIAL status", () => {
    fc.assert(
      fc.property(
        fc.constantFrom(...playableStatuses).chain((status) =>
          songArbitrary(status)
        ),
        (song) => {
          // 清理之前的渲染
          cleanup();
          
          const onPlay = vi.fn();
          render(<SongList songs={[song]} onPlay={onPlay} />);

          // 查找播放按钮
          const playButtons = screen.getAllByRole("button");
          const playButton = playButtons.find(btn => 
            btn.getAttribute("aria-label") === "播放"
          );

          // 验证按钮存在且未被禁用
          expect(playButton).toBeDefined();
          expect(playButton).not.toBeDisabled();

          // 点击按钮
          if (playButton) {
            fireEvent.click(playButton);
          }

          // 验证 onPlay 回调被调用
          expect(onPlay).toHaveBeenCalledWith(song);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * 验证 FAILED 状态的歌曲也不可播放
   */
  it("should disable play button for songs with FAILED status", () => {
    fc.assert(
      fc.property(songArbitrary(SongStatus.FAILED), (song) => {
        // 清理之前的渲染
        cleanup();
        
        const onPlay = vi.fn();
        render(<SongList songs={[song]} onPlay={onPlay} />);

        // 查找播放按钮
        const playButtons = screen.getAllByRole("button");
        const playButton = playButtons.find(btn => 
          btn.getAttribute("aria-label")?.includes("处理失败")
        );

        // 验证按钮存在且被禁用
        expect(playButton).toBeDefined();
        expect(playButton).toBeDisabled();

        // 尝试点击按钮
        if (playButton) {
          fireEvent.click(playButton);
        }

        // 验证 onPlay 回调未被调用
        expect(onPlay).not.toHaveBeenCalled();
      }),
      { numRuns: 100 }
    );
  });
});
