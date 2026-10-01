export type WorkspaceTypeId =
  | 'synopsis'
  | 'partner'
  | 'partner-tailored'
  | 'social-graphic'

export type RuntimeContext = {
  data_kind?: 'synthetic' | null
  status: 'ok' | 'configuration_error'
  now_utc: string | null
  system_utc: string
  data_source: 'operational' | 'replay'
  source_mode?: 'live' | 'gannon' | 'standalone_replay'
  source: 'operational' | 'replay'
  clock_source: string
  scenario: string | null
  replay_now_env: string | null
  invalid_replay_now_env: string[]
  warnings: string[]
  configuration_errors: string[]
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
