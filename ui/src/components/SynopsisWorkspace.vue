<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { createBundle, createDraft, getBundle, getDraft, getHealth } from '../synopsis/api'
import type { Bundle, Draft, Health } from '../synopsis/types'

const text = ref('')
const version = ref(0)
const bundle = ref<Bundle | null>(null)
const draft = ref<Draft | null>(null)
const health = ref<Health | null>(null)
const busy = ref(false)
const message = ref('')
const error = ref('')
const selectedSentence = ref('')
const sentences = computed(() => draft.value?.sections.flatMap(section => section.sentences) ?? [])
const evidence = computed(() => {
  const sentence = sentences.value.find(item => item.sentence_id === selectedSentence.value)
  return bundle.value?.fact_ledger.filter(fact => !sentence || sentence.support_fact_ids.includes(fact.ledger_fact_id)) ?? []
})

async function load() {
  busy.value = true
  try {
    const response = await fetch('/api/v1/space-weather-summary/workspace')
    if (!response.ok) throw new Error('Saved synopsis is unavailable.')
    const saved = await response.json()
    version.value = saved.version
    text.value = saved.item?.text ?? ''
    if (saved.item?.source_bundle_id) bundle.value = (await getBundle(saved.item.source_bundle_id)).item
    if (saved.item?.source_draft_id) draft.value = (await getDraft(saved.item.source_draft_id)).item
    health.value = await getHealth()
  } catch (cause) { error.value = String(cause) }
  finally { busy.value = false }
}

async function collect() {
  busy.value = true; error.value = ''; message.value = ''
  try {
    const collected = (await createBundle(null)).item
    if (collected.state !== 'ready') {
      error.value = collected.sources.flatMap(source => source.errors.map(item => item.message)).join(' ') || 'The source contexts need attention before a draft can be prepared.'
      return
    }
    const generated = (await createDraft(collected.bundle_id)).item
    bundle.value = collected; draft.value = generated; selectedSentence.value = ''
    message.value = 'Evidence collected. Review the suggested text, then use it when ready.'
  } catch (cause) { error.value = String(cause) }
  finally { busy.value = false }
}

function useDraft() {
  if (text.value.trim() && !window.confirm('Replace the current synopsis text with the evidence draft?')) return
  text.value = draft.value?.sections.map(section => `${section.heading}\n${section.sentences.map(item => item.text).join(' ')}`).join('\n\n') ?? ''
  message.value = 'Suggested text loaded for forecaster editing.'
}

async function save() {
  busy.value = true; error.value = ''; message.value = ''
  try {
    const response = await fetch('/api/v1/space-weather-summary/workspace', {
      method: 'PUT', headers: { 'Content-Type': 'application/json', 'If-Match': String(version.value) },
      body: JSON.stringify({ text: text.value, source_bundle_id: bundle.value?.bundle_id ?? null, source_draft_id: draft.value?.draft_id ?? null }),
    })
    const result = await response.json()
    if (!response.ok) throw new Error(result.description || 'Workspace could not be saved.')
    version.value = result.version
    message.value = 'Synopsis workspace saved. Product issuance is a separate step.'
  } catch (cause) { error.value = String(cause) }
  finally { busy.value = false }
}

onMounted(load)
</script>

