import type {
  OpsToCommsAudience,
  OpsToCommsCannedStatementOption,
  OpsToCommsCommunicationMode,
  OpsToCommsEducationTemplateFamily,
  OpsToCommsEventType,
  OpsToCommsInput,
  OpsToCommsLevel,
  OpsToCommsPathId,
  OpsToCommsRecommendation,
  OpsToCommsSector,
  OpsToCommsSeverity,
  OpsToCommsTimingStatus,
  SocialGraphicsAssetCategory,
  SocialGraphicsAssetLibrary,
  SocialGraphicsAssetType,
  SocialGraphicsTemplateId,
} from '../types'

export const opsToCommsEventOptions: { value: OpsToCommsEventType; label: string }[] = [
  { value: 'geomagnetic-storm', label: 'Geomagnetic storm' },
  { value: 'solar-radiation-storm', label: 'Solar radiation storm' },
  { value: 'radio-blackout', label: 'Radio blackout' },
  { value: 'flare', label: 'Flare' },
  { value: 'cme', label: 'CME' },
  { value: 'coronal-hole', label: 'Coronal hole' },
  { value: 'outlook-forecast', label: 'Outlook / forecast' },
  { value: 'other', label: 'Other' },
]

export const opsToCommsSeverityOptions: { value: OpsToCommsSeverity; label: string }[] = [
  { value: 'minor', label: 'Minor' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'strong', label: 'Strong' },
  { value: 'severe', label: 'Severe' },
  { value: 'extreme', label: 'Extreme' },
]

export const opsToCommsTimingOptions: { value: OpsToCommsTimingStatus; label: string }[] = [
  { value: 'ongoing', label: 'Ongoing' },
  { value: 'imminent', label: 'Imminent' },
  { value: 'forecast', label: 'Forecast' },
  { value: 'past-summary', label: 'Past / summary' },
]

export const opsToCommsLevelOptions: { value: OpsToCommsLevel; label: string }[] = [
  { value: 'low', label: 'Low' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'high', label: 'High' },
  { value: 'very-high', label: 'Very High' },
]

export const opsToCommsCommunicationModeOptions: {
  value: OpsToCommsCommunicationMode
  label: string
  description: string
}[] = [
  {
    value: 'event-based',
    label: 'Event Based Communication',
    description: 'Use for active hazards, event updates, response messaging, and impact communication.',
  },
  {
    value: 'education-outreach',
    label: 'Education & Outreach',
    description: 'Use for explainer graphics, awareness content, level meaning, and evergreen partner/public education.',
  },
]

export const opsToCommsEducationTemplateOptions: {
  value: OpsToCommsEducationTemplateFamily
  label: string
  description: string
}[] = [
  {
    value: 'phenomena',
    label: 'Phenomena',
    description: '',
  },
  {
    value: 'swpc-products-services',
    label: 'SWPC Products and Services',
    description: 'Reserved for future education slides about SWPC forecasts, watches, warnings, and services.',
  },
  {
    value: 'sector-highlight',
    label: 'Sector Highlight',
    description: 'Reserved for future education slides focused on how a sector experiences space weather.',
  },
]

const defaultOpsToCommsWhatItIsOptions: OpsToCommsCannedStatementOption[] = [
  {
    id: 'what-this-means-1',
    label: 'Active conditions may affect some users',
    text: 'This level means space weather conditions are active enough to affect some users, but impacts will vary by location, system, and timing.',
  },
  {
    id: 'what-this-means-2',
    label: 'Operating environment has changed',
    text: 'This condition signals a meaningful change in the operating environment and may reduce normal communications, timing, or planning confidence.',
  },
  {
    id: 'what-this-means-3',
    label: 'Impacts depend on exposure',
    text: 'The level of impact depends on the system, location, operational sensitivity, and how long disturbed space weather conditions persist.',
  },
  {
    id: 'what-this-means-4',
    label: 'Conditions may be noticeable',
    text: 'Space weather conditions may be noticeable to affected users, especially those relying on radio communication, GNSS, satellites, power systems, or aurora observations.',
  },
  {
    id: 'what-this-means-5',
    label: 'Forecast confidence may evolve',
    text: 'Forecast confidence can change as new solar wind, solar imagery, and ground-based observations become available.',
  },
]

