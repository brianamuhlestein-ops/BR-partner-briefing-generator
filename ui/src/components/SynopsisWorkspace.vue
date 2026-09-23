<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { createBundle, createDraft, getBundle, getDraft } from '../synopsis/api'
import { synopsisRequest, type ReviewedSynopsis } from '../synopsis/review'
import { toDatetimeLocal, fromDatetimeLocal } from '../utils/briefingTime'
import type { Bundle, Draft } from '../synopsis/types'

const exerciseDelivery = ref(false)
const text = ref(''), version = ref(0), runtimeKey = ref(''), mode = ref('')
const start = ref(''), end = ref(''), dirty = ref(false)
const bundle = ref<Bundle | null>(null), draft = ref<Draft | null>(null)
const reviewed = ref<ReviewedSynopsis | null>(null)
const busy = ref(false), message = ref(''), error = ref(''), selectedSentence = ref('')
type SourceReadout = {label:string;value:unknown;unit:string | null;at_utc:string | null}
const exercise = ref<{item:{text:string;reporting_start_utc:string;reporting_end_utc:string};record:{id:string};scenario:{notice:string};sources?:Array<{slug:string;status:string;readouts:SourceReadout[]}>} | null>(null)
const exerciseError = ref('')
const exerciseSeedId = ref<string | null>(null)
const alternateWorkspaceUrl = ref('')
const sentences = computed(() => draft.value?.sections.filter(s => s.section_id !== 'forecast').flatMap(s => s.sentences) ?? [])
const evidence = computed(() => {
  const sentence = sentences.value.find(item => item.sentence_id === selectedSentence.value)
  return bundle.value?.fact_ledger.filter(fact => !sentence || sentence.support_fact_ids.includes(fact.ledger_fact_id)) ?? []
})
const sourceNames = [{slug:'geomagnetic-observations-monitor',name:'Geomagnetic observations'}, {slug:'geomagnetic-forecast-console',name:'Geomagnetic interpretation'}, {slug:'solar',name:'Solar activity and current indices'}, {slug:'particles',name:'Particles and fluence'}, {slug:'events',name:'Edited Events'}, {slug:'radio',name:'Daily 245 MHz summary'}]
function sourceStatus(slug:string) {
  const source = bundle.value?.sources.find(s => s.application_slug === slug)
  if (source) return source.generated_at_utc ? `${source.status} | ${source.generated_at_utc}` : 'Unavailable for this reporting window'
  const sample=exercise.value?.sources?.find(s=>s.slug===slug)
  if(sample)return sample.readouts.length && !sourceReadouts(slug).length ? 'Outside the selected reporting window' : sample.status
  return slug.startsWith('geomagnetic') ? 'Not collected' : 'Not connected'
}
function sourceIssues(slug:string) {return bundle.value?.sources.find(s=>s.application_slug===slug)?.errors ?? []}
function sourceReadouts(slug:string):SourceReadout[] {
  const sample=exercise.value?.sources?.find(s=>s.slug===slug)
  if(sample)return sample.readouts.filter(r=>!r.at_utc || (Date.parse(r.at_utc)>=Date.parse(fromDatetimeLocal(start.value) ?? '') && Date.parse(r.at_utc)<=Date.parse(fromDatetimeLocal(end.value) ?? '')))
  return (bundle.value?.fact_ledger ?? []).filter(f=>f.source_application===slug).map(f=>({label:f.label,value:f.value,unit:f.unit,at_utc:f.valid_at_utc}))
}
function readoutValue(value:unknown) {return typeof value==='number' ? value.toLocaleString('en-US') : typeof value==='object' ? JSON.stringify(value) : String(value)}
async function run(action:()=>Promise<void>) {
  busy.value=true;error.value='';message.value=''
  try { await action() } catch(cause) { error.value=String(cause) } finally { busy.value=false }
}
async function load() {
  const saved=await synopsisRequest('workspace')
  version.value=saved.version;runtimeKey.value=saved.runtime_key;mode.value=saved.runtime.data_source;exerciseDelivery.value=Boolean(saved.runtime.exercise_delivery_enabled)
  const alternate=mode.value==='operational' ? saved.runtime.exercise_workspace_url : saved.runtime.operational_workspace_url
  alternateWorkspaceUrl.value=typeof alternate==='string' && /^https?:\/\//.test(alternate) ? alternate : ''
  text.value=saved.item?.text ?? '';reviewed.value=saved.reviewed
  exerciseSeedId.value=saved.item?.exercise_seed_id ?? null
  exercise.value=null;exerciseError.value=''
  start.value=toDatetimeLocal(saved.item?.reporting_start_utc ?? saved.defaults.reporting_start_utc)
  end.value=toDatetimeLocal(saved.item?.reporting_end_utc ?? saved.defaults.reporting_end_utc)
  bundle.value=null;draft.value=null;dirty.value=false
  if(saved.item?.source_bundle_id)bundle.value=(await getBundle(saved.item.source_bundle_id)).item
  if(saved.item?.source_draft_id)draft.value=(await getDraft(saved.item.source_draft_id)).item
  if(saved.runtime.data_kind==='synthetic') {
    try {
      const seed=await synopsisRequest('exercise')
      if(seed.enabled)exercise.value=seed
    } catch(cause) {exerciseError.value=`Exercise catalogue unavailable. Saved evidence is still shown. ${String(cause)}`}
  }
}
function collect() {run(async()=>{
  const collected=(await createBundle(fromDatetimeLocal(end.value))).item
  bundle.value=collected;draft.value=null;selectedSentence.value='';dirty.value=true
  if(collected.state!=='ready') {
    message.value='Some evidence needs attention. Available source details are shown; your narrative is unchanged.'
    return
  }
  draft.value=(await createDraft(collected.bundle_id)).item
  message.value='Evidence collected. Suggested observations are ready to review.'
})}
function appendSuggested() {
  const suggested=sentences.value.map(s=>s.text).join(' ')
  text.value=[text.value.trim(),suggested].filter(Boolean).join('\n\n');dirty.value=true
  message.value='Suggested observations appended. Review and edit before saving a review.'
}
async function saveDraft() {
  const saved=await synopsisRequest('workspace','PUT',{runtime_key:runtimeKey.value,text:text.value,
    reporting_start_utc:fromDatetimeLocal(start.value),reporting_end_utc:fromDatetimeLocal(end.value),
    source_bundle_id:bundle.value?.bundle_id ?? null,source_draft_id:draft.value?.draft_id ?? null,
    exercise_seed_id:exerciseSeedId.value},version.value)
  version.value=saved.version;dirty.value=false
  message.value='Draft saved.'
}
function saveReview() {run(async()=>{
  if(dirty.value || !version.value)await saveDraft()
  reviewed.value=(await synopsisRequest('reviewed','POST',{runtime_key:runtimeKey.value},version.value)).item
  message.value='Reviewed Synopsis saved. Both briefing tabs can load this exact version.'
})}
function push() {run(async()=>{
  const result=await synopsisRequest('deliver','POST',{runtime_key:runtimeKey.value},version.value)
  message.value=`Sent to Product Launcher for review (${result.receipt.candidate_id}).`
})}
onMounted(()=>run(load))
function loadExercise() {
  if(!exercise.value)return
  text.value=exercise.value.item.text
  start.value=toDatetimeLocal(exercise.value.item.reporting_start_utc)
  end.value=toDatetimeLocal(exercise.value.item.reporting_end_utc)
  exerciseSeedId.value=exercise.value.record.id
  bundle.value=null;draft.value=null;dirty.value=true
  message.value='Synthetic example loaded for editing. Refresh evidence to test the connected geomagnetic adapters.'
}
</script>

