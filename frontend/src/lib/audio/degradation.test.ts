/**
 * 降级策略单元测试
 * **Validates: Requirements 6.5**
 */

import { describe, it, expect } from "vitest";
import {
  calculateDegradationState,
  canSwitchToMode,
  getDefaultVocalMode,
  getDegradationMessage,
} from "./degradation";

describe("Degradation Strategy", () => {
  describe("calculateDegradationState", () => {
    it("should return full mode when all tracks are available", () => {
      const state = calculateDegradationState({
        video: true,
        original: true,
        instrumental: true,
      });

      expect(state.mode).toBe("full");
      expect(state.canSwitchVocal).toBe(true);
      expect(state.errorMessage).toBeUndefined();
    });

    it("should return original-only mode when instrumental fails", () => {
      const state = calculateDegradationState({
        video: true,
        original: true,
        instrumental: false,
      });

      expect(state.mode).toBe("original-only");
      expect(state.canSwitchVocal).toBe(false);
      expect(state.instrumentalAvailable).toBe(false);
      expect(state.errorMessage).toContain("伴奏加载失败");
    });

    it("should return instrumental-only mode when original fails", () => {
      const state = calculateDegradationState({
        video: true,
        original: false,
        instrumental: true,
      });

      expect(state.mode).toBe("instrumental-only");
      expect(state.canSwitchVocal).toBe(false);
      expect(state.originalAvailable).toBe(false);
      expect(state.errorMessage).toContain("原唱加载失败");
    });

    it("should return error mode when video fails", () => {
      const state = calculateDegradationState({
        video: false,
        original: true,
        instrumental: true,
      });

      expect(state.mode).toBe("error");
      expect(state.canSwitchVocal).toBe(false);
      expect(state.errorMessage).toContain("视频加载失败");
    });

    it("should return error mode when both audio tracks fail", () => {
      const state = calculateDegradationState({
        video: true,
        original: false,
        instrumental: false,
      });

      expect(state.mode).toBe("error");
      expect(state.canSwitchVocal).toBe(false);
      expect(state.errorMessage).toContain("音频加载失败");
    });
  });

  describe("canSwitchToMode", () => {
    it("should allow switching in full mode", () => {
      const state = calculateDegradationState({
        video: true,
        original: true,
        instrumental: true,
      });

      expect(canSwitchToMode("original", state)).toBe(true);
      expect(canSwitchToMode("instrumental", state)).toBe(true);
    });

    it("should not allow switching in original-only mode", () => {
      const state = calculateDegradationState({
        video: true,
        original: true,
        instrumental: false,
      });

      expect(canSwitchToMode("original", state)).toBe(false);
      expect(canSwitchToMode("instrumental", state)).toBe(false);
    });

    it("should not allow switching in instrumental-only mode", () => {
      const state = calculateDegradationState({
        video: true,
        original: false,
        instrumental: true,
      });

      expect(canSwitchToMode("original", state)).toBe(false);
      expect(canSwitchToMode("instrumental", state)).toBe(false);
    });
  });

  describe("getDefaultVocalMode", () => {
    it("should return original as default when available", () => {
      const state = calculateDegradationState({
        video: true,
        original: true,
        instrumental: true,
      });

      expect(getDefaultVocalMode(state)).toBe("original");
    });

    it("should return original in original-only mode", () => {
      const state = calculateDegradationState({
        video: true,
        original: true,
        instrumental: false,
      });

      expect(getDefaultVocalMode(state)).toBe("original");
    });

    it("should return instrumental in instrumental-only mode", () => {
      const state = calculateDegradationState({
        video: true,
        original: false,
        instrumental: true,
      });

      expect(getDefaultVocalMode(state)).toBe("instrumental");
    });

    it("should return null in error mode", () => {
      const state = calculateDegradationState({
        video: false,
        original: true,
        instrumental: true,
      });

      expect(getDefaultVocalMode(state)).toBeNull();
    });
  });

  describe("getDegradationMessage", () => {
    it("should return null for full mode", () => {
      const state = calculateDegradationState({
        video: true,
        original: true,
        instrumental: true,
      });

      expect(getDegradationMessage(state)).toBeNull();
    });

    it("should return message for degraded modes", () => {
      const originalOnly = calculateDegradationState({
        video: true,
        original: true,
        instrumental: false,
      });

      expect(getDegradationMessage(originalOnly)).toContain("伴奏加载失败");

      const instrumentalOnly = calculateDegradationState({
        video: true,
        original: false,
        instrumental: true,
      });

      expect(getDegradationMessage(instrumentalOnly)).toContain("原唱加载失败");
    });
  });
});