const cmeWhatItIsOptions: OpsToCommsCannedStatementOption[] = [
  {
    id: 'cme-what-it-is-1',
    label: 'CME Definition 1',
    text: 'A coronal mass ejection, or CME, is a large cloud of magnetized solar material released from the Sun into space.',
  },
  {
    id: 'cme-what-it-is-2',
    label: 'CME Definition 2',
    text: 'CMEs occur when the Sun expels plasma and magnetic field outward, sometimes in the direction of Earth.',
  },
  {
    id: 'cme-what-it-is-3',
    label: 'CME Definition 3',
    text: 'A CME is a burst of solar gas and magnetic energy that can travel through interplanetary space.',
  },
  {
    id: 'cme-what-it-is-4',
    label: 'CME Definition 4',
    text: 'Coronal mass ejections are major solar eruptions that send billions of tons of charged particles away from the Sun.',
  },
  {
    id: 'cme-what-it-is-5',
    label: 'CME Definition 5',
    text: 'A CME is not light or radiation alone. It is a moving structure of solar plasma and magnetic field traveling outward from the Sun.',
  },
]

const defaultOpsToCommsWhyItMattersOptions: OpsToCommsCannedStatementOption[] = [
  {
    id: 'why-it-matters-1',
    label: 'Moderate disturbances can affect operations',
    text: 'It matters because even moderate disturbances can affect mission timing, routing, and communication confidence for affected sectors.',
  },
  {
    id: 'why-it-matters-2',
    label: 'Systems people rely on may be affected',
    text: 'It matters because changing space weather conditions can affect the systems people rely on, even when impacts are not visible to everyone.',
  },
  {
    id: 'why-it-matters-3',
    label: 'Impacts can vary by sector',
    text: 'It matters because the same space weather event can create different impacts for aviation, power, satellite, communications, GNSS, and public audiences.',
  },
  {
    id: 'why-it-matters-4',
    label: 'Timing supports preparedness',
    text: 'It matters because clear timing and confidence information helps partners decide when to monitor, prepare, message, or adjust operations.',
  },
  {
    id: 'why-it-matters-5',
    label: 'Plain language supports action',
    text: 'It matters because clear, impact-based language helps users understand what could happen and what information to watch next.',
  },
]

const cmeWhyItMattersOptions: OpsToCommsCannedStatementOption[] = [
  {
    id: 'cme-why-it-matters-1',
    label: 'CME Relevance 1',
    text: 'When a CME reaches Earth, it can disturb Earth’s magnetic field and trigger geomagnetic storm conditions.',
  },
  {
    id: 'cme-why-it-matters-2',
    label: 'CME Relevance 2',
    text: 'CMEs matter because they can affect technologies we rely on, including power systems, communications, satellites, and navigation signals.',
  },
  {
    id: 'cme-why-it-matters-3',
    label: 'CME Relevance 3',
    text: 'A CME directed toward Earth can increase the risk of impacts to space-based and ground-based systems.',
  },
  {
    id: 'cme-why-it-matters-4',
    label: 'CME Relevance 4',
    text: 'Strong CMEs can drive space weather that disrupts operations, increases uncertainty in positioning and communications, and enhances auroral activity.',
  },
  {
    id: 'cme-why-it-matters-5',
    label: 'CME Relevance 5',
    text: 'Understanding CMEs helps forecasters anticipate when solar activity could create operational impacts for critical infrastructure and the public.',
  },
]

export function opsToCommsWhatItIsOptionsForEvent(
  eventType: OpsToCommsEventType,
): OpsToCommsCannedStatementOption[] {
  return eventType === 'cme' ? cmeWhatItIsOptions : defaultOpsToCommsWhatItIsOptions
}

export function opsToCommsWhyItMattersOptionsForEvent(
  eventType: OpsToCommsEventType,
): OpsToCommsCannedStatementOption[] {
  return eventType === 'cme' ? cmeWhyItMattersOptions : defaultOpsToCommsWhyItMattersOptions
}

export const opsToCommsWhatItIsOptions = defaultOpsToCommsWhatItIsOptions
export const opsToCommsWhyItMattersOptions = defaultOpsToCommsWhyItMattersOptions

