<script setup lang="ts">
import { reactive } from 'vue'

type RiskLevel = 'Little to None' | 'Minor' | 'Moderate' | 'Major' | 'Extreme'

const riskLevels: { label: RiskLevel; color: string; text: string }[] = [
  { label: 'Little to None', color: '#a8e6a1', text: '#102316' },
  { label: 'Minor', color: '#ffe564', text: '#111827' },
  { label: 'Moderate', color: '#ff9838', text: '#111827' },
  { label: 'Major', color: '#e84f4f', text: '#ffffff' },
  { label: 'Extreme', color: '#a027d7', text: '#ffffff' },
]

const sectors = ['Electric Power', 'HF Communications', 'GNSS', 'Satellite Operations', 'Aviation', 'Aurora']
const days = ['Day 1\nApr 13 (Mon)', 'Day 2\nApr 14 (Tue)', 'Day 3\nApr 15 (Wed)']

const briefing = reactive({
  dateTime: 'Apr 13, 2026 1200 UTC',
  headline: 'Elevated Geomagnetic Activity Possible Late Thursday into Friday',
  summary:
    'A high-speed solar wind stream from a coronal hole is expected to reach Earth late Thursday into Friday. This may lead to elevated geomagnetic activity, with G1-G2 (Minor to Moderate) storm levels possible, primarily on Friday. Conditions are expected to improve by Saturday. No significant solar flares are anticipated.',
  keyPoints:
    'A high-speed solar wind stream is expected to reach Earth late Thursday into Friday.\nG1-G2 (Minor to Moderate) geomagnetic storm levels are possible, mainly on Friday.\nConfidence is moderate in the timing; low to moderate in the magnitude.\nSectors of interest: electric power, HF communications, GNSS, satellite operations, aviation, and aurora observers at higher latitudes.\nConditions are expected to calm by Saturday.',
  activeProducts:
    'Geomagnetic Storm Watch: 14 Apr 0000 UTC - 15 Apr 2359 UTC\nSpace Weather Summary: In Effect\nRadiation Storm Warning: None',
  impacts:
    'Periods of voltage control issues and false alarms on the power grid.\nDegraded HF radio communications at higher latitudes, especially on polar routes.\nIncreased range error in GNSS positioning at higher latitudes.\nIncreased drag on low Earth orbit satellites may require maneuvering.\nAurora may be visible at higher latitudes in the Northern Hemisphere on Friday night.',
  watchNext:
    'Monitor updates for changes to timing and geomagnetic storm levels.\nCheck for additional watches or warnings as conditions evolve.\nFollow SWPC social media and website for the latest information.',
  info:
    'For the latest forecasts, alerts, and space weather information, visit www.swpc.noaa.gov.\nQuestions or to report impacts, contact SWPC at swpc.answers@noaa.gov or (303) 497-0016.\nYou are receiving this email because you are a valued space weather partner.',
  riskOutlook: Object.fromEntries(
    sectors.map((sector) => [
      sector,
      sector === 'Aurora'
        ? ['Little to None', 'Minor', 'Moderate']
        : sector === 'Aviation'
          ? ['Little to None', 'Little to None', 'Minor']
          : sector === 'Satellite Operations'
            ? ['Little to None', 'Minor', 'Minor']
            : ['Little to None', 'Minor', 'Moderate'],
    ]),
  ) as Record<string, RiskLevel[]>,
})

function lines(value: string): string[] {
  return value
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
}

function riskStyle(level: RiskLevel) {
  const risk = riskLevels.find((item) => item.label === level) ?? riskLevels[0]!
  return {
    backgroundColor: risk.color,
    color: risk.text,
  }
}

function riskLevelFor(sector: string, index: number): RiskLevel {
  return briefing.riskOutlook[sector]?.[index] ?? 'Little to None'
}

function handleRiskChange(sector: string, index: number, event: Event) {
  const target = event.target as HTMLSelectElement | null
  if (!target) {
    return
  }
  const value = target.value as RiskLevel
  const sectorRisk = briefing.riskOutlook[sector]
  if (!sectorRisk) {
    return
  }
  sectorRisk[index] = value
}
</script>

