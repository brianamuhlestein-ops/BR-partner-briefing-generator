<script setup lang="ts">
import { computed, ref } from 'vue'

import type { PartnerSector } from '../types'

const idssMessage = `The National Weather Service is evolving from information provider to decision-support partner. Impact-Based Decision Support Services (IDSS) focus not just on what the weather is, but on what that weather means for infrastructure, operations, and public safety. By integrating likelihood and consequence, forecasters empower partners to make confident, timely decisions that save lives, protect property, and strengthen resilience to space-weather impacts.`

const likelihoodOptions = [
  { value: 1, label: 'Extremely Unlikely' },
  { value: 2, label: 'Unlikely' },
  { value: 3, label: 'As Likely as Not' },
  { value: 4, label: 'Likely' },
  { value: 5, label: 'Very Likely' },
]

const impactOptions = [
  { value: 1, label: 'No Impact' },
  { value: 2, label: 'Minor' },
  { value: 3, label: 'Moderate' },
  { value: 4, label: 'Major' },
  { value: 5, label: 'Extreme' },
]

const riskLabels = ['Little to None', 'Minor', 'Moderate', 'High', 'Extreme']
const riskColors = ['#00A878', '#FFE864', '#FF8C42', '#E84F4F', '#C12AFF']

const sectors: PartnerSector[] = [
  {
    name: 'Power Grid',
    description: 'High-voltage transmission systems affected by geomagnetically induced currents (GICs).',
    keyIndicators: ['Kp', 'dB/dt', 'Dst'],
    impactLevels: {
      '1': 'Nominal geomagnetic activity. No measurable GICs or voltage deviations.',
      '2': 'Minor GICs at high latitudes. Operators monitor alerts.',
      '3': 'Regional voltage regulation required. Possible equipment alarms.',
      '4': 'Significant GICs; transformer heating or protection trips likely.',
      '5': 'Widespread instability or blackouts. Emergency grid operations activated.',
    },
    thresholds: {
      '1': 'Kp <= 4 | dB/dt < 20 nT/min',
      '2': 'Kp = 5 (G1) | dB/dt approx 20-40 nT/min',
      '3': 'Kp = 6-7 (G2-G3) | dB/dt approx 40-80 nT/min',
      '4': 'Kp = 8 (G4) | dB/dt approx 80-120 nT/min',
      '5': 'Kp >= 9 (G5) | dB/dt > 120 nT/min',
    },
  },
  {
    name: 'Aviation & HF Communications',
    description: 'Aircraft and communication systems using HF or GNSS affected by ionospheric disturbances and radiation.',
    keyIndicators: ['>10 MeV Proton Flux', 'D-RAP Absorption Index', 'Kp'],
    impactLevels: {
      '1': 'Nominal operations; no HF degradation.',
      '2': 'Polar HF signal fading possible; flight ops monitor SWPC advisories.',
      '3': 'Polar reroutes or altitude restrictions due to elevated radiation.',
      '4': 'Widespread HF blackout; GNSS errors; operational delays.',
      '5': 'Severe radiation hazard; trans-polar routes closed; crew/passenger dose management required.',
    },
    thresholds: {
      '1': 'Proton Flux < 10 pfu @ >10 MeV (S0)',
      '2': '10-99 pfu (S1 Minor)',
      '3': '100-999 pfu (S2-S3 Moderate-Strong)',
      '4': '1,000-9,999 pfu (S4 Severe)',
      '5': '>=10,000 pfu (S5 Extreme)',
    },
  },
  {
    name: 'Satellites / Spacecraft',
    description: 'Space-based assets subject to surface charging, drag, and single-event upsets.',
    keyIndicators: ['>2 MeV Electron Flux', '>10 MeV Proton Flux', 'F10.7'],
    impactLevels: {
      '1': 'Nominal charging environment.',
      '2': 'Minor sensor anomalies or drag variations.',
      '3': 'Increased upsets, orbit perturbations; safe-mode consideration.',
      '4': 'Multiple anomalies; risk of attitude loss or data corruption.',
      '5': 'Widespread spacecraft failures or total mission loss.',
    },
    thresholds: {
      '1': 'Electron Flux < 10^3 cm^-2 s^-1 sr^-1',
      '2': '10^3-10^4 cm^-2 s^-1 sr^-1',
      '3': '10^4-10^5 cm^-2 s^-1 sr^-1',
      '4': '10^5-10^6 cm^-2 s^-1 sr^-1',
      '5': '>10^6 cm^-2 s^-1 sr^-1',
    },
  },
  {
    name: 'GPS / Navigation',
    description: 'GNSS signal degradation from ionospheric scintillation and storm-time TEC gradients.',
    keyIndicators: ['Kp', 'TEC', 'S4 Index'],
    impactLevels: {
      '1': 'Accurate positioning within nominal error budget.',
      '2': 'Minor degradation at high latitudes or dusk sector.',
      '3': 'Intermittent signal loss; increased differential errors.',
      '4': 'Regional navigation outages; aviation and survey impact.',
      '5': 'Global GNSS outage or unrecoverable error magnitudes.',
    },
    thresholds: {
      '1': 'S4 Index < 0.3 | TEC variation < 5 TECU',
      '2': 'S4 approx 0.3-0.4 | TEC 5-15 TECU',
      '3': 'S4 approx 0.4-0.6 | TEC 15-30 TECU',
      '4': 'S4 approx 0.6-0.8 | TEC 30-50 TECU',
      '5': 'S4 > 0.8 | TEC > 50 TECU',
    },
  },
  {
    name: 'Pipelines',
    description: 'Corrosion control systems influenced by geomagnetically induced voltages.',
    keyIndicators: ['dB/dt', 'Kp'],
    impactLevels: {
      '1': 'Nominal currents; corrosion control unaffected.',
      '2': 'Low-level induced voltages; monitoring initiated.',
      '3': 'Elevated rectifier currents; temporary mitigation actions.',
      '4': 'Significant corrosion potential; damage assessment required.',
      '5': 'Widespread cathodic protection failure; system damage.',
    },
    thresholds: {
      '1': 'dB/dt < 20 nT/min',
      '2': '20-40 nT/min',
      '3': '40-80 nT/min',
      '4': '80-120 nT/min',
      '5': '>120 nT/min',
    },
  },
  {
    name: 'Human Spaceflight',
    description: 'Crewed missions exposed to radiation from solar energetic particles.',
    keyIndicators: ['>100 MeV Proton Flux'],
    impactLevels: {
      '1': 'Nominal radiation levels.',
      '2': 'Minor alert; increased monitoring.',
      '3': 'Elevated exposure; re-positioning recommended.',
      '4': 'Critical dose thresholds approached; shelter procedures.',
      '5': 'Severe exposure risk; mission-critical safety protocols enacted.',
    },
    thresholds: {
      '1': 'Proton Flux < 1 pfu @ >100 MeV',
      '2': '1-9 pfu (S1)',
      '3': '10-99 pfu (S2-S3)',
      '4': '100-999 pfu (S4)',
      '5': '>=1,000 pfu (S5)',
    },
  },
  {
    name: 'Public / Auroral Visibility',
    description: 'Societal and public interest impacts including aurora visibility and communications.',
    keyIndicators: ['Kp'],
    impactLevels: {
      '1': 'Aurora visible only at high latitudes.',
      '2': 'Aurora visible mid-latitudes; minor HF disruptions.',
      '3': 'Aurora visible to lower U.S. states; occasional HF loss.',
      '4': 'Strong aurora globally; moderate radio disruptions.',
      '5': 'Extreme visual and communication impacts worldwide.',
    },
    thresholds: {
      '1': 'Kp <= 4',
      '2': 'Kp = 5',
      '3': 'Kp = 6-7',
      '4': 'Kp = 8',
      '5': 'Kp >= 9',
    },
  },
]