export const opsToCommsActionsToTakeOptions: OpsToCommsCannedStatementOption[] = [
  {
    id: 'actions-to-take-1',
    label: 'Readiness Guidance',
    text: 'Review the latest forecast, highlight the most likely impacts, and use clear timing language so affected users know when to pay closer attention.',
  },
  {
    id: 'actions-to-take-2',
    label: 'Public Guidance',
    text: 'Use simple, direct language, avoid overstatement, and focus on what people may notice, who may be affected, and what action is useful now.',
  },
]

export function educationTopicRequiresActions(eventType: OpsToCommsEventType): boolean {
  return (
    eventType === 'geomagnetic-storm' ||
    eventType === 'solar-radiation-storm' ||
    eventType === 'radio-blackout'
  )
}

function resolveStatement(
  options: OpsToCommsCannedStatementOption[],
  optionId: string,
): OpsToCommsCannedStatementOption {
  const fallbackOption = options[0]
  if (!fallbackOption) {
    throw new Error('Canned statement library is not configured.')
  }
  return options.find((option) => option.id === optionId) ?? fallbackOption
}

export const opsToCommsSectorOptions: { value: OpsToCommsSector; label: string }[] = [
  { value: 'aviation', label: 'Aviation' },
  { value: 'satellite', label: 'Satellite' },
  { value: 'power-grid', label: 'Power grid' },
  { value: 'communications', label: 'Communications' },
  { value: 'gnss-positioning', label: 'GNSS / positioning' },
  { value: 'human-spaceflight', label: 'Human spaceflight' },
  { value: 'public-aurora', label: 'Public / aurora' },
  { value: 'government-emergency-management', label: 'Government / emergency management' },
]

const scoreMap: Record<OpsToCommsLevel | OpsToCommsSeverity, number> = {
  low: 1,
  minor: 1,
  moderate: 2,
  high: 3,
  strong: 3,
  'very-high': 4,
  severe: 4,
  extreme: 5,
}

function levelScore(level: OpsToCommsLevel | OpsToCommsSeverity): number {
  return scoreMap[level]
}

export function createDefaultOpsToCommsInput(): OpsToCommsInput {
  const defaultWhatItIsOptions = opsToCommsWhatItIsOptionsForEvent('geomagnetic-storm')
  const defaultWhyItMattersOptions = opsToCommsWhyItMattersOptionsForEvent('geomagnetic-storm')
  return {
    communicationMode: 'event-based',
    educationTemplateFamily: 'phenomena',
    eventType: 'geomagnetic-storm',
    whatItIsOptionId: defaultWhatItIsOptions[0]?.id ?? '',
    whyItMattersOptionId: defaultWhyItMattersOptions[0]?.id ?? '',
    actionsToTakeOptionId: opsToCommsActionsToTakeOptions[0]?.id ?? '',
    severity: 'moderate',
    timingStatus: 'forecast',
    impactedSectors: ['aviation', 'communications'],
    riskLevel: 'moderate',
    impactProbability: 'moderate',
    confidence: 'moderate',
  }
}

export function opsToCommsPathLabel(path: OpsToCommsPathId): string {
  return path === 'social-design-review'
    ? 'Social Media Design Review'
    : 'Partner Graphic Design Review'
}

function includesAnySector(input: OpsToCommsInput, sectors: OpsToCommsSector[]): boolean {
  return sectors.some((sector) => input.impactedSectors.includes(sector))
}

function deriveAudience(input: OpsToCommsInput): OpsToCommsAudience {
  const hasPublicSector = includesAnySector(input, ['public-aurora'])
  const hasPartnerSector = includesAnySector(input, [
    'aviation',
    'satellite',
    'power-grid',
    'communications',
    'gnss-positioning',
    'human-spaceflight',
    'government-emergency-management',
  ])

  if (hasPublicSector && hasPartnerSector) {
    return 'mixed'
  }
  if (hasPartnerSector) {
    return 'partners'
  }
  if (hasPublicSector) {
    return 'public'
  }

  return input.communicationMode === 'education-outreach' ? 'public' : 'mixed'
}

function withEducationDefaults(input: OpsToCommsInput): OpsToCommsInput {
  if (input.communicationMode !== 'education-outreach') {
    return input
  }

  return {
    ...input,
    educationTemplateFamily: input.educationTemplateFamily ?? 'phenomena',
    severity: educationTopicRequiresActions(input.eventType) ? 'strong' : 'moderate',
    timingStatus: educationTopicRequiresActions(input.eventType) ? 'past-summary' : 'forecast',
    riskLevel: educationTopicRequiresActions(input.eventType) ? 'moderate' : 'low',
    impactProbability: 'moderate',
    confidence: 'high',
  }
}

