export function parseUtc(value: string | null | undefined): Date | null {
  if (!value) return null
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

export function formatIssueTime(value: string | null | undefined): string {
  const date = parseUtc(value)
  if (!date) return 'Issue time unavailable'
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: 'UTC',
    weekday: 'short',
    month: 'short',
    day: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).formatToParts(date)
  const get = (type: Intl.DateTimeFormatPartTypes) => parts.find((part) => part.type === type)?.value ?? ''
  return `${get('hour')}${get('minute')} UTC ${get('weekday')} ${get('month')} ${get('day')} ${get('year')}`
}

export function formatTailoredIssueTime(value: string | null | undefined): string {
  const date = parseUtc(value)
  if (!date) return 'Issue time unavailable'
  const weekday = new Intl.DateTimeFormat('en-US', { timeZone: 'UTC', weekday: 'short' }).format(date)
  const datePart = new Intl.DateTimeFormat('en-US', {
    timeZone: 'UTC', month: 'short', day: '2-digit', year: 'numeric',
  }).format(date)
  const timePart = `${date.getUTCHours().toString().padStart(2, '0')}${date.getUTCMinutes().toString().padStart(2, '0')}`
  return `${weekday} ${datePart} | ${timePart} UTC`
}

export function toDatetimeLocal(value: string | null | undefined): string {
  const date = parseUtc(value)
  return date ? date.toISOString().slice(0, 16) : ''
}

export function fromDatetimeLocal(value: string): string | null {
  if (!value) return null
  const parsed = new Date(`${value}:00Z`)
  return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString().replace('.000Z', 'Z')
}

export function forecastDayLabels(value: string | null | undefined): string[] {
  const issue = parseUtc(value)
  if (!issue) return ['Day 1', 'Day 2', 'Day 3']
  return [0, 1, 2].map((offset) => {
    const date = new Date(issue)
    date.setUTCDate(date.getUTCDate() + offset)
    const label = new Intl.DateTimeFormat('en-US', {
      timeZone: 'UTC', month: 'short', day: 'numeric', weekday: 'short',
    }).format(date)
    return `Day ${offset + 1}\n${label.replace(', ', ' (')})`
  })
}
