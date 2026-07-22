export type BriefingType = {
  id: string
  label: string
}

export type WorkspaceTypeId =
  | 'impact-risk'
  | 'partner'
  | 'partner-tailored'
  | 'ops-to-comms'
  | 'social-graphic'
  | 'single-briefing-graphic'

export type ProbabilityTableValue = Record<string, Record<string, string>>

export type SectionValue = string | ProbabilityTableValue

export type TemplateSection = {
  id: string
  label: string
  kind: 'text' | 'probability_table'
  categories?: string[]
  days?: string[]
}

export type BriefingTemplate = {
  briefing_type: string
  title: string
  sections: TemplateSection[]
}

export type BriefingTemplateResponse = {
  briefing_type: string
  version: string
  template: BriefingTemplate
}

export type BriefingDraft = {
  draft_id: string
  briefing_type: string
  template_version: string
  sections: Record<string, SectionValue>
  status: string
  issue_time_utc: string
  valid_dates: string[]
  runtime_mode: 'operational' | 'replay'
  replay_scenario: string | null
  created_at: string
  updated_at: string
}

export type RuntimeContext = {
  status: 'ok' | 'configuration_error'
  now_utc: string | null
  system_utc: string
  data_source: 'operational' | 'replay'
  source: 'operational' | 'replay'
  clock_source: string
  scenario: string | null
  replay_now_env: string | null
  invalid_replay_now_env: string[]
  warnings: string[]
  configuration_errors: string[]
}

export type ContextItem = {
  id: string
  summary: string
}

export type PreviewResponse = {
  draft_id: string
  format: 'html'
  html: string
}

export type PdfResponse = {
  draft_id: string
  format: 'pdf'
  status: string
  message: string
}

export type PartnerImpactLevel = {
  label: string
  thresholdIndicators: string
  impact: string
  action: string
  confidence: string
}

export type PartnerSector = {
  name: string
  description: string
  hazardFamilies: string[]
  keyIndicators: string[]
  confidenceNote: string
  impactLevels: Record<string, PartnerImpactLevel>
}

export type DownstreamOutputId = 'discussion' | 'icao' | 'staff'

export type DerivedOutputStatus = {
  id: DownstreamOutputId
  label: string
  readiness: 'ready' | 'missing_inputs'
  missingSections: string[]
  html: string | null
  pdfMessage: string
}

export type SocialGraphicsTemplateId =
  | 'informed-design-event'
  | 'operational-snapshot'
  | 'decision-support-focus'
  | 'educational-slide'

export type GraphicsWorkspaceMode = 'social' | 'briefing'

export type SocialGraphicsAssetType =
  | 'logo'
  | 'icon'
  | 'photo'
  | 'background'
  | 'texture'
  | 'map'
  | 'satellite'
  | 'chart'
  | 'abstract'

export type SocialGraphicsAssetCategory =
  | 'branding'
  | 'event-icons'
  | 'aurora-geomagnetic'
  | 'solar-satellite'
  | 'radio-communications'
  | 'sector-operations'
  | 'backgrounds'
  | 'maps-charts'

export type SocialGraphicsAssetSourceType = 'local' | 'remote' | 'generated'

export type SocialGraphicsAssetLibrary = 'event-based' | 'education-outreach' | 'shared'

export type SocialGraphicsAssetRole =
  | 'background'
  | 'logo'
  | 'main-image'
  | 'secondary-image'
  | 'icon-slot'

export type SocialGraphicsAssetApplyTarget =
  | 'background'
  | 'logo'
  | 'main-image'
  | 'secondary-image'
  | 'icon-slot'
  | 'selected-image'

export type SocialGraphicsElementKind = 'rect' | 'text' | 'image' | 'line'

export type SocialGraphicsBaseElement = {
  id: string
  name: string
  kind: SocialGraphicsElementKind
  x: number
  y: number
  width: number
  height: number
  visible: boolean
  opacity: number
  locked?: boolean
}

export type SocialGraphicsRectElement = SocialGraphicsBaseElement & {
  kind: 'rect'
  fill: string
  cornerRadius: number
}

export type SocialGraphicsTextElement = SocialGraphicsBaseElement & {
  kind: 'text'
  text: string
  fill: string
  fontFamily: string
  fontSize: number
  fontWeight: number
  align: 'left' | 'center' | 'right'
  lineHeight: number
}

export type SocialGraphicsImageElement = SocialGraphicsBaseElement & {
  kind: 'image'
  src: string
  fit: 'cover' | 'contain'
  cornerRadius: number
  assetRole?: SocialGraphicsAssetRole
  linkedAssetId?: string | null
}