const selectedSectorName = ref(sectors[0]?.name ?? '')
const selectedLikelihood = ref(3)
const selectedImpact = ref(3)

const selectedSector = computed(() => {
  return sectors.find((sector) => sector.name === selectedSectorName.value) ?? sectors[0]
})

const riskLevel = computed(() => {
  return Math.ceil((selectedLikelihood.value * selectedImpact.value) / 5)
})

const riskLabel = computed(() => riskLabels[riskLevel.value - 1])
const riskColor = computed(() => riskColors[riskLevel.value - 1])
const selectedLikelihoodLabel = computed(() => {
  return likelihoodOptions.find((option) => option.value === selectedLikelihood.value)?.label ?? ''
})
const selectedImpactLabel = computed(() => {
  return impactOptions.find((option) => option.value === selectedImpact.value)?.label ?? ''
})

function cellRiskLevel(impact: number, likelihood: number): number {
  return Math.ceil((impact * likelihood) / 5)
}

function cellStyle(impact: number, likelihood: number) {
  const level = cellRiskLevel(impact, likelihood)
  const isSelected = impact === selectedImpact.value && likelihood === selectedLikelihood.value
  return {
    backgroundColor: riskColors[level - 1],
    color: level >= 3 ? '#ffffff' : '#111827',
    border: isSelected ? '3px solid #111827' : '1px solid #d8e1ea',
    boxShadow: isSelected ? '0 0 0 2px rgba(17, 24, 39, 0.2)' : 'none',
  }
}
</script>