<template>
  <section class="synopsis-workspace">
    <div class="synopsis-heading">
      <div><p class="synopsis-kicker">Recent activity & interpretation</p><h2>Space Weather Synopsis</h2><p>Build the shared assessment, then adapt it for partner briefings.</p></div>
      <button :disabled="busy" @click="collect">{{ busy ? 'Working…' : 'Collect current evidence' }}</button>
    </div>
    <p v-if="error" class="synopsis-error" role="alert">{{ error }}</p>
    <p v-if="message" class="synopsis-message" role="status">{{ message }}</p>
    <div class="synopsis-layout">
      <aside class="synopsis-panel">
        <h3>Source context</h3>
        <div v-for="name in ['Geomagnetic observations', 'Geomagnetic forecast', 'Solar activity', 'Particles', 'Edited Events']" :key="name" class="synopsis-source">
          <strong>{{ name }}</strong><span>{{ name.startsWith('Geomagnetic') ? 'Evidence adapter available' : 'Not connected yet' }}</span>
        </div>
        <p>{{ health ? `${health.runtime_mode} context` : 'Checking source service…' }}</p>
        <p v-if="bundle">Evidence cutoff: {{ bundle.cutoff_at_utc }}</p>
        <p>Current numerical drafting covers geomagnetic context only. Missing inputs remain available for manual forecaster narrative.</p>
      </aside>
      <section class="synopsis-panel synopsis-editor">
        <div class="synopsis-heading"><h3>Forecaster assessment</h3><span>Working name · Synopsis</span></div>
        <label for="synopsis-text">Observations, recent activity, and scientific interpretation</label>
        <textarea id="synopsis-text" v-model="text" placeholder="Describe the recent solar, geomagnetic, and particle environment. Explain noteworthy activity and uncertainty." />
        <p>Forecaster edits are reviewed narrative. Evidence links below apply to the original suggested sentences.</p>
        <div class="synopsis-actions"><button :disabled="busy || !text.trim()" @click="save">Save workspace</button></div>
      </section>
      <aside class="synopsis-panel">
        <div class="synopsis-heading"><h3>Evidence & suggested text</h3><button :disabled="busy || !draft" @click="useDraft">Use draft</button></div>
        <p v-if="!draft">Collect evidence to prepare a supported first draft. Existing writing stays in place while inputs are collected.</p>
        <button v-for="sentence in sentences" :key="sentence.sentence_id" class="synopsis-sentence" :class="{ selected: selectedSentence === sentence.sentence_id }" @click="selectedSentence = sentence.sentence_id">{{ sentence.text }}</button>
        <details v-if="bundle"><summary>Supporting facts · {{ evidence.length }}</summary><div v-for="fact in evidence" :key="fact.ledger_fact_id" class="synopsis-fact"><strong>{{ fact.label }}</strong><p>{{ fact.value }} {{ fact.unit }}</p><small>{{ fact.source_application }} · {{ fact.valid_at_utc }}</small></div></details>
      </aside>
    </div>
    <p class="synopsis-footnote">Routine Synopsis authoring · Event-specific summaries and product release will follow as their content and lifecycle are defined.</p>
  </section>
</template>

<style scoped>
.synopsis-workspace { display:grid; gap:12px; color:#e8eff8; }
.synopsis-heading { display:flex; align-items:center; justify-content:space-between; gap:12px; }
.synopsis-heading h2,.synopsis-heading h3 { margin:0; }
.synopsis-heading p { margin:4px 0; }
.synopsis-kicker { text-transform:uppercase; color:#f0c66b; font-size:12px; letter-spacing:.08em; }
.synopsis-layout { display:grid; grid-template-columns:minmax(190px,.65fr) minmax(360px,1.5fr) minmax(280px,1fr); gap:12px; }
.synopsis-panel { min-width:0; padding:16px; border:1px solid #2b4054; border-radius:8px; background:#0b1928; }
.synopsis-panel h3 { font-size:16px; margin:0 0 12px; }
.synopsis-panel p,.synopsis-heading span,.synopsis-footnote { color:#aabacd; font-size:13px; line-height:1.5; }
.synopsis-source { display:grid; gap:4px; padding:12px 0; border-bottom:1px solid #26384a; }
.synopsis-source span { color:#aabacd; font-size:12px; }
.synopsis-editor { display:flex; flex-direction:column; }
.synopsis-editor label { font-size:13px; margin-bottom:10px; }
textarea { flex:1; width:100%; min-height:370px; padding:14px; resize:vertical; border:1px solid #38516a; border-radius:5px; background:#06121e; color:#edf5ff; font:inherit; line-height:1.65; }
button { padding:8px 12px; background:#193e55; border:1px solid #477590; color:#bdeaff; border-radius:5px; cursor:pointer; font:inherit; font-size:13px; }
button:disabled { opacity:.45; cursor:default; }
.synopsis-actions { display:flex; justify-content:flex-end; }
.synopsis-sentence { display:block; width:100%; margin:8px 0; text-align:left; background:#102334; line-height:1.45; }
.synopsis-sentence.selected { border-color:#5fc7ff; }
.synopsis-fact { padding:10px 0; border-bottom:1px solid #26384a; font-size:13px; }
.synopsis-error { background:#4d2528; padding:12px; }
.synopsis-message { background:#153b33; padding:12px; }
@media(max-width:1050px) { .synopsis-layout { grid-template-columns:1fr; } }
</style>
