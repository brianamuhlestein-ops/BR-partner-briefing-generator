export type Runtime = {
  mode: "operational" | "replay";
  effective_at_utc: string;
  scenario: string | null;
  source_clock: string;
};

export type Health = {
  status: string;
  service: string;
  time_utc: string;
  scope: string;
  registered_applications: string[];
  runtime_mode: "operational" | "replay";
  replay_scenario: string | null;
};

export type SourceError = { code: string; message: string };

export type BundleSource = {
  application_slug: string;
  role: string;
  required: boolean;
  status: string;
  context_schema: string;
  context_id: string | null;
  generated_at_utc: string | null;
  lifecycle_state: string | null;
  runtime: Runtime | null;
  errors: SourceError[];
};

export type ConsistencyCheck = {
  check_id: string;
  status: "pass" | "warning" | "fail";
  message: string;
  source_applications: string[];
};

export type Fact = {
  ledger_fact_id: string;
  source_application: string;
  source_context_id: string;
  producer_fact_id: string;
  kind: string;
  label: string;
  value: unknown;
  unit: string | null;
  status: string;
  valid_at_utc: string | null;
  confidence: string | number | null;
  source_type: string;
  evidence_links: string[];
  experimental: boolean;
  not_for_alerting: boolean;
};

export type Bundle = {
  bundle_id: string;
  state: "ready" | "needs_attention";
  cutoff_at_utc: string;
  created_at_utc: string;
  runtime: Runtime;
  sources: BundleSource[];
  consistency_checks: ConsistencyCheck[];
  fact_ledger: Fact[];
  integrity: { sha256: string };
};

export type BundleSummary = Pick<Bundle, "bundle_id" | "state" | "cutoff_at_utc" | "created_at_utc" | "runtime"> & {
  source_count: number;
  fact_count: number;
  href: string;
};

export type Sentence = {
  sentence_id: string;
  text: string;
  support_fact_ids: string[];
  generation_method: string;
  validation_status: "pass" | "warning" | "fail";
  validation_findings: Array<{ code: string; severity: string; message: string }>;
};

export type DraftSection = {
  section_id: string;
  heading: string;
  sentences: Sentence[];
};

export type Draft = {
  draft_id: string;
  revision: number;
  state: "drafted" | "in_review";
  source_bundle: { bundle_id: string; integrity_sha256: string; href: string };
  created_at_utc: string;
  title: string;
  sections: DraftSection[];
  generation: { method: string; template_version: string; generated_at_utc: string };
  validation: { status: "pass" | "warning" | "fail"; findings: unknown[] };
};

export type DraftSummary = Pick<Draft, "draft_id" | "revision" | "state" | "created_at_utc"> & {
  bundle_id: string;
  href: string;
};

export type ApiCollection<T> = {
  status: string;
  items: T[];
  total: number;
};

export type ApiItem<T> = { status: string; item: T };