<template>
  <section class="synopsis-workspace">
    <header class="synopsis-heading"><div><h2>Space Weather Synopsis</h2><p>Recent observations, activity, and scientific interpretation</p></div><div class="synopsis-actions"><a v-if="alternateWorkspaceUrl" class="workspace-link" :href="alternateWorkspaceUrl" target="_blank" rel="noopener">{{ mode==='operational' ? 'Open test data' : 'Open operational workspace' }}</a><button :disabled="busy" @click="run(load)">{{ dirty ? 'Discard unsaved / reload' : 'Reload' }}</button></div></header>
    <p v-if="error" class="synopsis-error" role="alert">{{ error }}</p>
    <p v-if="exerciseError" class="synopsis-error" role="alert">{{ exerciseError }}</p>
    <p v-if="message" class="synopsis-message" :class="{'synopsis-attention':bundle?.state==='needs_attention'}" role="status">{{ message }}</p>
    <div v-if="exercise" class="exercise-banner"><div><strong>Shared suite exercise</strong><p>{{ exercise.scenario.notice }}</p><small>The cross-domain narrative is an exercise example. Native source collection currently covers geomagnetic observations and guidance.</small></div><button :disabled="busy" @click="loadExercise">{{ text.trim() ? 'Replace with exercise example' : 'Load exercise example' }}</button></div>
    <div class="synopsis-layout">
      <section class="synopsis-panel synopsis-editor">
        <div class="synopsis-heading"><h3>Synopsis narrative</h3><small>{{ mode }} <span v-if="dirty">| Unsaved changes</span></small></div>
        <div class="reporting-window">
          <label>Reporting start (UTC)<input v-model="start" type="datetime-local" :disabled="busy" @input="dirty=true" /></label>
          <label>Reporting cutoff (UTC)<input v-model="end" type="datetime-local" :disabled="busy" @input="dirty=true" /></label>
        </div>
        <label for="synopsis-text">Forecaster assessment</label>
        <textarea id="synopsis-text" v-model="text" :disabled="busy" @input="dirty=true" placeholder="Summarize solar activity, geomagnetic conditions, particles, and radio observations. Explain their scientific significance and any gaps in the assessment." />
        <small>Reporting period is editable; the initial 24-hour window is a working default, not an issuance cadence.</small>
        <div class="synopsis-actions"><button :disabled="busy || !text.trim()" @click="run(saveDraft)">Save draft</button><button class="save-review" :disabled="busy || !text.trim()" @click="saveReview">Save review</button><button class="push-product" :disabled="busy || dirty || !reviewed || reviewed.version!==version || (mode!=='operational' && !exerciseDelivery)" @click="push">{{ mode==='replay' ? 'Push to Exercise Launcher' : 'Push to Product Launcher' }}</button></div>
        <p v-if="reviewed" class="review-status">Reviewed v{{ reviewed.version }} | {{ reviewed.reviewed_at_utc }} <span v-if="reviewed.version!==version || dirty">| Draft has newer changes</span></p>
        <details v-if="reviewed"><summary>Reviewed product text</summary><pre>{{ reviewed.product_text }}</pre></details>
      </section>
      <aside class="synopsis-evidence">
        <section class="synopsis-panel">
          <div class="synopsis-heading"><h3>Source context</h3><button :disabled="busy || !end" @click="collect">Refresh evidence</button></div>
          <p v-if="!bundle && !exercise" class="source-empty">No evidence collected yet. Use Refresh evidence to check the connected sources.</p>
          <div v-for="source in sourceNames" :key="source.slug" class="synopsis-source"><span>{{ source.name }}</span><small>{{ sourceStatus(source.slug) }}</small><small v-for="issue in sourceIssues(source.slug)" :key="issue.code" class="source-issue">{{ issue.message }}</small><div v-for="(readout,index) in sourceReadouts(source.slug)" :key="index" class="source-readout"><span>{{ readout.label }}</span><strong>{{ readoutValue(readout.value) }} {{ readout.unit }}</strong><small v-if="readout.at_utc">{{ readout.at_utc.replace('T',' ').replace('Z',' UTC') }}</small></div></div>
        </section>
        <section class="synopsis-panel">
          <div class="synopsis-heading"><h3>Suggested observations</h3><button :disabled="busy || !sentences.length" @click="appendSuggested">Append to narrative</button></div>
          <p v-if="!sentences.length">Refresh evidence to prepare supported observation text. Missing sources remain available for manual assessment.</p>
          <button v-for="sentence in sentences" :key="sentence.sentence_id" class="synopsis-sentence" :class="{selected:selectedSentence===sentence.sentence_id}" @click="selectedSentence=sentence.sentence_id">{{ sentence.text }}</button>
          <details v-if="bundle"><summary>Supporting facts ({{ evidence.length }})</summary><div v-for="fact in evidence" :key="fact.ledger_fact_id" class="synopsis-fact"><span>{{ fact.label }}</span><p>{{ fact.value }} {{ fact.unit }}</p><small>{{ fact.source_application }} | {{ fact.valid_at_utc }}</small></div></details>
        </section>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.workspace-link {display:inline-flex;align-items:center;background:#244e63;border:1px solid #5fb8df;color:#ddf5ff;padding:8px 12px;border-radius:4px;text-decoration:none;}
.synopsis-message.synopsis-attention {background:#3b321c;color:#ffe093;}.source-issue {color:#efca81;line-height:1.4;}
.exercise-banner {display:flex;justify-content:space-between;align-items:center;gap:16px;padding:14px;border:1px solid #ad9343;border-radius:6px;background:#302b18;color:#ffe493;flex-wrap:wrap;}
.exercise-banner p {margin:6px 0;}
.synopsis-workspace { display:grid; gap:12px; color:#e8eff8; }
.synopsis-heading { display:flex; align-items:center; justify-content:space-between; gap:12px; }
.synopsis-heading h2,.synopsis-heading h3 { margin:0; }
.synopsis-heading p { margin:5px 0 0; color:#aabacd; }
.synopsis-layout { display:grid; grid-template-columns:minmax(0,1.6fr) minmax(340px,1fr); gap:16px; align-items:start; }
.synopsis-panel { min-width:0; padding:18px; border:1px solid #2b4054; border-radius:8px; background:#0b1928; }
.synopsis-editor { display:grid; gap:14px; border-top:3px solid #5fc7ff; }
.synopsis-evidence { display:grid; gap:14px; }.synopsis-evidence .synopsis-panel { border-top:3px solid #68c4ac; }
.reporting-window { display:grid; grid-template-columns:1fr 1fr; gap:14px; }.reporting-window label { display:grid; gap:6px; }
textarea,input { width:100%; min-width:0; background:#071421; color:#e8eff8; border:1px solid #4b677b; border-radius:4px; padding:10px; color-scheme:dark; }
textarea { min-height:360px; resize:vertical; line-height:1.6; }
button { border:1px solid #45697e; border-radius:4px; background:#143246; color:#e8eff8; padding:8px 12px; cursor:pointer; }button:disabled { opacity:.45; cursor:default; }
.synopsis-actions { display:flex; justify-content:flex-end; flex-wrap:wrap; gap:8px; }.save-review { background:#285979; }.push-product { background:#246658; }
.synopsis-source { display:grid; gap:4px; padding:10px 0; border-bottom:1px solid #26384a; }.synopsis-source:last-child { border-bottom:0; }
.source-readout {display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 12px;padding:6px 0;align-items:baseline;}.source-readout strong {color:#83d9ed;font-weight:500;}.source-readout small {grid-column:1/-1;}.source-empty {color:#aabacd;margin:12px 0;}
small,.review-status { color:#aabacd; }.synopsis-sentence { display:block; width:100%; margin:10px 0; text-align:left; line-height:1.5; }.synopsis-sentence.selected { border-color:#5fc7ff; }
.synopsis-fact { padding:10px 0; border-bottom:1px solid #26384a; }.synopsis-fact p { margin:4px 0; }
.synopsis-error { background:#4d2528; padding:12px; }.synopsis-message { background:#153b33; padding:12px; }summary { cursor:pointer; }pre { white-space:pre-wrap; overflow-wrap:anywhere; }
@media(max-width:1000px) { .synopsis-layout { grid-template-columns:1fr; }.reporting-window { grid-template-columns:1fr; } }
</style>
