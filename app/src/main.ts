import GUI from 'lil-gui'
import './style.css'
import { AppleRenderer } from './appleRenderer'
import { clampParams, mergeParams, paramRanges } from './params'
import { createRandomAppleParams } from './random'
import { storyPages } from './story'
import type { AppleParams } from './types'

/* ═══════════════════════════════════════════════════
   DOM scaffold
   ═══════════════════════════════════════════════════ */
const app = document.querySelector<HTMLDivElement>('#app')
if (!app) throw new Error('App root not found')

const dotButtons = storyPages.map(
  (_, i) => `<button class="dot${i === 0 ? ' active' : ''}" data-index="${i}" aria-label="Page ${i}"></button>`,
)

app.innerHTML = `
  <div class="shell">
    <!-- Left: narrative -->
    <section class="narrative-panel">
      <header class="narrative-header">
        <span class="project-label">Apple Grammar</span>
        <span class="page-counter" id="page-counter">01 / ${String(storyPages.length).padStart(2, '0')}</span>
      </header>

      <div class="story-content">
        <div class="story-image" id="story-image">
          <div class="image-inner" id="image-inner"></div>
        </div>
        <span class="chapter-label" id="chapter-label"></span>
        <h1 class="page-title" id="page-title"></h1>
        <p class="page-text" id="page-text"></p>
        <span class="mode-badge" id="mode-badge"></span>
      </div>

      <footer class="narrative-footer">
        <div class="dot-nav" id="dot-nav">
          ${dotButtons.join('')}
        </div>
        <div class="page-nav">
          <button class="nav-btn" id="prev-btn" aria-label="Previous page">
            <svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
          </button>
          <button class="nav-btn" id="next-btn" aria-label="Next page">
            <svg viewBox="0 0 24 24"><polyline points="9 6 15 12 9 18"/></svg>
          </button>
        </div>
      </footer>
    </section>

    <!-- Right: 3D -->
    <section class="canvas-panel">
      <div class="canvas-wrap" id="canvas-wrap"></div>
      <div class="gui-host" id="gui-host"></div>
      <div class="keyboard-hint" id="keyboard-hint">Press &larr; &rarr; to navigate</div>
    </section>
  </div>
  
  <!-- Copyright Footer -->
  <footer class="copyright-footer">
    <p>© ${new Date().getFullYear()} Shengqi Dang. All rights reserved.</p>
  </footer>
`

/* ═══════════════════════════════════════════════════
   Element references
   ═══════════════════════════════════════════════════ */
const el = {
  counter: document.getElementById('page-counter')!,
  chapterLabel: document.getElementById('chapter-label')!,
  title: document.getElementById('page-title')!,
  text: document.getElementById('page-text')!,
  modeBadge: document.getElementById('mode-badge')!,
  storyImage: document.getElementById('story-image')!,
  imageInner: document.getElementById('image-inner')!,
  prevBtn: document.getElementById('prev-btn') as HTMLButtonElement,
  nextBtn: document.getElementById('next-btn') as HTMLButtonElement,
  dotNav: document.getElementById('dot-nav')!,
  canvasWrap: document.getElementById('canvas-wrap')!,
  guiHost: document.getElementById('gui-host')!,
  keyboardHint: document.getElementById('keyboard-hint')!,
}

const dots = Array.from(el.dotNav.querySelectorAll<HTMLButtonElement>('.dot'))

/* ═══════════════════════════════════════════════════
   Renderer
   ═══════════════════════════════════════════════════ */
const renderer = new AppleRenderer(el.canvasWrap)

/* ═══════════════════════════════════════════════════
   State
   ═══════════════════════════════════════════════════ */
let pageIndex = 0
let gui: GUI | null = null
let randomPageParams = createRandomAppleParams()
let editorParams: AppleParams = mergeParams({
  ...storyPages.find((p) => p.id === 'vessel')?.params,
})
let isTransitioning = false

/* ═══════════════════════════════════════════════════
   GUI (free edit mode)
   ═══════════════════════════════════════════════════ */
function destroyGui() {
  if (gui) {
    gui.destroy()
    gui = null
  }
  el.guiHost.innerHTML = ''
}

function setupGui() {
  destroyGui()
  gui = new GUI({ container: el.guiHost, title: '参数调节' })
  const params = editorParams

  const addSlider = (folder: GUI, key: keyof AppleParams, label: string, step = 0.001) => {
    const range = paramRanges[key]
    if (!range) return
    folder
      .add(params, key, range[0], range[1], step)
      .name(label)
      .onChange(() => {
        editorParams = clampParams({ ...params })
        renderer.update(editorParams)
      })
  }

  const form = gui.addFolder('核心形态')
  addSlider(form, 'height', '高度', 0.01)
  addSlider(form, 'width', '宽度', 0.01)
  addSlider(form, 'maxWidthHeight', '最宽处高度', 0.01)
  addSlider(form, 'cubicRatio', '曲线张力', 0.01)

  const dimples = gui.addFolder('凹陷')
  addSlider(dimples, 'bottomRadius', '底部开口半径', 0.005)
  addSlider(dimples, 'bottomDepth', '底部深度', 0.005)
  addSlider(dimples, 'topRadius', '顶部开口半径', 0.005)
  addSlider(dimples, 'topDepth', '顶部深度', 0.005)

  const shell = gui.addFolder('壳体')
  addSlider(shell, 'shellThickness', '壳厚度', 0.005)

  const leaf = gui.addFolder('叶子')
  leaf.add(params, 'leafEnabled').name('显示叶子').onChange(() => {
    editorParams = clampParams({ ...params })
    renderer.update(editorParams)
  })
  addSlider(leaf, 'leafLength', '叶片长度', 0.005)
  addSlider(leaf, 'leafWidth', '叶片宽度', 0.005)
  addSlider(leaf, 'leafAngle', '叶片角度', 0.01)

  const bite = gui.addFolder('咬痕')
  bite.add(params, 'biteEnabled').name('显示咬痕').onChange(() => {
    editorParams = clampParams({ ...params })
    renderer.update(editorParams)
  })
  addSlider(bite, 'biteU', '经度 U', 0.01)
  addSlider(bite, 'biteV', '纬度 V', 0.01)
  addSlider(bite, 'biteRadius', '咬痕半径', 0.01)

  const presentation = gui.addFolder('展示')
  addSlider(presentation, 'rotationY', 'Y轴旋转', 0.01)

  gui.add(
    {
      '随机生成': () => {
        editorParams = createRandomAppleParams()
        destroyGui()
        setupGui()
        renderPage()
      },
    },
    '随机生成',
  )
}