type NormalizedOpsToCommsInput = OpsToCommsInput & { audience: OpsToCommsAudience }

function determineTone(input: OpsToCommsInput): OpsToCommsRecommendation['recommendedHeadlineTone'] {
  const severity = levelScore(input.severity)
  const risk = levelScore(input.riskLevel)
  const confidence = levelScore(input.confidence)

  if ((input.timingStatus === 'ongoing' || input.timingStatus === 'imminent') && severity >= 4 && risk >= 3) {
    return 'urgent'
  }

  if (input.timingStatus === 'forecast' && confidence <= 2) {
    return 'watchful'
  }

  if (input.timingStatus === 'past-summary') {
    return 'reassuring'
  }

  return confidence >= 3 ? 'informational' : 'watchful'
}

function determineMessageEmphasis(input: NormalizedOpsToCommsInput): string {
  const hasPartnerSector = includesAnySector(input, [
    'aviation',
    'satellite',
    'power-grid',
    'communications',
    'gnss-positioning',
    'human-spaceflight',
    'government-emergency-management',
  ])
  const hasPublicSector = includesAnySector(input, ['public-aurora'])

  if (input.audience === 'partners' || input.audience === 'internal') {
    return 'Sector impacts, operational timing, and confidence framing'
  }

  if (input.audience === 'public' && input.timingStatus !== 'past-summary') {
    return 'Public awareness, plain-language impacts, and action-oriented messaging'
  }

  if (hasPartnerSector && hasPublicSector) {
    return 'Dual-track messaging with public awareness supported by sector impact context'
  }

  return 'Operational context, likely impacts, and recommended communication posture'
}

function uniqueValues<T>(values: T[]): T[] {
  return [...new Set(values)]
}