export type SocialGraphicsLineElement = SocialGraphicsBaseElement & {
  kind: 'line'
  stroke: string
  strokeWidth: number
}

export type SocialGraphicsElement =
  | SocialGraphicsRectElement
  | SocialGraphicsTextElement
  | SocialGraphicsImageElement
  | SocialGraphicsLineElement

export type SocialGraphicsScene = {
  version: string
  title: string
  templateId: SocialGraphicsTemplateId
  width: number
  height: number
  elements: SocialGraphicsElement[]
}

export type SocialGraphicsTemplateOption = {
  id: SocialGraphicsTemplateId
  label: string
  description: string
}

export type SocialGraphicsDraft = {
  draft_id: string
  template_id: SocialGraphicsTemplateId
  scene: SocialGraphicsScene
  status: string
  created_at: string
  updated_at: string
}

export type SocialGraphicsExportVariant = {
  variant_id: string
  label: string
  width: number
  height: number
  url: string
}

export type SocialGraphicsExportResult = {
  export_id: string
  draft_id: string | null
  created_at: string
  variants: SocialGraphicsExportVariant[]
}

export type SocialGraphicsAsset = {
  id: string
  title: string
  description: string
  assetType: SocialGraphicsAssetType
  category: SocialGraphicsAssetCategory
  library: SocialGraphicsAssetLibrary
  tags: string[]
  audience: OpsToCommsAudience[]
  eventTypes: OpsToCommsEventType[]
  recommendedUse: string
  sourceType: SocialGraphicsAssetSourceType
  localPath?: string
  url?: string
  thumbnailPath?: string
  attribution?: string
  approvedForUse: boolean
  priority: number
  defaultApplyTarget: SocialGraphicsAssetApplyTarget
}

export type OpsToCommsEventType =
  | 'geomagnetic-storm'
  | 'solar-radiation-storm'
  | 'radio-blackout'
  | 'flare'
  | 'cme'
  | 'coronal-hole'
  | 'outlook-forecast'
  | 'other'

export type OpsToCommsSeverity =
  | 'minor'
  | 'moderate'
  | 'strong'
  | 'severe'
  | 'extreme'

export type OpsToCommsTimingStatus = 'ongoing' | 'imminent' | 'forecast' | 'past-summary'

export type OpsToCommsSector =
  | 'aviation'
  | 'satellite'
  | 'power-grid'
  | 'communications'
  | 'gnss-positioning'
  | 'human-spaceflight'
  | 'public-aurora'
  | 'government-emergency-management'

export type OpsToCommsLevel = 'low' | 'moderate' | 'high' | 'very-high'

export type OpsToCommsAudience = 'public' | 'partners' | 'internal' | 'mixed'

export type OpsToCommsCommunicationMode = 'event-based' | 'education-outreach'

export type OpsToCommsEducationTemplateFamily =
  | 'phenomena'
  | 'swpc-products-services'
  | 'sector-highlight'

export type OpsToCommsCannedStatementOption = {
  id: string
  label: string
  text: string
}

export type OpsToCommsPathId = 'social-design-review' | 'partner-design-review'

export type OpsToCommsInput = {
  communicationMode: OpsToCommsCommunicationMode
  educationTemplateFamily: OpsToCommsEducationTemplateFamily
  eventType: OpsToCommsEventType
  whatItIsOptionId: string
  whyItMattersOptionId: string
  actionsToTakeOptionId: string
  severity: OpsToCommsSeverity
  timingStatus: OpsToCommsTimingStatus
  impactedSectors: OpsToCommsSector[]
  riskLevel: OpsToCommsLevel
  impactProbability: OpsToCommsLevel
  confidence: OpsToCommsLevel
}

export type OpsToCommsRecommendation = OpsToCommsInput & {
  audience: OpsToCommsAudience
  selectedWhatItIsText: string
  selectedWhyItMattersText: string
  selectedActionsToTakeText: string | null
  recommendedPrimaryPath: OpsToCommsPathId
  recommendedSecondaryPath: OpsToCommsPathId | null
  recommendedTemplate: SocialGraphicsTemplateId
  recommendedPathTemplates: Partial<Record<OpsToCommsPathId, SocialGraphicsTemplateId>>
  recommendedAssetLibrary: SocialGraphicsAssetLibrary
  recommendedVisualType: SocialGraphicsAssetType
  recommendedVisualKeywords: string[]
  recommendedAssetTags: string[]
  recommendedAssetCategories: SocialGraphicsAssetCategory[]
  recommendedHeadlineTone: 'urgent' | 'watchful' | 'informational' | 'reassuring'
  recommendedMessageEmphasis: string
  summary: string
  generatedAt: string
}