/* ═══════════════════════════════════════════════════
   Resolve params for current page
   ═══════════════════════════════════════════════════ */
function resolvePageParams(): AppleParams {
  const page = storyPages[pageIndex]
  if (page.freeEdit) return editorParams
  if (page.random) return randomPageParams
  return mergeParams(page.params)
}

/* ═══════════════════════════════════════════════════
   Text transition helpers
   ═══════════════════════════════════════════════════ */
const animatableEls = () => [el.storyImage, el.chapterLabel, el.title, el.text, el.modeBadge]

function hideText() {
  animatableEls().forEach((e) => e.classList.remove('visible'))
}

function showText() {
  animatableEls().forEach((e, i) => {
    setTimeout(() => e.classList.add('visible'), i * 60)
  })
}

/* ═══════════════════════════════════════════════════
   Render current page
   ═══════════════════════════════════════════════════ */
function renderPage() {
  const page = storyPages[pageIndex]
  const params = resolvePageParams()

  // counter
  el.counter.textContent = `${String(pageIndex + 1).padStart(2, '0')} / ${String(storyPages.length).padStart(2, '0')}`

  // chapter label
  el.chapterLabel.textContent = page.freeEdit
    ? 'Playground'
    : page.random
      ? 'Variation'
      : `Chapter ${page.label}`

  // title & text
  el.title.innerHTML = page.title.replace(/\n/g, '<br>')
  el.text.innerHTML = page.text.replace(/\n/g, '<br>')

  // mode badge
  el.modeBadge.textContent = page.freeEdit
    ? 'Free Edit'
    : page.random
      ? 'Random'
      : ''

  // dots
  dots.forEach((d, i) => d.classList.toggle('active', i === pageIndex))

  // buttons
  el.prevBtn.disabled = pageIndex === 0
  el.nextBtn.disabled = pageIndex === storyPages.length - 1

  // keyboard hint
  el.keyboardHint.classList.toggle('visible', pageIndex === 0)

  // story image
  el.storyImage.classList.remove('visible')
  if (page.imageUrl) {
    el.imageInner.style.backgroundImage = `url(${page.imageUrl})`
    el.imageInner.style.backgroundSize = 'cover'
    el.imageInner.style.backgroundPosition = 'center'
    el.imageInner.setAttribute('data-shape', page.imageShape || '')
    setTimeout(() => el.storyImage.classList.add('visible'), 0)
  } else if (page.imageGradient) {
    el.imageInner.style.background = page.imageGradient
    el.imageInner.setAttribute('data-shape', page.imageShape || '')
    setTimeout(() => el.storyImage.classList.add('visible'), 0)
  }

  // camera
  // Removed fixed camera - all pages now have free camera control

  // renderer
  renderer.setInteractive(true)  // Always enable interactive mode for free camera control
  renderer.update(params)

  // gui
  if (page.freeEdit) {
    setupGui()
  } else {
    destroyGui()
  }

  // trigger text appear
  showText()
}

/* ═══════════════════════════════════════════════════
   Navigation
   ═══════════════════════════════════════════════════ */
function goToPage(target: number) {
  const clamped = Math.max(0, Math.min(storyPages.length - 1, target))
  if (clamped === pageIndex || isTransitioning) return

  isTransitioning = true
  hideText()

  setTimeout(() => {
    pageIndex = clamped

    if (storyPages[pageIndex].random) {
      randomPageParams = createRandomAppleParams()
    }

    renderPage()
    isTransitioning = false
  }, 340)
}

// Prev / Next buttons
el.prevBtn.addEventListener('click', () => goToPage(pageIndex - 1))
el.nextBtn.addEventListener('click', () => goToPage(pageIndex + 1))

// Dot clicks
dots.forEach((dot) => {
  dot.addEventListener('click', () => {
    const idx = Number(dot.dataset.index)
    if (!isNaN(idx)) goToPage(idx)
  })
})

// Keyboard
window.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft') goToPage(pageIndex - 1)
  if (e.key === 'ArrowRight') goToPage(pageIndex + 1)
})

// Wheel navigation (debounced)
let wheelCooldown = false
window.addEventListener(
  'wheel',
  (e) => {
    if ((e.target as HTMLElement).closest('.lil-gui')) return

    if (wheelCooldown) return
    if (Math.abs(e.deltaY) < 30) return

    wheelCooldown = true
    if (e.deltaY > 0) {
      goToPage(pageIndex + 1)
    } else {
      goToPage(pageIndex - 1)
    }

    setTimeout(() => {
      wheelCooldown = false
    }, 800)
  },
  { passive: true },
)

/* ═══════════════════════════════════════════════════
   Initial render
   ═══════════════════════════════════════════════════ */
renderPage()