function determineVisualGuidance(input: NormalizedOpsToCommsInput): {
  recommendedAssetLibrary: SocialGraphicsAssetLibrary
  recommendedVisualType: SocialGraphicsAssetType
  recommendedVisualKeywords: string[]
  recommendedAssetTags: string[]
  recommendedAssetCategories: SocialGraphicsAssetCategory[]
} {
  const severity = levelScore(input.severity)
  const risk = levelScore(input.riskLevel)
  const confidence = levelScore(input.confidence)
  const publicFacing = input.audience === 'public' || input.audience === 'mixed'
  const partnerFacing = input.audience === 'partners' || input.audience === 'internal' || input.audience === 'mixed'
  const urgent = input.timingStatus === 'ongoing' || input.timingStatus === 'imminent'
  const forecastLike = input.timingStatus === 'forecast' || input.eventType === 'outlook-forecast'
  const auroraRelevant = includesAnySector(input, ['public-aurora'])
  const sectorFocused = includesAnySector(input, [
    'aviation',
    'satellite',
    'power-grid',
    'communications',
    'gnss-positioning',
    'human-spaceflight',
    'government-emergency-management',
  ])

  let recommendedVisualType: SocialGraphicsAssetType = forecastLike ? 'chart' : 'abstract'
  let recommendedAssetLibrary: SocialGraphicsAssetLibrary =
    input.communicationMode === 'education-outreach' ? 'education-outreach' : 'event-based'
  const recommendedVisualKeywords = ['space weather', 'SWPC', input.eventType.replace(/-/g, ' ')]
  const recommendedAssetTags = ['approved', input.audience, input.timingStatus]
  const recommendedAssetCategories: SocialGraphicsAssetCategory[] = ['backgrounds']

  if (input.communicationMode === 'education-outreach') {
    recommendedVisualType = 'icon'
    recommendedAssetLibrary = 'education-outreach'
    recommendedAssetTags.push('educational', 'explainer', 'awareness')
    recommendedAssetCategories.push('event-icons')
    recommendedVisualKeywords.push('education', 'what this means', 'outreach graphic')
    if (educationTopicRequiresActions(input.eventType)) {
      recommendedVisualKeywords.push('actions to take', 'scale infographic')
      recommendedAssetTags.push('scale infographic')
    }
  }

  if (forecastLike) {
    recommendedVisualType = partnerFacing && !publicFacing ? 'chart' : 'background'
    recommendedAssetCategories.push('maps-charts')
    recommendedAssetTags.push('forecast', 'planning', 'confidence')
    recommendedVisualKeywords.push('outlook', 'forecast', 'planning')
  }

  if (input.eventType === 'geomagnetic-storm' || input.eventType === 'coronal-hole') {
    if (publicFacing || auroraRelevant) {
      recommendedVisualType = urgent && severity >= 3 ? 'photo' : 'background'
      recommendedAssetCategories.push('aurora-geomagnetic')
      recommendedAssetTags.push('geomagnetic', 'aurora', 'contrast')
      recommendedVisualKeywords.push('geomagnetic', 'aurora', 'northern lights')
    } else {
      recommendedVisualType = 'map'
      recommendedAssetCategories.push('maps-charts', 'sector-operations')
      recommendedAssetTags.push('geomagnetic', 'operations', 'sector-risk')
      recommendedVisualKeywords.push('geomagnetic impacts', 'sector risk', 'operations')
    }
  }

  if (input.eventType === 'radio-blackout') {
    recommendedVisualType = publicFacing && urgent ? 'icon' : 'map'
    recommendedAssetCategories.push('radio-communications')
    recommendedAssetTags.push('communications', 'HF', 'radio blackout')
    recommendedVisualKeywords.push('communications', 'HF degradation', 'radio blackout')
  }

  if (input.eventType === 'solar-radiation-storm' || input.eventType === 'flare' || input.eventType === 'cme') {
    recommendedVisualType = publicFacing && !sectorFocused ? 'satellite' : 'chart'
    recommendedAssetCategories.push('solar-satellite')
    recommendedAssetTags.push('solar', 'satellite', 'space environment')
    recommendedVisualKeywords.push('solar imagery', 'satellite view', 'space weather source region')
    if (input.eventType === 'cme') {
      recommendedAssetTags.push('cme-library', 'ENLIL', 'timeline', 'impacted sectors')
      recommendedVisualKeywords.push('coronal mass ejection', 'ENLIL depiction', 'timeline viewer', 'impacted sectors')
      recommendedAssetCategories.push('maps-charts', 'sector-operations')
    }
  }

  if (sectorFocused) {
    recommendedAssetCategories.push('sector-operations', 'maps-charts')
    recommendedAssetTags.push('impact-focused', 'operations', 'decision support')
    recommendedVisualKeywords.push('impacts', 'operations', 'decision support')
  }

  if (includesAnySector(input, ['aviation'])) {
    recommendedAssetTags.push('aviation')
    recommendedVisualKeywords.push('aviation routing')
  }
  if (includesAnySector(input, ['communications'])) {
    recommendedAssetTags.push('communications')
    recommendedVisualKeywords.push('communications network')
  }
  if (includesAnySector(input, ['gnss-positioning'])) {
    recommendedAssetTags.push('GNSS')
    recommendedVisualKeywords.push('GNSS positioning')
  }
  if (includesAnySector(input, ['power-grid'])) {
    recommendedAssetTags.push('power grid')
    recommendedVisualKeywords.push('power grid operations')
  }
  if (includesAnySector(input, ['satellite', 'human-spaceflight'])) {
    recommendedAssetTags.push('satellite')
    recommendedVisualKeywords.push('satellite operations')
  }

  if (publicFacing && urgent && risk >= 3) {
    recommendedAssetTags.push('high-contrast', 'public-awareness')
    recommendedVisualKeywords.push('clear public message', 'high contrast')
  }

  if (partnerFacing && confidence >= 3) {
    recommendedAssetTags.push('confidence framing', 'partner-ready')
    recommendedVisualKeywords.push('confidence framing', 'operational timing')
  }

  if (input.audience === 'internal') {
    recommendedAssetTags.push('technical', 'internal')
    recommendedVisualKeywords.push('technical context', 'internal decision support')
  }

  if (publicFacing && urgent) {
    recommendedAssetTags.push('informed-design', 'actions', 'severity scale')
    recommendedAssetCategories.push('event-icons')
    recommendedVisualKeywords.push('impact graphic', 'actions to take', 'severity scale')
  }

  if ((input.timingStatus === 'forecast' || input.timingStatus === 'past-summary') && confidence >= 2) {
    recommendedAssetTags.push('educational', 'explainer')
    recommendedAssetCategories.push('event-icons')
    recommendedVisualKeywords.push('what this means', 'explainer graphic', 'education')
  }

  return {
    recommendedAssetLibrary,
    recommendedVisualType,
    recommendedVisualKeywords: uniqueValues(recommendedVisualKeywords),
    recommendedAssetTags: uniqueValues(recommendedAssetTags),
    recommendedAssetCategories: uniqueValues(recommendedAssetCategories),
  }
}

