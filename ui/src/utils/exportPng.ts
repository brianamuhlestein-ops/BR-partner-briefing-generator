import html2canvas from 'html2canvas'

export async function exportElementToPng(element: HTMLElement | null, fileName: string) {
  if (!element) {
    return
  }

  const { stage, clone, width, height } = createExportClone(element)
  document.body.appendChild(stage)

  try {
    await waitForImages(clone)

    const canvas = await html2canvas(clone, {
      backgroundColor: '#ffffff',
      scale: 2,
      useCORS: true,
      allowTaint: true,
      width,
      height,
      windowWidth: width,
      windowHeight: height,
      scrollX: 0,
      scrollY: 0,
    })

    const link = document.createElement('a')
    link.download = `${sanitizeFileName(fileName)}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } finally {
    stage.remove()
  }
}

function sanitizeFileName(value: string) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '') || 'social-graphic'
}

function createExportClone(element: HTMLElement) {
  const width = positiveInteger(element.dataset.exportWidth) ?? Math.ceil(element.offsetWidth)
  const height = positiveInteger(element.dataset.exportHeight) ?? Math.ceil(element.offsetHeight)
  const clone = element.cloneNode(true) as HTMLElement
  inlineComputedStyles(element, clone)

  clone
    .querySelectorAll('.swift-social-image-upload, .swift-social-image-fit-toggle')
    .forEach((node) => node.remove())

  clone.style.width = `${width}px`
  clone.style.height = `${height}px`
  clone.style.maxWidth = 'none'
  clone.style.boxShadow = 'none'
  clone.style.transform = 'none'

  const stage = document.createElement('div')
  stage.style.position = 'fixed'
  stage.style.left = '-10000px'
  stage.style.top = '0'
  stage.style.width = `${width}px`
  stage.style.height = `${height}px`
  stage.style.overflow = 'hidden'
  stage.style.background = '#ffffff'
  stage.style.zoom = String(1 / currentPresentationZoom())
  stage.appendChild(clone)

  return { stage, clone, width, height }
}

function positiveInteger(value: string | undefined): number | null {
  const parsed = Number.parseInt(value ?? '', 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
}

function currentPresentationZoom(): number {
  const value = window
    .getComputedStyle(document.documentElement)
    .getPropertyValue('--app-presentation-zoom')
  const parsed = Number.parseFloat(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 1
}

function inlineComputedStyles(source: Element, target: Element) {
  if (source instanceof HTMLElement && target instanceof HTMLElement) {
    const computed = window.getComputedStyle(source)
    for (const property of computed) {
      target.style.setProperty(
        property,
        computed.getPropertyValue(property),
        computed.getPropertyPriority(property),
      )
    }
  }

  const sourceChildren = Array.from(source.children)
  const targetChildren = Array.from(target.children)

  sourceChildren.forEach((sourceChild, index) => {
    const targetChild = targetChildren[index]
    if (targetChild) {
      inlineComputedStyles(sourceChild, targetChild)
    }
  })
}

async function waitForImages(element: HTMLElement) {
  const images = Array.from(element.querySelectorAll('img'))

  await Promise.all(
    images.map((image) => {
      if (image.complete) {
        return Promise.resolve()
      }

      return new Promise<void>((resolve) => {
        image.addEventListener('load', () => resolve(), { once: true })
        image.addEventListener('error', () => resolve(), { once: true })
      })
    }),
  )
}
