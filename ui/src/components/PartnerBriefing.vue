<script setup lang="ts">
import { computed, ref } from 'vue'

import type { PartnerImpactLevel, PartnerSector } from '../types'

const likelihoodOptions = [
  { value: 1, label: 'Extremely Unlikely' },
  { value: 2, label: 'Unlikely' },
  { value: 3, label: 'As Likely as Not' },
  { value: 4, label: 'Likely' },
  { value: 5, label: 'Very Likely' },
]

const impactOptions = [
  { value: 1, label: 'Little / None' },
  { value: 2, label: 'Minor' },
  { value: 3, label: 'Moderate' },
  { value: 4, label: 'High' },
  { value: 5, label: 'Extreme' },
]

const riskLabels = ['Little to None', 'Minor', 'Moderate', 'High', 'Extreme']
const riskColors = ['#00A878', '#FFE864', '#FF8C42', '#E84F4F', '#C12AFF']
const sectorLevelTints = [
  '#07584c',
  '#6b6b3f',
  '#764832',
  '#73313e',
  '#62238a',
]
const impactLevelIds = ['1', '2', '3', '4', '5']

function level(
  label: string,
  thresholdIndicators: string,
  impact: string,
  action: string,
  confidence: string,
): PartnerImpactLevel {
  return { label, thresholdIndicators, impact, action, confidence }
}