function recommendPathTemplates(
  input: NormalizedOpsToCommsInput,
  primaryPath: OpsToCommsPathId,
  secondaryPath: OpsToCommsPathId | null,
): Partial<Record<OpsToCommsPathId, SocialGraphicsTemplateId>> {
  const severity = levelScore(input.severity)
  const risk = levelScore(input.riskLevel)
  const confidence = levelScore(input.confidence)
  const publicFacing = input.audience === 'public' || input.audience === 'mixed'
  const urgent = input.timingStatus === 'ongoing' || input.timingStatus === 'imminent'
  const educationLean =
    input.communicationMode === 'education-outreach' ||
    ((input.timingStatus === 'forecast' || input.timingStatus === 'past-summary' || input.audience === 'mixed') &&
    confidence >= 2 &&
    input.audience !== 'internal')

  const socialTemplate: SocialGraphicsTemplateId =
    educationLean && publicFacing
      ? 'educational-slide'
      : publicFacing &&
          urgent &&
          (severity >= 3 || risk >= 3)
      ? 'educational-slide'
      : 'educational-slide'

  const partnerTemplate: SocialGraphicsTemplateId =
    input.timingStatus === 'forecast' || input.eventType === 'outlook-forecast'
      ? 'operational-snapshot'
      : input.audience === 'internal'
        ? 'decision-support-focus'
        : 'operational-snapshot'

  const templates: Partial<Record<OpsToCommsPathId, SocialGraphicsTemplateId>> = {
    'social-design-review': socialTemplate,
    'partner-design-review': partnerTemplate,
  }

  return {
    [primaryPath]: templates[primaryPath],
    ...(secondaryPath ? { [secondaryPath]: templates[secondaryPath] } : {}),
  }
}

