<script setup lang="ts">
import { ref } from 'vue'
import { synopsisRequest, type ReviewedSynopsis } from '../synopsis/review'
defineProps<{ source?: ReviewedSynopsis | null }>()
const emit = defineEmits<{ apply: [item: ReviewedSynopsis] }>()
const review = ref<ReviewedSynopsis | null>(null), error = ref(''), busy = ref(false)
async function check() {
  busy.value = true; error.value = ''; review.value = null
  try {
    review.value = (await synopsisRequest('reviewed')).item
    if (!review.value) error.value = 'No reviewed Synopsis in this application mode yet.'
  } catch (cause) { error.value = String(cause) }
  finally { busy.value = false }
}
</script>
<template>
  <div class="synopsis-reuse">
    <button type="button" :disabled="busy" @click="check">Load reviewed Synopsis</button>
    <small v-if="source">Based on Synopsis v{{ source.version }} · {{ source.reporting_end_utc }} · {{ source.runtime.data_source }}</small>
    <p v-if="error" role="status">{{ error }}</p>
    <div v-if="review" class="reuse-preview">
      <small>Synopsis v{{ review.version }} · {{ review.reporting_start_utc }} to {{ review.reporting_end_utc }}</small>
      <p>{{ review.text }}</p>
      <button type="button" @click="emit('apply', review); review = null">Replace narrative with this version</button>
      <button type="button" @click="review = null">Cancel</button>
    </div>
  </div>
</template>
<style scoped>
.synopsis-reuse { display:grid; gap:8px; margin-bottom:12px; }
.synopsis-reuse button { padding:8px 12px; border:1px solid #4b8198; border-radius:4px; color:#bfeaff; background:#143246; justify-self:start; }
.synopsis-reuse small { color:#9fb8c8; }
.reuse-preview { padding:12px; border:1px solid #48726c; background:#102c30; border-radius:4px; }
.reuse-preview p { white-space:pre-wrap; max-height:240px; overflow:auto; margin:10px 0; }
</style>
