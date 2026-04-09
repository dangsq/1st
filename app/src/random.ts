import { clampParams, defaultParams, mergeParams } from './params'
import type { AppleParams } from './types'

const rand = (min: number, max: number) => min + Math.random() * (max - min)

export const createRandomAppleParams = (): AppleParams => {
  const biteEnabled = Math.random() > 0.3
  const leafEnabled = Math.random() > 0.2

  return clampParams(
    mergeParams({
      ...defaultParams,
      height: rand(0.85, 1.15),
      width: rand(0.85, 1.15),
      maxWidthHeight: rand(0.44, 0.65),
      bottomRadius: rand(0.12, 0.32),
      bottomDepth: rand(0.02, 0.2),
      topRadius: rand(0.12, 0.32),
      topDepth: rand(0.02, 0.2),
      cubicRatio: rand(0.15, 0.55),

      shellThickness: rand(0.03, 0.1),

      leafEnabled,
      leafLength: rand(0.08, 0.3),
      leafWidth: rand(0.03, 0.12),
      leafAngle: rand(Math.PI / 4, Math.PI / 2),

      biteEnabled,
      biteU: rand(0.1, 0.9),
      biteV: rand(0.3, 0.7),
      biteRadius: biteEnabled ? rand(0.08, 0.25) : 0.15,

      segments: 64,
      rotationY: rand(0.3, 1.5),
    }),
  )
}