const sectors: PartnerSector[] = [
  {
    name: 'Power Grid',
    description: 'Use for bulk-power, transmission, regional reliability, and utility-facing GMD IDSS. Kp/G-scale remains context; primary hazard logic is regional geoelectric field, local dB/dt, and measured or modeled GIC response.',
    hazardFamilies: ['Geomagnetic storm', 'Geoelectric field', 'GIC response'],
    keyIndicators: ['Regional E-field V/km', 'Local dB/dt', 'Measured/modeled GIC', 'Regional K/Hpo', 'Ground conductivity', 'Grid topology'],
    confidenceNote: 'Use scale values as context, then evaluate regional or local exposure, sector indicators, and confidence before generating an IDSS action statement.',
    impactLevels: {
      '1': level('Routine', 'E-field <0.05 V/km; dB/dt below local monitoring threshold, e.g., <20 nT/min prototype; measured/modelled GIC <10% of operator action threshold; Kp <5 / no G-level context.', 'No material operational impact expected. Routine GMD awareness only.', 'Continue normal monitoring. Keep geoelectric field, magnetometer, and GIC feeds visible for trend detection.', 'High confidence only where local magnetometer/E-field/GIC data are available.'),
      '2': level('Awareness', 'E-field 0.05-0.20 V/km; dB/dt rising or 20-40 nT/min prototype; GIC 10-25% of action threshold or weak response in susceptible assets; G1-G2 context possible.', 'Weak or localized GIC possible, especially in high-latitude, high-resistivity, long-line, or transformer-sensitive portions of the footprint.', 'Notify interested partners if trend increases. Verify data quality and watch local E-field/dB/dt/GIC, not Kp alone.', 'Use regional/utility thresholds where provided.'),
      '3': level('Elevated', 'E-field 0.20-1.0 V/km; dB/dt above monitoring threshold or 40-80 nT/min prototype; GIC 25-50% of action threshold or rapidly increasing; G2-G3 context.', 'Enhanced monitoring warranted. Localized alarms, transformer neutral current, VAR demand changes, or voltage-control concerns are plausible in susceptible systems.', 'Brief grid partners. Review current outages, maintenance, reactive reserve, and GMD operating procedure readiness.', 'Impact depends strongly on ground conductivity and actual grid posture.'),
      '4': level('High', 'E-field 1-5 V/km; dB/dt at/above operating threshold or 80-120 nT/min prototype; GIC 50-100% of action threshold; G3-G5/Hpo context.', 'Operational mitigation may be needed in affected regions. Regional voltage/reactive-power management and outage/maintenance posture may become relevant.', 'Coordinate with RC/BA/TOP partners. Review reactive reserve, defer vulnerable maintenance where appropriate, and prepare approved GMD procedures.', 'Do not infer impact from global G-scale alone.'),
      '5': level('Severe / Extreme', 'E-field >5 V/km, especially near or above the 8 V/km NERC reference level; dB/dt >120 nT/min prototype or extreme local derivative; measured/modelled GIC exceeds operator action threshold; G5/Hpo high-end context.', 'Emergency GMD posture possible. Reliability impacts are possible in susceptible systems; restoration and emergency-management coordination may be needed.', 'Execute approved GMD operating plan. Recall assets from outage where feasible, reconfigure to reduce GIC if procedurally allowed, coordinate restoration and emergency-management briefings.', 'Separate severe G5 from Carrington-class language unless supporting indicators justify it.'),
    },
  },
  {
    name: 'Aviation Operations',
    description: 'Use for dispatch, ATC coordination, polar-route planning, long-haul operations, alternate communications, reroute/fuel planning, and operational continuity.',
    hazardFamilies: ['Geomagnetic storm', 'Solar radiation storm', 'HF absorption', 'SATCOM/GNSS disruption'],
    keyIndicators: ['Route geometry', 'Geomagnetic latitude', 'Altitude', 'HF/D-RAP absorption', 'SATCOM availability', 'GNSS service quality', 'G/S/R context'],
    confidenceNote: 'Keep this separate from aviation radiation dose so communications/navigation decisions are not confused with dose decisions.',
    impactLevels: {
      '1': level('Routine', 'No route-relevant HF absorption; R0; S0; G0-G1; SATCOM and GNSS nominal; no polar cap absorption along planned route.', 'Normal operations. Space weather does not require operational planning changes.', 'Display routine monitoring state. No special aviation IDSS action.', 'Route-specific view is essential; global scale levels alone are insufficient.'),
      '2': level('Awareness', 'G1-G2, S1-S2, or R1-R2 possible or occurring near route; weak HF absorption on sunlit side; weak polar absorption; high-latitude/polar route exposure exists but backup comms remain available.', 'Minor comms or navigation degradation possible. Operators may need increased awareness for polar or high-latitude routes.', 'Prompt dispatch/operations to monitor route-specific HF, SATCOM, GNSS, and radiation products. Confer with provider if G2/S2 or higher is expected.', 'STPI found some airlines confer with providers at G2/S2 and above, but procedures vary by company.'),
      '3': level('Elevated', 'G3, S3, or R3; moderate D-RAP/HF absorption affecting planned routing; SATCOM availability uncertain in polar region; GNSS degradation reports; proton/PCA indicators affecting high latitudes.', 'Route, altitude, or communications contingency may be needed. HF reliability may be reduced; SATCOM/GNSS availability should be checked.', 'Consider rerouting for SATCOM coverage, added fuel reserve for lower-altitude flight, alternate HF frequencies, and coordination with long-distance operational control/ANSPs.', 'Impact depends on planned route, aircraft equipage, time of day, and comms architecture.'),
      '4': level('High', 'G4, S4, or R4; strong HF absorption or polar cap absorption along route; SATCOM gap likely; GNSS integrity or timing effects plausible; radiation product approaching action threshold.', 'Major operational mitigation may be required for affected routes. Polar operations may require lower altitude, reroute, delay, or alternate communications.', 'Plan lower altitude or avoid vulnerable routes where procedures call for it. Coordinate dispatch, ATC/ANSP, provider, and management decision points.', 'Separate comms/navigation impacts from dose impacts.'),
      '5': level('Severe / Extreme', 'G5, S5, or R5; persistent route-relevant HF blackout/PCA; SATCOM/GNSS alternatives degraded; route-specific radiation product at high/action level; limited reliable communications over planned segment.', 'Operations on affected polar/high-latitude routes may be unacceptable without mitigation. Sustained reroute, descent, delay, or route avoidance may be needed.', 'Execute aviation space weather procedures. Actively reroute/descent/avoid affected region as required; brief crews and operational control; maintain contingency communications.', 'Avoid implying all global aviation is affected; scope to routes and equipage.'),
    },
  },
  {
    name: 'Aviation Radiation Dose',
    description: 'Use only for human radiation exposure at aviation altitudes; do not use the NOAA S-scale alone as a dose proxy.',
    hazardFamilies: ['Solar radiation storm', 'Dose-rate / D-index', 'Hard-spectrum proton event'],
    keyIndicators: ['Route-altitude dose rate', 'Flight-specific accumulated dose', '>=500 MeV protons', 'GLE/neutron monitor response', 'Geomagnetic cutoff rigidity'],
    confidenceNote: 'Dose assessment depends on route, altitude, latitude, duration, particle spectrum, and forecast confidence.',
    impactLevels: {
      '1': level('Routine', 'D0: additional solar dose rate <5 uSv/h at route altitude/FL410 proxy; no GLE; no significant >=500 MeV proton enhancement; S-scale may be nonzero but dose product is quiet.', 'No aviation-dose action expected beyond routine radiation awareness.', 'Display dose product and route exposure. No reroute/altitude action for dose.', 'Use D-index/dose product as primary; S-scale is context only.'),
      '2': level('Awareness', 'D1-D2: 5-20 uSv/h additional solar dose rate; weak hard-spectrum or neutron-monitor indication; high-latitude/high-altitude route exposure.', 'Additional dose is elevated but likely manageable through monitoring and flight-specific assessment.', 'Monitor route-specific dose, update dispatch/crew advisories if required, and prepare mitigation options for polar/high-altitude operations.', 'Thresholds should be tied to airline, regulator, and radiation-protection procedures.'),
      '3': level('Elevated', 'D3-D4: 20-80 uSv/h; FAA-style 20 uSv/h alert concept may be met if sustained; >=500 MeV/GLE indicators support hard spectrum; flight-specific dose could become operationally relevant.', 'Operational concern for crew/passenger dose management on exposed routes. Altitude, latitude, and duration matter.', 'Run flight-specific dose assessment. Consider lower altitude, latitude change, route adjustment, or advisory products based on operator procedures.', 'This is the first level where dose-oriented IDSS should become prominent.'),
      '4': level('High', 'D5-D6: 80-320 uSv/h; strong hard-spectrum event; significant GLE/neutron monitor response; affected high-latitude/high-altitude routes.', 'Substantial additional dose possible for exposed flights. Mitigation may be warranted before or during flight.', 'Recommend route/altitude mitigation assessment. Coordinate operational control, radiation safety, provider, and management decision points.', 'Do not use S4 alone as the trigger; require dose or hard-spectrum confirmation.'),
      '5': level('Severe / Extreme', 'D7 or higher: >320 uSv/h; extreme hard-spectrum/GLE conditions; flight-specific dose potentially high over affected route segment.', 'Severe radiation-dose environment for exposed aviation routes. Avoidance or major mitigation may be needed.', 'Execute radiation-dose procedures: avoid affected high-altitude/high-latitude exposure, descend/reroute/delay as required, and document flight-specific dose.', 'Communicate clearly to avoid broad public alarm outside affected routes.'),
    },
  },
  {
    name: 'HF Communications',
    description: 'Use for HF skywave communications, including aviation, maritime, amateur radio, emergency backup HF, and polar HF.',
    hazardFamilies: ['X-ray HF absorption', 'D-RAP absorption', 'Polar cap absorption'],
    keyIndicators: ['GOES x-ray class/R-scale', 'D-RAP absorption', 'Sunlit-side footprint', 'Frequency band', 'Circuit geometry', 'S-scale/proton context'],
    confidenceNote: 'Label as HF Communications or X-ray HF Absorption rather than generic Radio Blackout.',
    impactLevels: {
      '1': level('Routine', 'R0; x-ray below M1; D-RAP absorption minimal; no polar cap absorption on affected circuits.', 'HF propagation may vary normally, but no event-driven blackout expected.', 'Routine monitoring. Display sunlit-side and polar-route maps when available.', 'HF impacts are strongly frequency-, path-, and daylight-dependent.'),
      '2': level('Minor', 'R1 / M1-class threshold or weak D-RAP absorption; brief dayside degradation possible; weak PCA possible on high-latitude paths.', 'Weak or minor HF degradation on sunlit-side paths. Occasional loss of contact possible on vulnerable circuits.', 'Advise alternate frequencies and monitor absorption maps. Flag affected daylight hemisphere/path segments.', 'R-scale does not represent all radio frequencies.'),
      '3': level('Moderate', 'R2 / M5 threshold or moderate D-RAP absorption; limited blackout/fadeout on sunlit side; PCA may affect polar HF paths.', 'Moderate HF degradation. Some circuits may require frequency changes, alternate routing, or backup comms.', 'Issue sector-specific HF advisory. Recommend alternate frequencies/paths and backup comms check for affected operations.', 'Polar proton absorption can persist day/night, unlike x-ray dayside absorption.'),
      '4': level('High', 'R3 / X1 threshold or strong D-RAP absorption; significant dayside HF blackout for parts of the spectrum; S3+ proton/PCA context on polar paths.', 'Major HF disruption likely for affected paths. Operational users may lose reliable HF on selected circuits.', 'Activate backup communications. Coordinate with aviation/maritime/emergency users whose routes/AOR intersect the absorption region.', 'Tie alert to actual AOR, not just global R number.'),
      '5': level('Severe / Extreme', 'R4-R5 / X10 to X20+ or severe D-RAP absorption; prolonged or widespread dayside blackout; strong PCA affecting polar regions.', 'HF may be unusable for affected circuits. Critical operations relying on HF need non-HF alternatives.', 'Execute HF contingency procedures. Provide map-based timing, region, frequencies affected, and expected recovery updates.', 'Include restoration/recovery timing and confidence; avoid all-frequency "radio blackout" wording.'),
    },
  },
  {
    name: 'Satellites / Spacecraft',
    description: 'Use for satellite owner/operators across LEO, MEO, GEO, HEO, and deep-space missions; support anomaly attribution and operational posture.',
    hazardFamilies: ['Energetic particles', 'Charging', 'Geomagnetic storm', 'Neutral density / drag'],
    keyIndicators: ['S-scale >=10 MeV protons', '>50/>100/>500 MeV protons', 'Energetic electrons', 'G/Hpo context', 'Neutral density/drag', 'Anomaly reports'],
    confidenceNote: 'Avoid implying a one-size-fits-all satellite impact; thresholds vary by orbit, shielding, mission design, and mode.',
    impactLevels: {
      '1': level('Routine', 'S0; G0-G1; neutral density/drag near baseline, e.g., <10% prototype increase; energetic electron/proton levels below mission watch thresholds.', 'Routine spacecraft operations. No event-driven anomaly risk above normal background.', 'Normal monitoring and anomaly attribution logging.', 'Mission thresholds vary by orbit, shielding, design, and mode.'),
      '2': level('Awareness', 'S1 or G2; neutral density +10-25% prototype for LEO; elevated >10 MeV protons or charging environment below action threshold; electron flux rising.', 'Minor anomaly risk or drag awareness. Vulnerable payloads/components may need closer monitoring.', 'Increase environment monitoring. Flag sensitive maneuvers, uploads, imaging, or star-tracker operations for awareness.', 'For GEO, charging/electrons may dominate; for LEO, drag/density may dominate.'),
      '3': level('Elevated', 'S2-S3 or G3; elevated >50/>100 MeV proton channels; neutral density +25-50% prototype; charging indicators at/near mission watch threshold; LEO drag prediction errors increasing.', 'Anomaly risk elevated. SEUs, star tracker issues, charging, degraded imaging, or orbit prediction errors are plausible.', 'Brief spacecraft ops. Review safe-mode criteria, maneuver plans, payload schedules, conjunction screening, and anomaly attribution notes.', 'S-scale alone is insufficient; use mission environment channels.'),
      '4': level('High', 'S4 or G4; high >100 MeV proton channel or mission radiation threshold; neutral density +50-100% prototype; significant charging/radiation/drag conditions; anomaly reports emerging.', 'Significant operational risk for susceptible spacecraft. Attitude control, tracking, imaging, solar array, or command/telemetry impacts may require mitigation.', 'Consider delaying vulnerable operations, modifying payload activities, increasing tracking cadence, and coordinating SDA/conjunction assessment.', 'Thresholds should be configurable by mission class and orbit.'),
      '5': level('Severe / Extreme', 'S5 or G5/Hpo high-end; severe proton/electron environment; neutral density >100% prototype; major tracking/orbit-prediction degradation; multiple anomaly reports.', 'Severe environment for vulnerable assets. Loss of function, major drag/orbit uncertainty, or fleet-wide anomaly management possible.', 'Execute spacecraft storm procedures. Prioritize asset protection, tracking recovery, conjunction-risk reassessment, and executive/partner briefings.', 'Separate environmental severity from guaranteed spacecraft failure.'),
    },
  },
  {
    name: 'GNSS / Navigation / Timing',
    description: 'Use for GNSS positioning, timing, integrity, augmentation, RTK/PPP, aviation navigation support, critical infrastructure timing, and radio-navigation users.',
    hazardFamilies: ['Scintillation', 'TEC disturbance', 'Solar radio burst', 'Geomagnetic storm context'],
    keyIndicators: ['S4 and sigma-phi', 'TEC/TEC gradients/ROTI', 'Loss-of-lock/cycle slips', 'SBAS/GBAS/RTK/PPP quality', 'Solar radio burst reports'],
    confidenceNote: 'Emphasize ionospheric conditions and receiver/service quality, not R-scale alone.',
    impactLevels: {
      '1': level('Routine', 'No regional scintillation product alert; S4 <0.3 prototype; sigma-phi below receiver concern; TEC gradients/ROTI normal; correction services nominal; no solar radio burst affecting GNSS bands.', 'GNSS accuracy, integrity, and timing expected to be normal.', 'Routine monitoring. Display regional ionosphere and service-quality indicators.', 'Use actual service-quality telemetry where available.'),
      '2': level('Awareness', 'Weak scintillation: S4 about 0.3-0.4 prototype or T1-T2; TEC gradients rising; G1-G2 context; occasional cycle slips or degraded precision reports.', 'Minor accuracy/confidence degradation possible for precision or single-frequency users.', 'Notify precision/timing users to monitor residuals, fix status, correction age, and timing holdover readiness.', 'Thresholds should be tuned to application: RTK, aviation integrity, timing, or public navigation.'),
      '3': level('Elevated', 'Moderate scintillation: S4 0.4-0.6 prototype or T3; sigma-phi elevated; TEC gradients disrupting corrections; G2-G3 context; regional loss-of-lock reports or correction-service degradation.', 'GNSS precision and timing may be degraded. RTK/PPP initialization delays, integrity alarms, or timing quality reductions are plausible.', 'Brief GNSS/timing partners. Recommend alternate timing sources, quality-control checks, and operational caution for precision tasks.', 'R-scale/x-ray flares are not the main GNSS ionosphere indicator; include solar radio burst separately.'),
      '4': level('High', 'Strong scintillation: S4 >=0.6 prototype or T4; frequent cycle slips/loss of lock; severe TEC gradients; G4 context; augmentation/correction services degraded; solar radio burst affecting GNSS receiver bands.', 'Wide-area or regional degradation possible. Precision positioning and timing services may become unreliable in affected areas.', 'Activate alternate navigation/timing plans. Advise postponing precision-dependent operations where tolerances cannot be maintained.', 'Map the affected region/local time; equatorial and auroral regions differ.'),
      '5': level('Severe / Extreme', 'Severe/widespread scintillation or T5; persistent loss of lock; correction services unusable; timing users losing primary source; severe solar radio burst interference; G5/Hpo high context.', 'GNSS-dependent mission operations may be compromised in affected regions. Timing, navigation, and precision positioning may require full fallback.', 'Execute GNSS contingency procedures. Switch to backup timing/nav, suspend precision operations, and provide recovery timing updates.', 'Avoid global outage language unless telemetry supports it.'),
    },
  },
  {
    name: 'Pipelines',
    description: 'Use for long conductive pipeline systems and cathodic-protection programs.',
    hazardFamilies: ['Geomagnetic storm', 'Geoelectric field', 'Induced pipeline current'],
    keyIndicators: ['E-field V/km', 'Local dB/dt', 'Pipe orientation/length', 'Ground conductivity', 'CP system state', 'Pipe-to-soil potential excursions'],
    confidenceNote: 'Operational consequence is cathodic-protection disturbance and corrosion-risk management, not voltage stability.',
    impactLevels: {
      '1': level('Routine', 'E-field <0.05 V/km; dB/dt below local monitoring threshold; CP readings normal; no measured pipeline current anomaly.', 'No event-driven CP impact expected.', 'Routine monitoring. No special pipeline IDSS action.', 'Pipeline response is highly asset-specific.'),
      '2': level('Awareness', 'E-field 0.05-0.20 V/km; dB/dt rising; weak CP noise or small pipe-to-soil potential excursions in susceptible regions.', 'Minor CP disturbance possible on long exposed segments.', 'Monitor CP telemetry and geoelectric field trends. Flag susceptible long pipelines and high-resistivity ground regions.', 'Use operator thresholds for CP compliance and integrity decisions.'),
      '3': level('Elevated', 'E-field 0.20-1.0 V/km; dB/dt above monitoring threshold; sustained CP excursions or modeled induced current in exposed segments.', 'Localized CP anomalies may require closer monitoring and post-event review.', 'Brief pipeline/integrity partners. Increase monitoring cadence and document CP deviations during event.', 'Do not map directly from Kp to CP impact.'),
      '4': level('High', 'E-field 1-5 V/km; dB/dt at operating threshold; significant CP excursions across multiple segments; high-risk orientation relative to E-field.', 'Widespread CP disturbance possible in exposed networks. Corrosion-risk management posture may be affected.', 'Coordinate with pipeline operators. Prioritize monitoring, defer sensitive CP surveys if needed, and plan post-event integrity review.', 'Geographic conductivity and asset orientation dominate risk.'),
      '5': level('Severe / Extreme', 'E-field >5 V/km, especially near/exceeding 8 V/km reference environment; severe dB/dt; major CP excursions or pipeline current above operator action threshold.', 'Severe induced-current environment. CP control and corrosion-risk management may require active response and post-event investigation.', 'Execute pipeline GMD procedures. Maintain safety/integrity monitoring and coordinate with emergency/grid partners where dependencies exist.', 'Use measured CP/current data where available.'),
    },
  },
  {
    name: 'Human Spaceflight',
    description: 'Use for crewed spacecraft, EVA planning, lunar/deep-space trajectories, and mission operations.',
    hazardFamilies: ['Solar energetic particles', 'Dose-rate product', 'Mission radiation rules'],
    keyIndicators: ['>30-50 MeV protons', '>100 MeV/hard-spectrum indicators', 'Onboard dosimeters', 'Modeled shielded dose', 'EVA/suit exposure'],
    confidenceNote: 'Tie to program flight rules and dosimetry, not generic public S-scale wording.',
    impactLevels: {
      '1': level('Routine', 'No SEP concern; >30-50 MeV proton channels quiet; onboard/model dose rates normal; no EVA/timeline sensitivity.', 'Normal mission timeline and EVA planning.', 'Routine radiation monitoring. No special crew action.', 'Program-specific dose limits and flight rules control decisions.'),
      '2': level('Awareness', 'S1 or rising SEP watch; weak >30 MeV channel increase; dose below program watch threshold; EVA/thin-shielded activity possible within forecast window.', 'Dose environment requires attention but no immediate crew action expected.', 'Increase radiation monitoring. Review EVA/timeline exposure and storm-shelter readiness.', 'S-scale is context; crew dose depends on energy spectrum and shielding.'),
      '3': level('Elevated', 'S2-S3 or significant >30-50 MeV proton flux; modeled/onboard dose approaching program watch threshold; EVA or lightly shielded activity scheduled.', 'Crewed operations may need timeline review. EVA deferral or additional shielding posture may be considered.', 'Brief flight control and radiation safety. Reassess EVA, trajectory exposure, and shelter timelines.', 'STPI notes astronauts can receive increased dose from 30-50 MeV protons in thin shielding.'),
      '4': level('High', 'S4 or strong >30-100 MeV event; dose rate reaches program action threshold; hard spectrum or GLE indication; EVA in progress or planned.', 'Active mitigation may be required. EVA restrictions, termination, or shelter posture may be needed.', 'Execute flight-rule-driven actions: delay/terminate EVA, move crew to better shielded area, update mission timeline.', 'Use real-time dosimetry when available.'),
      '5': level('Severe / Extreme', 'S5 or extreme hard-spectrum SEP/GLE; high onboard/model dose; shelter thresholds exceeded or likely; limited geomagnetic shielding/mission-critical exposure.', 'Crew health-critical radiation posture possible. Major mission timeline changes may be required.', 'Execute crew radiation emergency procedures. Shelter, abort EVA, protect critical crew tasks, and coordinate mission leadership.', 'Avoid public/aviation assumptions; this is mission-architecture-specific.'),
    },
  },
  {
    name: 'Emergency Management / Critical Comms',
    description: 'Use for emergency managers, public safety, critical communications, and continuity-of-operations partners.',
    hazardFamilies: ['HF absorption', 'GNSS/scintillation/TEC', 'SATCOM impacts', 'Power-grid GMD risk'],
    keyIndicators: ['HF/R-scale/D-RAP', 'GNSS scintillation/TEC', 'SATCOM impacts', 'Regional E-field/GIC', 'Critical infrastructure dependencies'],
    confidenceNote: 'Answer which communications, navigation/timing, and infrastructure dependencies remain reliable in the affected area.',
    impactLevels: {
      '1': level('Routine', 'No route/AOR-relevant HF, GNSS, SATCOM, or grid risk; R0; G0-G1; no regional scintillation alert; E-field quiet.', 'No space-weather-driven emergency-management action expected.', 'Routine monitoring. Keep dashboard available for situational awareness.', 'Scope to the emergency manager AOR, not global conditions.'),
      '2': level('Awareness', 'R1-R2 or weak HF absorption; G1-G2; weak scintillation indicators; grid/pipeline E-field awareness level; no critical service degradation reported.', 'Minor degradation possible. Backup systems should remain available.', 'Issue awareness note if partner requested. Recommend checking backup comms, timing holdover, and utility status.', 'Avoid alarmist language for public-facing comms.'),
      '3': level('Elevated', 'R2-R3 or route/AOR HF degradation; G3; moderate scintillation/TEC gradients; E-field elevated; localized grid/comms partner concerns.', 'Emergency communications or timing may be degraded regionally. Some backup pathways may be needed.', 'Brief emergency managers. Identify affected frequencies/services, alternate comms, timing backups, utility points of contact, and public-message needs.', 'This level should generate plain-language action statements.'),
      '4': level('High', 'R4 or major D-RAP/PCA; G4 or high regional E-field; strong scintillation/GNSS degradation; SATCOM issues; grid risk high in AOR.', 'Multiple communications or infrastructure dependencies may need active management.', 'Activate comms contingency planning. Coordinate with utilities, telecoms, aviation/maritime/public safety, and state/federal partners.', 'Include confidence and expected duration.'),
      '5': level('Severe / Extreme', 'R5 or severe/persistent HF/PCA; G5/Hpo high; severe GNSS/timing disruption; E-field severe; critical infrastructure partners report operational impacts.', 'Critical comms, timing, or infrastructure dependencies may be unreliable in affected regions.', 'Execute emergency coordination posture. Provide regular IDSS briefings, fallback comms guidance, utility status integration, and public-facing risk messaging.', 'Do not imply nationwide failure unless partner data support it.'),
    },
  },
  {
    name: 'Public / Aurora',
    description: 'Use for public aurora visibility and public-facing space weather awareness.',
    hazardFamilies: ['Geomagnetic storm', 'Auroral oval/viewline', 'Public communication'],
    keyIndicators: ['Kp/G-scale', 'Regional auroral oval/viewline', 'Geomagnetic latitude', 'Local night/clouds/light pollution', 'Hpo context'],
    confidenceNote: 'Do not frame as public safety risk unless other sector tables indicate infrastructure or communications risk.',
    impactLevels: {
      '1': level('Routine', 'Kp <4 or aurora confined to usual high latitudes; regional aurora forecast quiet; no public infrastructure message needed.', 'Normal public conditions. Aurora unlikely outside high-latitude areas.', 'No special public action. Provide routine educational content if desired.', 'Weather/clouds affect visibility but are not space weather indicators.'),
      '2': level('Minor / Interest', 'Kp 4-5 / G1 context; aurora possible at high latitudes or northern-tier viewing areas; public interest rising.', 'Aurora viewing possible for high-latitude/northern users. Minimal public-safety implications.', 'Post aurora visibility guidance and explain that visibility does not equal infrastructure impact.', 'Use regional auroral oval/viewline instead of Kp alone.'),
      '3': level('Moderate / Broad Interest', 'Kp 6 / G2 context; aurora possible farther equatorward, around typical G2 visibility guidance; social/media interest likely.', 'Broader aurora viewing opportunity. Some users may ask about technology impacts.', 'Provide public explainer with separate links to operational impacts if needed. Coordinate with media/social teams.', 'Keep public language simple and non-alarmist.'),
      '4': level('High / Widespread Visibility', 'Kp 7-8 / G3-G4 context; aurora possible into mid-latitudes; high public interest; separate sector products may show GNSS/HF/grid impacts.', 'Widespread public attention and possible misinformation risk. Aurora may be highly visible where skies cooperate.', 'Issue coordinated public messaging: what to expect, where aurora may be visible, and what impacts are/are not expected.', 'Use separate risk sections for grid/comms, not aurora color alone.'),
      '5': level('Exceptional / Historic Visibility', 'Kp 9 / G5 or high Hpo context; aurora possible unusually far equatorward; potentially historic event; separate IDSS sectors should assess infrastructure risk.', 'Exceptional public attention. Public may conflate aurora with catastrophic infrastructure impacts.', 'Provide frequent plain-language updates and clear separation between aurora visibility, space weather conditions, and any actual infrastructure advisories.', 'Avoid "extreme means catastrophic" unless sector data support it.'),
    },
  },
  {
    name: 'Space Domain Awareness',
    description: 'Use for catalog maintenance, tracking, conjunction assessment, reentry prediction, LEO operator coordination, and space traffic coordination.',
    hazardFamilies: ['Neutral density / drag', 'Geomagnetic storm', 'Tracking uncertainty'],
    keyIndicators: ['Neutral density', 'Drag acceleration', 'Percent density/drag increase', 'G/Hpo/Ap context', 'Tracking residuals', 'Covariance growth'],
    confidenceNote: 'Related to satellites, but focused on orbit knowledge and tracking uncertainty rather than spacecraft health.',
    impactLevels: {
      '1': level('Routine', 'Neutral density/drag near baseline, e.g., <10% prototype increase; G0-G1; tracking residuals and covariance nominal.', 'Normal orbit determination and conjunction assessment quality.', 'Routine tracking, screening, and catalog maintenance.', 'No official neutral-density scale currently exists; percent thresholds are prototype.'),
      '2': level('Awareness', 'Neutral density +10-25% prototype; G1-G2; early tracking residual increase for very low LEO or high area-to-mass objects.', 'Minor drag awareness. OD updates may be needed for sensitive LEO objects.', 'Increase monitoring of low-perigee and high-drag objects. Flag likely covariance growth.', 'Tune thresholds by altitude, ballistic coefficient, and tracking cadence.'),
      '3': level('Elevated', 'Neutral density +25-50% prototype; G3; drag model residuals increasing; conjunction screening sensitivity affected in LEO.', 'Orbit prediction uncertainty is elevated. Conjunction assessments and maneuver planning may require more frequent updates.', 'Increase tracking/OD cadence. Re-run conjunction screenings and notify affected LEO operators.', 'G-scale is a proxy; use density/drag products when available.'),
      '4': level('High', 'Neutral density +50-100% prototype; G4; significant residuals/covariance growth; catalog maintenance burden high; reentry predictions shifting.', 'Large orbit-prediction uncertainty for affected LEO population. Collision-risk management may be degraded.', 'Coordinate SDA operators. Prioritize tracking, update reentry/conjunction products, and communicate uncertainty bounds.', 'Communicate uncertainty explicitly.'),
      '5': level('Severe / Extreme', 'Neutral density >100% prototype; G5/Hpo high-end; severe drag/residuals; major catalog disruption or widespread LEO covariance growth.', 'Severe tracking/orbit-prediction degradation. Conjunction assessment and reentry prediction may be unreliable until recovery.', 'Execute SDA storm posture. Prioritize critical objects, communicate catalog uncertainty, coordinate with satellite operators and national/international partners.', 'STPI notes neutral-density products are an evolving research area.'),
    },
  },
  {
    name: 'Surveying / Geomatics',
    description: 'Use for magnetic surveys, GNSS surveying, RTK/PPP, photogrammetry ground control, precision agriculture-style positioning support, and geodetic operations.',
    hazardFamilies: ['Geomagnetic disturbance', 'GNSS scintillation', 'TEC disturbance'],
    keyIndicators: ['Local K/Kp/regional Hpo', 'dB/dt', 'Magnetometer noise', 'S4/sigma-phi', 'TEC gradients/ROTI', 'Correction service status'],
    confidenceNote: 'Distinguish magnetic-field disturbance from GNSS ionospheric disturbance.',
    impactLevels: {
      '1': level('Routine', 'Local K <4; dB/dt quiet; S4 <0.3 prototype; TEC gradients/ROTI normal; RTK/PPP/correction service nominal; magnetic survey residuals normal.', 'Precision surveying and magnetic operations expected to perform normally.', 'Routine QA/QC and normal field operations.', 'Use project tolerance as the final impact threshold.'),
      '2': level('Awareness', 'Local K 4-5 or G1 context; dB/dt rising; weak scintillation S4 0.3-0.4 prototype; correction age/residuals slightly degraded.', 'Minor delays or QA/QC flags possible. Sensitive magnetic surveys or long-baseline GNSS may need attention.', 'Advise crews to monitor fix status, residuals, PDOP/GDOP, correction age, and magnetometer stability.', 'Effects vary with receiver, baseline, constellation, and local ionosphere.'),
      '3': level('Elevated', 'Local K 6 or G2 context; moderate scintillation S4 0.4-0.6 prototype; TEC gradients disrupt RTK/PPP; magnetic noise exceeds project watch threshold.', 'RTK initialization delays, float solutions, lower confidence, or magnetic survey noise likely for sensitive work.', 'Consider schedule adjustments for high-precision tasks. Increase check shots, independent controls, and post-processing review.', 'Flag in pre-survey report and client risk notes.'),
      '4': level('High', 'Local K 7-8 or G3-G4 context; strong scintillation S4 >=0.6 prototype; frequent cycle slips/loss of lock; dB/dt/magnetic noise above operating threshold.', 'High-precision GNSS or magnetic survey operations may be unreliable in affected region.', 'Postpone sensitive magnetic/GNSS work if tolerances cannot be maintained. Use alternatives or additional controls.', 'Scope by region and local time; equatorial/auroral effects differ.'),
      '5': level('Severe / Extreme', 'Local K 9/G5 or high Hpo; severe/widespread scintillation; persistent loss of lock; correction services unusable; magnetic disturbance severe.', 'Precision operations likely unreliable. Significant rework risk if operations continue without mitigation.', 'Suspend or shift precision operations; move to redundant methods; document event for QA/QC and client communication.', 'STPI had limited direct engagement with some adjacent sectors, so validate with geomatics users.'),
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
const riskTextColor = computed(() => (riskLevel.value >= 3 ? '#ffffff' : '#111827'))
const riskOutputStyle = computed(() => {
  return {
    backgroundColor: riskColor.value,
    color: riskTextColor.value,
  }
})

function cellRiskLevel(impact: number, likelihood: number): number {
  return Math.ceil((impact * likelihood) / 5)
}

function impactLevelDetails(level: string): PartnerImpactLevel {
  return selectedSector.value?.impactLevels[level] ?? {
    label: '',
    thresholdIndicators: '',
    impact: '',
    action: '',
    confidence: '',
  }
}

function thresholdIndicatorItems(level: string): string[] {
  return impactLevelDetails(level).thresholdIndicators
    .split(';')
    .map((item) => item.trim())
    .filter(Boolean)
}

function sectorLevelStyle(level: string) {
  const index = Number(level) - 1
  return {
    '--sector-level-color': riskColors[index],
    backgroundColor: sectorLevelTints[index],
  }
}

function sectorLevelBadgeStyle(level: string) {
  const index = Number(level) - 1
  return {
    backgroundColor: riskColors[index],
    color: index >= 2 ? '#ffffff' : '#111827',
  }
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
    <section class="partner-section partner-sector-section">
      <div class="partner-section-heading">
        <h3>IDSS Sector Table</h3>
      </div>

      <v-btn-toggle
        v-model="selectedSectorName"
        class="partner-sector-toggle"
        color="primary"
        density="compact"
        divided
        mandatory
        variant="outlined"
      >
        <v-btn
          v-for="sector in sectors"
          :key="sector.name"
          :value="sector.name"
          size="small"
        >
          {{ sector.name }}
        </v-btn>
      </v-btn-toggle>

      <div v-if="selectedSector" class="partner-sector-topline">
        <div class="partner-sector-summary-card">
          <div class="partner-sector-summary-row partner-sector-summary-row--focus">
            <span class="partner-summary-label">Sector Focus</span>
            <p>{{ selectedSector.description }}</p>
          </div>
          <div class="partner-sector-summary-row">
            <span class="partner-summary-label">Hazard Families</span>
            <div class="partner-chip-row">
              <span v-for="family in selectedSector.hazardFamilies" :key="family" class="partner-chip">
                {{ family }}
              </span>
            </div>
          </div>
          <div class="partner-sector-summary-row">
            <span class="partner-summary-label">Primary Indicators</span>
            <div class="partner-chip-row">
              <span v-for="indicator in selectedSector.keyIndicators" :key="indicator" class="partner-chip">
                {{ indicator }}
              </span>
            </div>
          </div>
        </div>

        <div class="partner-risk-controls">
          <div class="partner-risk-title-row">
            <h3 class="partner-risk-title">Risk Evaluation</h3>
            <div class="partner-risk-help">
              <button
                class="partner-risk-help-button"
                type="button"
                aria-label="Show risk matrix reference"
              >
                i
              </button>
              <div class="partner-risk-help-popover" role="tooltip">
                <div class="partner-risk-help-title">Risk Matrix</div>
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
            </div>
          </div>

          <p class="partner-risk-note">
            Probability is the chance that relevant hazard conditions reach the selected level in the
            forecast window. Impact is the sector-specific consequence level, not a direct NOAA scale
            translation.
          </p>

          <div class="partner-risk-fields">
            <div class="partner-risk-field">
              <label class="partner-risk-label" for="partner-probability">Hazard Probability</label>
              <select id="partner-probability" v-model="selectedLikelihood" class="partner-risk-select">
                <option v-for="option in likelihoodOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>

            <div class="partner-risk-field">
              <label class="partner-risk-label" for="partner-impact">Sector Impact Level</label>
              <select id="partner-impact" v-model="selectedImpact" class="partner-risk-select">
                <option v-for="option in impactOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
          </div>

          <div class="partner-risk-output">
            <span class="partner-risk-output-label">Risk Level</span>
            <span class="partner-risk-output-cell" :style="riskOutputStyle">
              {{ riskLabel }}
            </span>
          </div>
        </div>
      </div>

      <div v-if="selectedSector" class="table-wrap">
        <table class="partner-sector-table">
          <thead>
            <tr>
              <th colspan="5">{{ selectedSector.name }}</th>
            </tr>
            <tr>
              <th>Level</th>
              <th>Threshold Indicators to Evaluate</th>
              <th>Possible Impact</th>
              <th>Suggested Action</th>
              <th>Confidence / Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="level in impactLevelIds" :key="level" :style="sectorLevelStyle(level)">
              <td>
                <strong class="partner-level-badge" :style="sectorLevelBadgeStyle(level)">
                  {{ level }}
                </strong>
                <span class="partner-level-label">{{ impactLevelDetails(level).label }}</span>
              </td>
              <td>
                <ul class="partner-threshold-list">
                  <li v-for="item in thresholdIndicatorItems(level)" :key="item">
                    {{ item }}
                  </li>
                </ul>
              </td>
              <td>{{ impactLevelDetails(level).impact }}</td>
              <td>{{ impactLevelDetails(level).action }}</td>
              <td>{{ impactLevelDetails(level).confidence }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped>
.partner-briefing {
  display: grid;
  gap: 20px;
  font-weight: 400;
}

.partner-section {
  display: grid;
  gap: 20px;
  padding: 18px;
  border-radius: 8px;
  border: 1px solid rgba(171, 199, 235, 0.14);
  background: rgba(255, 255, 255, 0.025);
}

.partner-sector-section {
  gap: 20px;
}

.partner-section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.partner-section h3 {
  margin: 0;
  color: #f2f7ff;
  font-size: 1.1rem;
  font-weight: 500;
  line-height: 1.15;
}

.partner-sector-toggle {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  justify-self: center;
  max-width: 100%;
  background: transparent;
  border: 0;
  border-radius: 0;
  overflow: visible;
}

.partner-sector-toggle :deep(.v-btn) {
  flex: 0 1 auto;
  min-height: 34px;
  padding-inline: 16px;
  color: rgba(231, 236, 244, 0.78) !important;
  background: rgba(145, 153, 166, 0.24) !important;
  border: 1px solid rgba(210, 218, 230, 0.18) !important;
  border-radius: 6px !important;
  box-shadow: none !important;
  font-size: 0.91rem !important;
  font-weight: 500 !important;
  letter-spacing: 0 !important;
  text-transform: none !important;
}

.partner-sector-toggle :deep(.v-btn.v-btn--active),
.partner-sector-toggle :deep(.v-btn[aria-pressed="true"]) {
  color: #ffe55e !important;
  background: #0b3f73 !important;
  box-shadow: inset 0 0 0 1px rgba(255, 229, 94, 0.38) !important;
}

.partner-sector-toggle :deep(.v-btn:not(.v-btn--active):hover) {
  background: rgba(178, 187, 201, 0.32) !important;
  color: rgba(255, 255, 255, 0.9) !important;
}

.partner-sector-topline {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(380px, 0.75fr);
  gap: 24px;
  align-items: stretch;
}

.table-wrap {
  display: grid;
  gap: 18px;
  overflow-x: auto;
}

.partner-sector-summary-card {
  display: grid;
  align-content: start;
  border: 1px solid rgba(171, 199, 235, 0.14);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.025);
  overflow: hidden;
}

.partner-sector-summary-row {
  display: grid;
  grid-template-columns: 158px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
  padding: 16px 18px;
}

.partner-sector-summary-row + .partner-sector-summary-row {
  border-top: 1px solid rgba(171, 199, 235, 0.12);
}

.partner-summary-label {
  display: block;
  color: #eff6ff;
  font-size: 0.84rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  line-height: 1.25;
  text-transform: uppercase;
}

.partner-sector-summary-card p,
.partner-chip-row {
  margin: 0;
}

.partner-sector-summary-card p {
  color: rgba(220, 230, 244, 0.8);
  font-size: 0.98rem;
  line-height: 1.4;
}

.partner-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.partner-chip {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  border: 1px solid rgba(171, 199, 235, 0.18);
  border-radius: 6px;
  background: rgba(95, 199, 255, 0.16);
  color: #d9efff;
  font-size: 0.84rem;
  font-weight: 400;
  line-height: 1.2;
  padding: 5px 10px;
}

.partner-chip:nth-child(2n) {
  border-color: rgba(62, 209, 159, 0.36);
  background: rgba(62, 209, 159, 0.16);
  color: #d9fff3;
}

.partner-chip:nth-child(3n) {
  border-color: rgba(255, 232, 100, 0.36);
  background: rgba(255, 232, 100, 0.16);
  color: #fff4ad;
}

.partner-chip:nth-child(4n) {
  border-color: rgba(255, 140, 66, 0.36);
  background: rgba(255, 140, 66, 0.16);
  color: #ffd2b2;
}

.partner-chip:nth-child(5n) {
  border-color: rgba(193, 42, 255, 0.36);
  background: rgba(193, 42, 255, 0.16);
  color: #efd0ff;
}

.partner-sector-table {
  min-width: 1120px;
  width: 100%;
  margin: 0;
  font-size: 0.98rem;
  line-height: 1.35;
}

.partner-sector-table td,
.partner-sector-table th {
  vertical-align: top;
  border: 1px solid #05070a;
  padding: 11px 13px;
  font-weight: 400;
}

.partner-sector-table th {
  background: #182536;
  color: #eff6ff;
  font-size: 0.98rem;
  font-weight: 500;
}

.partner-sector-table td {
  color: #ffffff;
}

.partner-sector-table tbody tr {
  box-shadow: inset 5px 0 var(--sector-level-color);
}

.partner-sector-table tbody td {
  background: transparent;
}

.partner-sector-table tbody td:first-child {
  width: 96px;
  text-align: center;
  vertical-align: middle;
}

.partner-sector-table tbody td:nth-child(2) {
  min-width: 315px;
  width: 34%;
}

.partner-level-badge {
  display: inline-grid;
  width: 30px;
  min-width: 30px;
  height: 30px;
  place-items: center;
  border-radius: 999px;
  font-weight: 500;
  font-size: 0.94rem;
}

.partner-level-label {
  display: block;
  color: #ffffff;
  font-size: 0.8rem;
  font-weight: 500;
  line-height: 1.15;
  margin-top: 4px;
}

.partner-threshold-list {
  display: grid;
  gap: 4px;
  margin: 0;
  padding-left: 14px;
}

.partner-threshold-list li {
  line-height: 1.3;
  padding-left: 1px;
}

.partner-risk-controls {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 16px;
  align-content: start;
  border: 1px solid rgba(171, 199, 235, 0.14);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.025);
  padding: 16px;
  text-align: left;
}

.partner-risk-title {
  margin: 0;
}

.partner-risk-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.partner-risk-help {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.partner-risk-help-button {
  display: inline-grid;
  width: 22px;
  min-width: 22px;
  height: 22px;
  place-items: center;
  border: 1px solid rgba(171, 199, 235, 0.28);
  border-radius: 999px;
  background: rgba(95, 199, 255, 0.1);
  color: #d9efff;
  font-size: 0.76rem;
  font-weight: 500;
  line-height: 1;
  padding: 0;
}

.partner-risk-help-popover {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  z-index: 20;
  width: min(820px, calc(100vw - 80px));
  padding: 10px;
  border: 1px solid rgba(171, 199, 235, 0.28);
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(17, 38, 61, 0.98), rgba(7, 18, 31, 0.99)),
    #0b1320;
  box-shadow: 0 20px 42px rgba(0, 0, 0, 0.42);
  opacity: 0;
  pointer-events: none;
  transform: translateY(-4px);
  transition: opacity 120ms ease, transform 120ms ease;
}

.partner-risk-help:hover .partner-risk-help-popover,
.partner-risk-help:focus-within .partner-risk-help-popover {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0);
}

.partner-risk-help-title {
  margin-bottom: 8px;
  color: #f2f7ff;
  font-size: 0.875rem;
  font-weight: 500;
}

.partner-risk-note {
  margin: 0;
  color: rgba(220, 230, 244, 0.72);
  font-size: 0.875rem;
  line-height: 1.4;
}

.partner-risk-fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.partner-risk-field {
  display: grid;
  gap: 5px;
}

.partner-risk-label {
  color: rgba(220, 230, 244, 0.8);
  font-size: 0.8rem;
  font-weight: 400;
}

.partner-risk-select {
  min-width: 0;
  appearance: none;
  border-color: #ffe864;
  background-color: rgba(4, 10, 18, 0.9);
  background-image:
    linear-gradient(45deg, transparent 50%, #ffe864 50%),
    linear-gradient(135deg, #ffe864 50%, transparent 50%);
  background-position:
    calc(100% - 18px) 50%,
    calc(100% - 12px) 50%;
  background-size:
    6px 6px,
    6px 6px;
  background-repeat: no-repeat;
  border-radius: 6px;
  font-size: 0.875rem;
  min-height: 40px;
  padding-block: 9px;
  padding-right: 34px;
}

.partner-risk-output {
  display: grid;
  grid-template-columns: auto minmax(130px, 1fr);
  gap: 8px;
  align-items: center;
  color: rgba(220, 230, 244, 0.86);
}

.partner-risk-output-label {
  color: rgba(220, 230, 244, 0.76);
  font-size: 0.8rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.partner-risk-output-cell {
  display: grid;
  min-height: 44px;
  min-width: 112px;
  place-items: center;
  border: 1px solid #d8e1ea;
  border-radius: 6px;
  font-size: 1.1rem;
  font-weight: 500;
}

.partner-risk-pill {
  border-radius: 999px;
  color: #fff;
  display: inline-flex;
  font-weight: 500;
  padding: 4px 10px;
}

@media (max-width: 760px) {
  .partner-sector-topline,
  .partner-risk-fields,
  .partner-risk-output,
  .partner-sector-summary-row {
    grid-template-columns: 1fr;
  }

  .partner-sector-toggle {
    justify-content: flex-start;
  }
}

.partner-matrix-layout {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.partner-matrix-table {
  min-width: 620px;
  font-size: 0.72rem;
}

.partner-matrix-table td,
.partner-matrix-table th {
  min-width: 78px;
  padding: 6px 8px;
}

.partner-legend {
  border: 1px solid rgba(171, 199, 235, 0.16);
  border-radius: 8px;
  overflow: hidden;
  min-width: 160px;
}

.partner-legend-title,
.partner-legend-item {
  padding: 7px 9px;
  text-align: center;
}

.partner-legend-title {
  background: rgba(255, 255, 255, 0.05);
  color: #eff6ff;
  font-weight: 500;
}

@media (max-width: 900px) {
  .partner-sector-topline {
    grid-template-columns: 1fr;
  }

  .partner-sector-table {
    width: 100%;
  }

  .partner-matrix-layout {
    flex-direction: column;
  }
}
</style>
