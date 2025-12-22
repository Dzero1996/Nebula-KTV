/**
 * Crossfade 音频切换工具
 * 实现 500ms 交叉渐变切换
 */

export interface CrossfadeOptions {
  duration: number; // 默认 500ms
  fromGain: GainNode;
  toGain: GainNode;
  audioContext: AudioContext;
}

/**
 * 执行交叉渐变切换
 * 使用 linearRampToValueAtTime 确保增益值平滑过渡
 * 
 * @param options - Crossfade 配置选项
 * @returns Promise 在渐变完成后 resolve
 */
export function crossfade(options: CrossfadeOptions): Promise<void> {
  const { duration, fromGain, toGain, audioContext } = options;

  const currentTime = audioContext.currentTime;
  const fadeDuration = duration / 1000; // Convert ms to seconds

  // Cancel any scheduled changes
  fromGain.gain.cancelScheduledValues(currentTime);
  toGain.gain.cancelScheduledValues(currentTime);

  // Set current values explicitly to avoid jumps
  fromGain.gain.setValueAtTime(fromGain.gain.value, currentTime);
  toGain.gain.setValueAtTime(toGain.gain.value, currentTime);

  // Ramp to target values
  fromGain.gain.linearRampToValueAtTime(0, currentTime + fadeDuration);
  toGain.gain.linearRampToValueAtTime(1, currentTime + fadeDuration);

  // Return a promise that resolves when the fade is complete
  return new Promise((resolve) => {
    setTimeout(resolve, duration);
  });
}

/**
 * 计算给定时间点的增益值
 * 用于属性测试验证
 * 
 * @param startValue - 起始增益值
 * @param endValue - 目标增益值
 * @param progress - 进度 (0-1)
 * @returns 当前增益值
 */
export function calculateGainAtProgress(
  startValue: number,
  endValue: number,
  progress: number
): number {
  // Linear interpolation
  return startValue + (endValue - startValue) * progress;
}

/**
 * 验证两个增益值之和是否接近 1.0
 * 允许 ±0.1 误差
 * 
 * @param gain1 - 第一个增益值
 * @param gain2 - 第二个增益值
 * @returns 是否满足约束
 */
export function validateGainSum(gain1: number, gain2: number): boolean {
  const sum = gain1 + gain2;
  return sum >= 0.9 && sum <= 1.1;
}

/**
 * 计算 crossfade 过程中任意时刻的两个增益值
 * 确保增益值之和始终接近 1.0
 * 
 * @param progress - 进度 (0-1)
 * @param fromOriginal - 是否从原唱切换到伴奏
 * @returns [originalGain, instrumentalGain]
 */
export function calculateCrossfadeGains(
  progress: number,
  fromOriginal: boolean
): [number, number] {
  // Clamp progress to [0, 1]
  const clampedProgress = Math.max(0, Math.min(1, progress));

  if (fromOriginal) {
    // Switching from original to instrumental
    const originalGain = 1 - clampedProgress;
    const instrumentalGain = clampedProgress;
    return [originalGain, instrumentalGain];
  } else {
    // Switching from instrumental to original
    const originalGain = clampedProgress;
    const instrumentalGain = 1 - clampedProgress;
    return [originalGain, instrumentalGain];
  }
}