<template>
  <div class="partner-briefing">
    <div class="partner-intro">
      <h2>Why IDSS?</h2>
      <p>{{ idssMessage }}</p>
    </div>

    <section class="partner-section">
      <h3>IDSS Sector Table</h3>
      <div class="partner-sector-buttons">
        <button
          v-for="sector in sectors"
          :key="sector.name"
          class="partner-sector-button"
          :class="{ active: sector.name === selectedSectorName }"
          @click="selectedSectorName = sector.name"
        >
          {{ sector.name }}
        </button>
      </div>

      <div v-if="selectedSector" class="table-wrap">
        <table class="partner-sector-table">
          <thead>
            <tr>
              <th colspan="4">{{ selectedSector.name }}</th>
            </tr>
            <tr>
              <th>Level</th>
              <th>Thresholds</th>
              <th>Description</th>
              <th>Key Indicators</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="level in ['1', '2', '3', '4', '5']" :key="level">
              <td><strong>{{ level }}</strong></td>
              <td>{{ selectedSector.thresholds[level] }}</td>
              <td>{{ selectedSector.impactLevels[level] }}</td>
              <td v-if="level === '1'" :rowspan="5">
                <div v-for="indicator in selectedSector.keyIndicators" :key="indicator">
                  {{ indicator }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="partner-section partner-risk-controls">
      <h3>Risk Evaluation</h3>
      <div class="partner-risk-row">
        <label>
          Probability
          <select v-model="selectedLikelihood">
            <option v-for="option in likelihoodOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>

        <label>
          Impact Level
          <select v-model="selectedImpact">
            <option v-for="option in impactOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
      </div>

      <div class="partner-risk-result">
        Probability: <strong>{{ selectedLikelihoodLabel }}</strong>, Impact:
        <strong>{{ selectedImpactLabel }}</strong>
        <span class="partner-risk-pill" :style="{ backgroundColor: riskColor }">
          {{ riskLabel }} Risk
        </span>
      </div>
    </section>

    <section class="partner-section">
      <h3>Risk Matrix</h3>
      <div class="partner-matrix-wrap">
        <div class="partner-matrix-layout">
          <table class="partner-matrix-table">
            <thead>
              <tr>
                <th></th>
                <th v-for="option in likelihoodOptions" :key="option.value">
                  {{ option.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="impact in [5, 4, 3, 2, 1]" :key="impact">
                <th>{{ impact }} ({{ impactOptions[impact - 1]?.label }})</th>
                <td
                  v-for="likelihood in [1, 2, 3, 4, 5]"
                  :key="`${impact}-${likelihood}`"
                  :style="cellStyle(impact, likelihood)"
                >
                  {{ cellRiskLevel(impact, likelihood) }}
                </td>
              </tr>
            </tbody>
          </table>

          <div class="partner-legend">
            <div class="partner-legend-title">Risk Level</div>
            <div v-for="(label, index) in riskLabels" :key="label" class="partner-legend-item" :style="{ backgroundColor: riskColors[index], color: index >= 2 ? '#ffffff' : '#111827' }">
              {{ label }}
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.partner-briefing {
  display: grid;
  gap: 20px;
}

.partner-intro {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(171, 199, 235, 0.14);
  border-left: 4px solid #4d94ff;
  border-radius: 14px;
  padding: 16px 18px;
}

.partner-intro h2 {
  color: #d8e9ff;
  margin-bottom: 8px;
}

.partner-intro p {
  margin: 0;
  color: rgba(220, 230, 244, 0.82);
}

.partner-section {
  display: grid;
  gap: 12px;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(171, 199, 235, 0.14);
  background: rgba(255, 255, 255, 0.025);
}

.partner-section h3 {
  margin: 0;
  color: #f2f7ff;
}

.partner-sector-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.partner-sector-button {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(171, 199, 235, 0.16);
  color: #d7e8ff;
  padding: 10px 16px;
  box-shadow: none;
}

.partner-sector-button.active {
  background: linear-gradient(180deg, rgba(57, 126, 220, 0.95), rgba(30, 84, 165, 0.96));
  border-color: rgba(171, 199, 235, 0.3);
}

.partner-sector-table {
  width: 100%;
  margin: 0;
}

.partner-sector-table td,
.partner-sector-table th {
  vertical-align: middle;
  border: 1px solid rgba(171, 199, 235, 0.16);
  padding: 10px;
}

.partner-sector-table th {
  background: rgba(255, 255, 255, 0.05);
  color: #eff6ff;
}

.partner-sector-table td {
  color: rgba(220, 230, 244, 0.8);
}

.partner-risk-controls {
  justify-items: center;
  text-align: center;
}

.partner-risk-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
}

.partner-risk-row label {
  display: grid;
  gap: 6px;
  min-width: 220px;
  color: rgba(220, 230, 244, 0.8);
}

.partner-risk-result {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  justify-content: center;
  color: rgba(220, 230, 244, 0.86);
}

.partner-risk-pill {
  border-radius: 999px;
  color: #fff;
  display: inline-flex;
  font-weight: 700;
  padding: 4px 10px;
}

.partner-matrix-wrap {
  overflow-x: auto;
}

.partner-matrix-layout {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.partner-matrix-table {
  min-width: 760px;
}

.partner-matrix-table td,
.partner-matrix-table th {
  min-width: 96px;
}

.partner-legend {
  border: 1px solid rgba(171, 199, 235, 0.16);
  border-radius: 14px;
  overflow: hidden;
  min-width: 160px;
}

.partner-legend-title,
.partner-legend-item {
  padding: 8px 10px;
  text-align: center;
}

.partner-legend-title {
  background: rgba(255, 255, 255, 0.05);
  color: #eff6ff;
  font-weight: 700;
}

@media (max-width: 900px) {
  .partner-sector-table {
    width: 100%;
  }

  .partner-matrix-layout {
    flex-direction: column;
  }
}
</style>
