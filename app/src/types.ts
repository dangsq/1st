export type AppleParams = {
  // Core form — Bezier lathe profile
  height: number
  width: number
  maxWidthHeight: number
  bottomRadius: number
  bottomDepth: number
  topRadius: number
  topDepth: number
  cubicRatio: number

  // Shell
  shellThickness: number

  // Leaf
  leafEnabled: boolean
  leafLength: number
  leafWidth: number
  leafAngle: number // angle with ground plane, π/4 – π/2

  // Bite (CSG boolean subtraction)
  biteEnabled: boolean
  biteU: number // longitude 0–1 around circumference
  biteV: number // latitude 0=bottom, 1=top
  biteRadius: number // UV-space radius

  // Presentation
  segments: number
  rotationY: number
}

export type StoryPage = {
  id: string
  label: string
  title: string
  text: string
  params?: Partial<AppleParams>
  random?: boolean
  freeEdit?: boolean

  // Visual illustration (CSS gradient + shape or image URL)
  imageGradient?: string
  imageUrl?: string
  imageShape?: string

  // Camera override for this page
  cameraPosition?: [number, number, number]
  cameraTarget?: [number, number, number]
}
