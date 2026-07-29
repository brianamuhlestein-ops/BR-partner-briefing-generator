const PRINT_RESOURCE_TIMEOUT_MS = 5000

export async function exportElementToPdf(element: HTMLElement | null, title: string) {
  if (!element) {
    return
  }

  const printWindow = window.open('', '_blank', 'width=980,height=1100')
  if (!printWindow) {
    window.print()
    return
  }

  const styles = Array.from(document.querySelectorAll('link[rel="stylesheet"], style'))
    .map((node) => node.outerHTML)
    .join('\n')
  const clone = element.cloneNode(true) as HTMLElement

  printWindow.document.write(`
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <base href="${escapeHtml(document.baseURI)}" />
        <title>${escapeHtml(title)}</title>
        ${styles}
        <style>
          @page {
            size: letter;
            margin: 0.25in;
          }

          html,
          body {
            margin: 0;
            background: #ffffff !important;
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
          }

          body {
            display: block;
            padding: 0;
          }

          .partner-pdf-preview,
          .tailored-brief-page {
            width: 100% !important;
            max-width: none !important;
            min-width: 0 !important;
            margin: 0 !important;
            box-shadow: none !important;
          }

          .partner-pdf-preview {
            padding: 12px 24px 20px !important;
            font-size: 11px !important;
            line-height: 1.2 !important;
          }

          .partner-pdf-masthead {
            display: flex !important;
            margin: 0 -10px 12px !important;
            padding: 9px 12px !important;
            gap: 12px !important;
            align-items: center !important;
          }

          .partner-pdf-brand img {
            width: 38px !important;
            height: 38px !important;
          }

          .partner-pdf-brand strong,
          .partner-pdf-meta strong {
            font-size: 14px !important;
          }

          .partner-pdf-brand span,
          .partner-pdf-brand div > div,
          .partner-pdf-meta span {
            font-size: 8px !important;
          }

          .partner-pdf-title h3 {
            font-size: 18px !important;
          }

          .partner-pdf-section {
            margin-top: 10px !important;
            padding-top: 8px !important;
          }

          .partner-pdf-risk-table th,
          .partner-pdf-risk-table td {
            padding: 5px 6px !important;
            font-size: 10px !important;
          }

          .tailored-brief-page {
            padding: 0 22px 18px !important;
            font-size: 10.5px !important;
            line-height: 1.18 !important;
          }

          .tailored-masthead {
            display: flex !important;
            margin: 0 -8px 12px !important;
            padding: 8px 12px !important;
            gap: 12px !important;
            align-items: center !important;
            justify-content: space-between !important;
          }

          .tailored-brand {
            display: flex !important;
            gap: 7px !important;
            align-items: center !important;
          }

          .tailored-brand img {
            width: 34px !important;
            height: 34px !important;
          }

          .tailored-brand strong {
            font-size: 13px !important;
          }

          .tailored-brand span,
          .tailored-brand div > div {
            font-size: 7.5px !important;
          }

          .tailored-meta {
            text-align: right !important;
            white-space: nowrap !important;
          }

          .tailored-meta strong {
            font-size: 13px !important;
          }

          .tailored-meta span {
            font-size: 9px !important;
          }

          .tailored-hero {
            gap: 6px !important;
            padding-bottom: 9px !important;
          }

          .tailored-hero h1 {
            font-size: 18px !important;
          }

          .tailored-hero p {
            font-size: 10.5px !important;
          }

          .tailored-section {
            margin-top: 9px !important;
            padding-top: 7px !important;
          }

          .tailored-section h3 {
            margin-bottom: 5px !important;
            font-size: 11px !important;
          }

          .tailored-probability-grid {
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            gap: 7px !important;
          }

          .tailored-probability-card {
            padding: 8px !important;
            gap: 5px !important;
            border-radius: 6px !important;
          }

          .tailored-probability-card h4 {
            font-size: 9.5px !important;
          }

          .tailored-probability-card strong {
            font-size: 10px !important;
          }

          .tailored-probability-card ul {
            padding-left: 14px !important;
            font-size: 9.5px !important;
          }

          .tailored-probability-value {
            font-size: 15px !important;
          }

          .tailored-table th,
          .tailored-table td {
            padding: 4px 5px !important;
            font-size: 9.5px !important;
          }

          .tailored-grid {
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: 14px !important;
          }

          .tailored-footer {
            margin-top: 10px !important;
            padding-top: 8px !important;
          }

          .partner-pdf-masthead,
          .partner-pdf-section,
          .tailored-masthead,
          .tailored-section,
          .tailored-probability-card {
            break-inside: avoid;
            page-break-inside: avoid;
          }
        </style>
      </head>
      <body></body>
    </html>
  `)

  printWindow.document.body.appendChild(clone)
  printWindow.document.close()

  await waitForPrintResources(printWindow)

  if (printWindow.closed) {
    return
  }

  printWindow.addEventListener('afterprint', () => printWindow.close(), { once: true })
  printWindow.focus()
  printWindow.print()
}

async function waitForPrintResources(printWindow: Window) {
  const documentReady =
    printWindow.document.readyState === 'complete'
      ? Promise.resolve()
      : new Promise<void>((resolve) => {
          printWindow.addEventListener('load', () => resolve(), { once: true })
        })

  const stylesheetReady = Array.from(
    printWindow.document.querySelectorAll<HTMLLinkElement>('link[rel="stylesheet"]'),
  ).map((stylesheet) => {
    if (stylesheet.sheet) {
      return Promise.resolve()
    }
    return new Promise<void>((resolve) => {
      stylesheet.addEventListener('load', () => resolve(), { once: true })
      stylesheet.addEventListener('error', () => resolve(), { once: true })
    })
  })

  const imagesReady = Array.from(printWindow.document.images).map(async (image) => {
    if (image.complete) {
      return
    }
    try {
      await image.decode()
    } catch {
      // A missing optional image should not block the rest of the PDF export.
    }
  })

  const fontsReady = printWindow.document.fonts?.ready ?? Promise.resolve()
  const resourcesReady = Promise.all([documentReady, fontsReady, ...stylesheetReady, ...imagesReady])
  const timeout = new Promise<void>((resolve) => {
    window.setTimeout(resolve, PRINT_RESOURCE_TIMEOUT_MS)
  })

  await Promise.race([resourcesReady, timeout])
  await waitForPrintLayout(printWindow)
}

async function waitForPrintLayout(printWindow: Window) {
  await new Promise<void>((resolve) => {
    let settled = false
    const finish = () => {
      if (settled) return
      settled = true
      window.clearTimeout(fallback)
      resolve()
    }
    const fallback = window.setTimeout(finish, 300)

    try {
      printWindow.requestAnimationFrame(() => printWindow.requestAnimationFrame(finish))
    } catch {
      finish()
    }
  })
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}