export function buildOpsToCommsRecommendation(input: OpsToCommsInput): OpsToCommsRecommendation {
  const normalizedInput = withEducationDefaults(input)
  const selectedWhatItIs = resolveStatement(
    opsToCommsWhatItIsOptionsForEvent(normalizedInput.eventType),
    normalizedInput.whatItIsOptionId,
  )
  const selectedWhyItMatters = resolveStatement(
    opsToCommsWhyItMattersOptionsForEvent(normalizedInput.eventType),
    normalizedInput.whyItMattersOptionId,
  )
  const selectedActionsToTake = educationTopicRequiresActions(normalizedInput.eventType)
    ? resolveStatement(opsToCommsActionsToTakeOptions, normalizedInput.actionsToTakeOptionId)
    : null
  const audience = deriveAudience(normalizedInput)
  const inputWithAudience = { ...normalizedInput, audience }

  const severity = levelScore(normalizedInput.severity)
  const risk = levelScore(normalizedInput.riskLevel)
  const probability = levelScore(normalizedInput.impactProbability)
  const confidence = levelScore(normalizedInput.confidence)

  const publicWeight =
    (audience === 'public' ? 3 : 0) +
    (audience === 'mixed' ? 2 : 0) +
    (includesAnySector(normalizedInput, ['public-aurora']) ? 2 : 0) +
    ((normalizedInput.timingStatus === 'ongoing' || normalizedInput.timingStatus === 'imminent') ? 2 : 0) +
    (severity >= 4 ? 2 : 0) +
    (risk >= 3 ? 1 : 0)

  const partnerWeight =
    (audience === 'partners' ? 3 : 0) +
    (audience === 'mixed' ? 2 : 0) +
    (audience === 'internal' ? 2 : 0) +
    (includesAnySector(normalizedInput, [
      'aviation',
      'satellite',
      'power-grid',
      'communications',
      'gnss-positioning',
      'human-spaceflight',
      'government-emergency-management',
    ])
      ? 2
      : 0) +
    (normalizedInput.eventType === 'outlook-forecast' || normalizedInput.timingStatus === 'forecast' ? 2 : 0) +
    (confidence >= 3 ? 1 : 0)

  let recommendedPrimaryPath: OpsToCommsPathId =
    publicWeight >= partnerWeight ? 'social-design-review' : 'partner-design-review'
  let recommendedSecondaryPath: OpsToCommsPathId | null = null

  if (normalizedInput.communicationMode === 'education-outreach') {
    recommendedPrimaryPath = 'social-design-review'
    recommendedSecondaryPath =
      audience === 'partners' || audience === 'internal' || audience === 'mixed'
        ? 'partner-design-review'
        : null
  }

  const shouldRecommendBoth =
    audience === 'mixed' ||
    (publicWeight >= 5 && partnerWeight >= 5) ||
    (severity >= 4 && probability >= 3 && confidence >= 3)

  if (shouldRecommendBoth) {
    recommendedSecondaryPath =
      recommendedPrimaryPath === 'social-design-review'
        ? 'partner-design-review'
        : 'social-design-review'
  }

  if (
    normalizedInput.communicationMode !== 'education-outreach' &&
    normalizedInput.eventType === 'outlook-forecast' &&
    audience !== 'public'
  ) {
    recommendedPrimaryPath = 'partner-design-review'
    recommendedSecondaryPath = audience === 'mixed' ? 'social-design-review' : null
  }

  if (
    normalizedInput.communicationMode !== 'education-outreach' &&
    audience === 'public' &&
    normalizedInput.timingStatus !== 'past-summary' &&
    severity >= 3
  ) {
    recommendedPrimaryPath = 'social-design-review'
    recommendedSecondaryPath = shouldRecommendBoth ? 'partner-design-review' : recommendedSecondaryPath
  }

  const recommendedPathTemplates = recommendPathTemplates(
    inputWithAudience,
    recommendedPrimaryPath,
    recommendedSecondaryPath,
  )

  const recommendedTemplate =
    recommendedPathTemplates[recommendedPrimaryPath] ??
    (recommendedPrimaryPath === 'social-design-review' ? 'educational-slide' : 'operational-snapshot')

  const tone = determineTone(inputWithAudience)
  const emphasis = determineMessageEmphasis(inputWithAudience)
  const visualGuidance = determineVisualGuidance(inputWithAudience)

  const primaryLabel = opsToCommsPathLabel(recommendedPrimaryPath)
  const sectorContext =
    normalizedInput.impactedSectors.length > 0
      ? `with emphasis on ${normalizedInput.impactedSectors.length > 1 ? 'cross-sector impacts' : 'sector risk'}`
      : 'with emphasis on operational context'
  const urgencyContext =
    normalizedInput.timingStatus === 'ongoing' || normalizedInput.timingStatus === 'imminent'
      ? 'elevated urgency'
      : normalizedInput.timingStatus === 'forecast'
        ? 'forward-looking planning'
        : 'post-event summary'

  const trackContext =
    normalizedInput.communicationMode === 'education-outreach'
      ? normalizedInput.educationTemplateFamily === 'phenomena'
        ? 'a phenomena-based education and outreach approach'
        : normalizedInput.educationTemplateFamily === 'swpc-products-services'
          ? 'an SWPC products and services education approach'
          : 'a sector highlight education approach'
      : 'an event-based communication approach'

  const summary = `Based on the selected event context, this case is best suited for ${primaryLabel.toLowerCase()} using ${trackContext}, ${sectorContext}, ${urgencyContext}, and ${emphasis.toLowerCase()}.`

  return {
    ...normalizedInput,
    audience,
    selectedWhatItIsText: selectedWhatItIs.text,
    selectedWhyItMattersText: selectedWhyItMatters.text,
    selectedActionsToTakeText: selectedActionsToTake?.text ?? null,
    recommendedPrimaryPath,
    recommendedSecondaryPath,
    recommendedTemplate,
    recommendedPathTemplates,
    ...visualGuidance,
    recommendedHeadlineTone: tone,
    recommendedMessageEmphasis: emphasis,
    summary,
    generatedAt: new Date().toISOString(),
  }
}
