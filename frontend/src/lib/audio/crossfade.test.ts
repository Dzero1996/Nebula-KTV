/**
 * **Feature: nebula-ktv, Property 7: Crossfade 增益值约束**
 * **Validates: Requirements 6.4**
 *
 * *For any* Crossfade 操作，在任意时刻两个音轨的增益值之和应接近 1.0（允许 ±0.1 误差）。
 */

import { describe, it, expect } from "vitest";
import * as fc from "fast-check";
import {
  calculateGainAtProgress,
  validateGainSum,
  calculateCrossfadeGains,
} from "./crossfade";

describe("Property 7: Crossfade 增益值约束", () => {
  /**
   * Property test: Gain sum should always be close to 1.0 during crossfade
   * For any progress value between 0 and 1, the sum of both gains should be ~1.0
   */
  it("should maintain gain sum close to 1.0 at any progress point", () => {
    fc.assert(
      fc.property(
        // Generate progress values between 0 and 1
        fc.float({ min: 0, max: 1, noNaN: true }),
        // Generate direction (true = original to instrumental, false = reverse)
        fc.boolean(),
        (progress, fromOriginal) => {
          const [originalGain, instrumentalGain] = calculateCrossfadeGains(
            progress,
            fromOriginal
          );

          // The sum should be exactly 1.0 for linear crossfade
          const sum = originalGain + instrumentalGain;

          // Verify sum is within tolerance (±0.1)
          expect(validateGainSum(originalGain, instrumentalGain)).toBe(true);

          // For linear crossfade, sum should be exactly 1.0
          expect(Math.abs(sum - 1.0)).toBeLessThan(0.001);

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property test: Gain values should be bounded between 0 and 1
   */
  it("should keep gain values between 0 and 1", () => {
    fc.assert(
      fc.property(
        fc.float({ min: 0, max: 1, noNaN: true }),
        fc.boolean(),
        (progress, fromOriginal) => {
          const [originalGain, instrumentalGain] = calculateCrossfadeGains(
            progress,
            fromOriginal
          );

          // Both gains should be in [0, 1]
          expect(originalGain).toBeGreaterThanOrEqual(0);
          expect(originalGain).toBeLessThanOrEqual(1);
          expect(instrumentalGain).toBeGreaterThanOrEqual(0);
          expect(instrumentalGain).toBeLessThanOrEqual(1);

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property test: Crossfade should be monotonic
   * As progress increases, one gain should decrease and the other should increase
   */
  it("should have monotonic gain changes during crossfade", () => {
    fc.assert(
      fc.property(
        // Generate two progress values where p1 < p2
        fc.float({ min: 0, max: 0.5, noNaN: true }),
        fc.float({ min: 0, max: 0.5, noNaN: true }),
        fc.boolean(),
        (p1, delta, fromOriginal) => {
          const p2 = p1 + delta; // Ensure p2 > p1

          const [originalGain1, instrumentalGain1] = calculateCrossfadeGains(
            p1,
            fromOriginal
          );
          const [originalGain2, instrumentalGain2] = calculateCrossfadeGains(
            p2,
            fromOriginal
          );

          if (fromOriginal) {
            // When switching from original to instrumental:
            // - Original gain should decrease (or stay same)
            // - Instrumental gain should increase (or stay same)
            expect(originalGain2).toBeLessThanOrEqual(originalGain1 + 0.001);
            expect(instrumentalGain2).toBeGreaterThanOrEqual(instrumentalGain1 - 0.001);
          } else {
            // When switching from instrumental to original:
            // - Original gain should increase (or stay same)
            // - Instrumental gain should decrease (or stay same)
            expect(originalGain2).toBeGreaterThanOrEqual(originalGain1 - 0.001);
            expect(instrumentalGain2).toBeLessThanOrEqual(instrumentalGain1 + 0.001);
          }

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property test: Boundary conditions
   * At progress 0 and 1, gains should be at their extremes
   */
  it("should have correct boundary values", () => {
    fc.assert(
      fc.property(fc.boolean(), (fromOriginal) => {
        // At progress 0
        const [og0, ig0] = calculateCrossfadeGains(0, fromOriginal);
        // At progress 1
        const [og1, ig1] = calculateCrossfadeGains(1, fromOriginal);

        if (fromOriginal) {
          // Start: original=1, instrumental=0
          // End: original=0, instrumental=1
          expect(og0).toBeCloseTo(1, 5);
          expect(ig0).toBeCloseTo(0, 5);
          expect(og1).toBeCloseTo(0, 5);
          expect(ig1).toBeCloseTo(1, 5);
        } else {
          // Start: original=0, instrumental=1
          // End: original=1, instrumental=0
          expect(og0).toBeCloseTo(0, 5);
          expect(ig0).toBeCloseTo(1, 5);
          expect(og1).toBeCloseTo(1, 5);
          expect(ig1).toBeCloseTo(0, 5);
        }

        return true;
      }),
      { numRuns: 100 }
    );
  });

  /**
   * Property test: Progress clamping
   * Values outside [0, 1] should be clamped
   */
  it("should clamp progress values outside [0, 1]", () => {
    fc.assert(
      fc.property(
        fc.float({ min: -10, max: 10, noNaN: true }),
        fc.boolean(),
        (progress, fromOriginal) => {
          const [originalGain, instrumentalGain] = calculateCrossfadeGains(
            progress,
            fromOriginal
          );

          // Gains should always be valid regardless of input
          expect(originalGain).toBeGreaterThanOrEqual(0);
          expect(originalGain).toBeLessThanOrEqual(1);
          expect(instrumentalGain).toBeGreaterThanOrEqual(0);
          expect(instrumentalGain).toBeLessThanOrEqual(1);

          // Sum should still be ~1.0
          expect(validateGainSum(originalGain, instrumentalGain)).toBe(true);

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
});

describe("Crossfade utility unit tests", () => {
  it("should calculate linear interpolation correctly", () => {
    expect(calculateGainAtProgress(0, 1, 0)).toBe(0);
    expect(calculateGainAtProgress(0, 1, 0.5)).toBe(0.5);
    expect(calculateGainAtProgress(0, 1, 1)).toBe(1);
    expect(calculateGainAtProgress(1, 0, 0.5)).toBe(0.5);
  });

  it("should validate gain sum correctly", () => {
    expect(validateGainSum(0.5, 0.5)).toBe(true);
    expect(validateGainSum(1, 0)).toBe(true);
    expect(validateGainSum(0, 1)).toBe(true);
    expect(validateGainSum(0.9, 0.1)).toBe(true);
    expect(validateGainSum(0.95, 0.05)).toBe(true);

    // Edge cases within tolerance
    expect(validateGainSum(0.45, 0.45)).toBe(true); // sum = 0.9
    expect(validateGainSum(0.55, 0.55)).toBe(true); // sum = 1.1

    // Outside tolerance
    expect(validateGainSum(0.4, 0.4)).toBe(false); // sum = 0.8
    expect(validateGainSum(0.6, 0.6)).toBe(false); // sum = 1.2
  });

  it("should calculate crossfade gains for original to instrumental", () => {
    const [og, ig] = calculateCrossfadeGains(0.5, true);
    expect(og).toBeCloseTo(0.5, 5);
    expect(ig).toBeCloseTo(0.5, 5);
  });

  it("should calculate crossfade gains for instrumental to original", () => {
    const [og, ig] = calculateCrossfadeGains(0.5, false);
    expect(og).toBeCloseTo(0.5, 5);
    expect(ig).toBeCloseTo(0.5, 5);
  });
});