<template>
  <section class="partner-email-briefing">
    <div class="partner-proposal-banner">
      Proposal for Partner Briefing to be single source of communication from Space Weather Forecast Office
      to External Partners including SWPC Staff and Core Partners (i.e. SRAG, ICAO).
    </div>

    <div class="partner-email-layout">
      <aside class="partner-email-editor" aria-label="Forecaster briefing inputs">
        <section class="partner-email-input-section">
          <div class="partner-email-editor-heading">Briefing Header</div>
          <label>
            Issue Time
            <input v-model="briefing.dateTime" type="text" />
          </label>

          <label>
            Headline
            <input v-model="briefing.headline" type="text" />
          </label>

          <label>
            Summary
            <textarea v-model="briefing.summary" />
          </label>
        </section>

        <section class="partner-email-input-section">
          <div class="partner-email-editor-heading">Briefing Body</div>
          <label>
            Key Points
            <textarea v-model="briefing.keyPoints" />
          </label>

          <label>
            Active Products
            <textarea v-model="briefing.activeProducts" />
          </label>

          <label>
            Potential Impacts
            <textarea v-model="briefing.impacts" />
          </label>

          <label>
            What To Watch Next
            <textarea v-model="briefing.watchNext" />
          </label>
        </section>

        <section class="partner-email-input-section partner-email-risk-editor">
          <div class="partner-email-editor-heading">Risk Outlook</div>
          <div class="partner-email-risk-grid">
            <div class="partner-email-risk-head">Sector</div>
            <div v-for="day in days" :key="day" class="partner-email-risk-head">
              {{ day.split('\n')[0] }}
            </div>
            <template v-for="sector in sectors" :key="sector">
              <div class="partner-email-risk-sector">{{ sector }}</div>
              <select
                v-for="(_, index) in days"
                :key="`${sector}-editor-${index}`"
                :value="riskLevelFor(sector, index)"
                @change="handleRiskChange(sector, index, $event)"
              >
                <option v-for="risk in riskLevels" :key="risk.label" :value="risk.label">
                  {{ risk.label }}
                </option>
              </select>
            </template>
          </div>
        </section>
      </aside>

      <article class="partner-pdf-preview" aria-label="Partner briefing PDF preview">
        <header class="partner-pdf-masthead">
          <div class="partner-pdf-brand">
            <img src="/assets/visual-finder/logos/noaa-emblem-rgb-withspace-2022.png" alt="NOAA" />
            <img src="/assets/visual-finder/logos/NWSlogo.png" alt="National Weather Service" />
            <div>
              <div>NOAA / National Weather Service</div>
              <strong>Space Weather Prediction Center</strong>
              <span>National Oceanic and Atmospheric Administration</span>
            </div>
          </div>
          <div class="partner-pdf-meta">
            <strong>Partner Briefing</strong>
            <span>{{ briefing.dateTime }}</span>
          </div>
        </header>

        <section class="partner-pdf-title">
          <h2>Space Weather Partner Briefing</h2>
          <h3>{{ briefing.headline }}</h3>
          <p>{{ briefing.summary }}</p>
        </section>

        <section class="partner-pdf-section">
          <h4>Key Points</h4>
          <ul>
            <li v-for="item in lines(briefing.keyPoints)" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section class="partner-pdf-section">
          <h4>Space Weather Risk Outlook</h4>
          <table class="partner-pdf-risk-table">
            <thead>
              <tr>
                <th>Sector</th>
                <th v-for="day in days" :key="day">
                  <span v-for="line in day.split('\n')" :key="line">{{ line }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sector in sectors" :key="sector">
                <th>{{ sector }}</th>
                <td
                  v-for="(_, index) in days"
                  :key="`${sector}-${index}`"
                  :style="riskStyle(riskLevelFor(sector, index))"
                >
                  {{ riskLevelFor(sector, index) }}
                </td>
              </tr>
            </tbody>
          </table>

          <div class="partner-pdf-legend">
            <strong>Risk Levels:</strong>
            <span v-for="risk in riskLevels" :key="risk.label" :style="{ backgroundColor: risk.color, color: risk.text }">
              {{ risk.label }}
            </span>
          </div>
        </section>

        <section class="partner-pdf-section">
          <h4>Active Products</h4>
          <ul>
            <li v-for="item in lines(briefing.activeProducts)" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section class="partner-pdf-section">
          <h4>Potential Impacts</h4>
          <ul>
            <li v-for="item in lines(briefing.impacts)" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section class="partner-pdf-section">
          <h4>What To Watch Next</h4>
          <ul>
            <li v-for="item in lines(briefing.watchNext)" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section class="partner-pdf-section partner-pdf-info">
          <h4>For More Information</h4>
          <p v-for="item in lines(briefing.info)" :key="item">{{ item }}</p>
        </section>
      </article>
    </div>
  </section>
</template>

<style scoped>
.partner-email-briefing {
  display: grid;
  gap: 14px;
}

.partner-proposal-banner {
  border: 1px solid rgba(95, 199, 255, 0.32);
  border-radius: var(--app-radius);
  background: rgba(95, 199, 255, 0.1);
  color: #dcefff;
  font-weight: 700;
  line-height: 1.35;
  padding: 12px 14px;
}

.partner-email-layout {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(460px, 2fr);
  gap: 16px;
  align-items: start;
}

.partner-email-editor {
  display: grid;
  gap: 12px;
}

.partner-email-input-section {
  display: grid;
  gap: 12px;
  padding: 14px;
  border: 1px solid rgba(255, 232, 100, 0.46);
  border-radius: var(--app-radius);
  background:
    linear-gradient(180deg, rgba(255, 232, 100, 0.055), rgba(255, 232, 100, 0.025)),
    rgba(4, 10, 18, 0.28);
}

.partner-email-editor label {
  display: grid;
  gap: 6px;
  color: rgba(232, 239, 248, 0.78);
  font-weight: 700;
}

.partner-email-editor input,
.partner-email-editor textarea,
.partner-email-editor select {
  background: rgba(2, 8, 15, 0.96);
  color: #e8eff8;
  font-weight: 400;
}

.partner-email-editor textarea {
  min-height: 96px;
}

.partner-email-editor-heading {
  color: #ffe864;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.partner-email-risk-editor {
  display: grid;
  gap: 8px;
}

.partner-email-risk-grid {
  display: grid;
  grid-template-columns: minmax(130px, 1fr) repeat(3, minmax(96px, 0.75fr));
  gap: 6px;
  align-items: center;
}

.partner-email-risk-head,
.partner-email-risk-sector {
  color: rgba(232, 239, 248, 0.78);
  font-size: 0.78rem;
  font-weight: 700;
}

.partner-pdf-preview {
  width: min(100%, 860px);
  justify-self: center;
  padding: 24px 42px 28px;
  background: #ffffff;
  color: #111827;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 14px;
  line-height: 1.28;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.34);
}

