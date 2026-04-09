import type { AppleParams } from './types'

export const defaultParams: AppleParams = {
  height: 1.0,
  width: 1.0,
  maxWidthHeight: 0.55,
  bottomRadius: 0.2,
  bottomDepth: 0.1,
  topRadius: 0.2,
  topDepth: 0.1,
  cubicRatio: 0.3,

  shellThickness: 0.05,

  leafEnabled: false,
  leafLength: 0.15,
  leafWidth: 0.06,
  leafAngle: Math.PI / 3, // 60°

  biteEnabled: false,
  biteU: 0.25,
  biteV: 0.5,
  biteRadius: 0.15,

  segments: 64,
  rotationY: 0,
}

export const paramRanges: Record<keyof AppleParams, [number, number] | null> = {
  height: [0.8, 1.2],
  width: [0.8, 1.2],
  maxWidthHeight: [0.42, 0.7],
  bottomRadius: [0.1, 0.35],
  bottomDepth: [0.0, 0.3],
  topRadius: [0.1, 0.35],
  topDepth: [0.0, 0.3],
  cubicRatio: [0.1, 0.8],

  shellThickness: [0.02, 0.15],

  leafEnabled: null,
  leafLength: [0.05, 0.5],
  leafWidth: [0.02, 0.2],
  leafAngle: [Math.PI / 4, Math.PI / 2],

  biteEnabled: null,
  biteU: [0.0, 1.0],
  biteV: [0.0, 1.0],
  biteRadius: [0.05, 0.4],

  segments: [32, 128],
  rotationY: [-Math.PI, Math.PI],
}

export const mergeParams = (overrides: Partial<AppleParams> = {}): AppleParams => ({
  ...defaultParams,
  ...overrides,
})

export const clampParams = (params: AppleParams): AppleParams => {
  const next = { ...params }

  ;(Object.keys(paramRanges) as Array<keyof AppleParams>).forEach((key) => {
    const range = paramRanges[key]
    if (!range) return
    const [min, max] = range
    next[key] = Math.min(max, Math.max(min, Number(next[key]))) as never
  })

  return next
}