.partner-pdf-masthead {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  margin-bottom: 22px;
  padding: 14px 18px;
  background: linear-gradient(90deg, #003f86, #002d62);
  color: #ffffff;
}

.partner-pdf-brand {
  display: flex;
  gap: 10px;
  align-items: center;
  text-transform: uppercase;
}

.partner-pdf-brand img {
  width: 52px;
  height: 52px;
  object-fit: contain;
  background: #ffffff;
  border-radius: 999px;
}

.partner-pdf-brand div {
  display: grid;
  line-height: 1.05;
}

.partner-pdf-brand strong {
  font-size: 18px;
}

.partner-pdf-brand span,
.partner-pdf-brand div > div {
  font-size: 11px;
}

.partner-pdf-meta {
  display: grid;
  gap: 4px;
  text-align: right;
  white-space: nowrap;
}

.partner-pdf-meta strong {
  font-size: 18px;
  font-weight: 500;
}

.partner-pdf-title {
  display: grid;
  gap: 8px;
  text-align: center;
}

.partner-pdf-title h2 {
  margin: 0;
  color: #003f86;
  font-size: 26px;
}

.partner-pdf-title h3 {
  margin: 0;
  color: #0052b5;
  font-size: 17px;
}

.partner-pdf-title p {
  margin: 8px auto 0;
  max-width: 720px;
  text-align: left;
}

.partner-pdf-section {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #cfd8e3;
}

.partner-pdf-section h4 {
  margin: 0 0 6px;
  color: #0052b5;
  font-size: 17px;
  text-transform: uppercase;
}

.partner-pdf-section ul {
  margin: 0;
  padding-left: 24px;
}

.partner-pdf-risk-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
}

.partner-pdf-risk-table th,
.partner-pdf-risk-table td {
  border: 3px solid #ffffff;
  padding: 8px;
}

.partner-pdf-risk-table thead th,
.partner-pdf-risk-table tbody th {
  background: #e5e7eb;
  color: #111827;
  font-weight: 700;
}

.partner-pdf-risk-table thead span {
  display: block;
}

.partner-pdf-risk-table td {
  font-weight: 700;
}

.partner-pdf-legend {
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
  margin-top: 12px;
  font-size: 12px;
  font-weight: 700;
}

.partner-pdf-legend span {
  min-width: 112px;
  padding: 7px 10px;
  text-align: center;
}

.partner-pdf-info p {
  margin: 2px 0;
}

@media (max-width: 1300px) {
  .partner-email-layout {
    grid-template-columns: 1fr;
  }

  .partner-pdf-preview {
    justify-self: stretch;
  }
}
</style>
