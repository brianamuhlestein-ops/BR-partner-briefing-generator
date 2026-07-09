# SWIFT Suite Social Media Branding and Generation Guidance

Recommended repo path: `docs/brand/swpc_social_media_generation_guidance.md`

## Purpose

This document defines the visual and content rules for generating SWPC social media graphics from SWIFT suite WWA JSON products.

The social media graphic is not a separate forecast. It is a visual rendering of the authoritative product JSON.

The goal is:

**One message, multiple formats.**

Official product JSON should drive:

* official text product
* website product card
* partner email briefing
* social media graphic
* event timeline

## Standard Canvas Size

Use the standard slide/social graphic aspect ratio used in the SWPC mockups:

```text
7.5 inches wide by 5 inches high
```

Recommended export size:

```text
1536 px by 1024 px
```

This preserves the 3:2 aspect ratio and works well in briefings, social media posts, website cards, and PowerPoint.

## Core Brand Palette

### Primary Colors

```json
{
  "swpc_deep_navy": "#002B5C",
  "swpc_midnight_blue": "#001B3F",
  "nws_blue": "#005EA8",
  "statement_blue": "#0065B3",
  "light_blue_panel": "#EAF3FB",
  "white": "#FFFFFF",
  "cool_gray": "#D6DEE8",
  "text_charcoal": "#1E1E1E"
}
```

### Product Status Colors

```json
{
  "outlook": "#1E73BE",
  "statement": "#0065B3",
  "watch": "#F4B000",
  "advisory": "#F28C28",
  "warning": "#D94A1E",
  "observed_alert": "#B31B1B",
  "extreme": "#6E1E8C",
  "notice": "#5C6B7A",
  "all_clear": "#2E8540",
  "summary": "#0065B3"
}
```

## Font Guidance

Use fonts available in Canva and common web environments.

Recommended:

```text
Headline: League Spartan Bold
Product badge: League Spartan Bold
Subhead: Barlow Condensed SemiBold
Body: Source Sans Pro Regular
Body bold: Source Sans Pro Semibold
Numbers/percentages: Barlow Condensed Bold
```

Fallbacks:

```text
Headline fallback: Arial Black
Body fallback: Arial
```

## Common Layout

Every graphic should use the same visual skeleton:

1. Navy header
2. NOAA/NWS/SWPC identity on left
3. Product badge on right
4. Large plain-language headline
5. Subheadline and issue time
6. Short narrative summary
7. Confidence/status card
8. What We Know block
9. Image placeholder on right
10. Impact sector strip
11. Navy footer with update/action language and spaceweather.gov

## Header

Header background:

```text
#002B5C or gradient #001B3F → #003E7E
```

Header left:

```text
NOAA logo | NWS logo | SPACE WEATHER PREDICTION CENTER
NATIONAL WEATHER SERVICE
```

Header right:

Product badge, using the product type color.

Examples:

```text
SPACE WEATHER OUTLOOK
SPACE WEATHER STATEMENT
SPACE WEATHER WATCH
SPACE WEATHER ADVISORY
SPACE WEATHER WARNING
OBSERVED SPACE WEATHER ALERT
SPACE WEATHER NOTICE
SPACE WEATHER SUMMARY
```

Secondary badges may be used:

```text
UPDATED WATCH
UPDATED WARNING
ALL CLEAR
END OF EVENT
G5 CONDITIONS REACHED
ADVISORY IN EFFECT
```

## Image Placeholder

Every template should include a large right-side image placeholder unless the product type does not need imagery.

Placeholder text:

```text
INSERT APPROPRIATE IMAGE HERE
```

Do not hardcode solar imagery. The application may insert:

* AIA imagery
* SUVI imagery
* coronagraph imagery
* model output
* geoelectric field map
* Kp/observations graphic
* event timeline graphic
* no image if not appropriate

## Icon Style

Use simple, line-based icons in navy or product accent color.

Recommended sectors:

```json
{
  "power": "transmission tower",
  "hf_radio": "radio tower",
  "gnss": "satellite signal",
  "satellites": "satellite",
  "aviation": "airplane",
  "aurora": "aurora arc over horizon",
  "radiation": "radiation trefoil",
  "notice": "information or megaphone",
  "summary": "document or clipboard",
  "time": "clock",
  "confidence": "shield/check",
  "status": "info circle"
}
```

Avoid aurora icons that look like grass.

## Product Template Mapping

### Outlook Template

Use for:

```json
"product_type": "space_weather_outlook"
```

Color:

```text
#1E73BE
```

Structure:

```text
Headline: Active Space Weather Conditions Expected This Week
Subheadline: May 6–12
Confidence card: optional
What We Know: 3–5 bullets
Impact strip: possible sectors
Footer: Outlooks are issued once weekly on Mondays
```

### Statement Template

Use for:

```json
"product_type": "space_weather_statement"
```

Color:

```text
#0065B3
```

Use for event under analysis, all clear, or event-end context.

For event under analysis:

```text
Headline: CME Under Analysis
Subheadline: Active Region 3664
Confidence card: Low / Medium / High
What We Know: 3–5 bullets
Footer: No Watch or Warning in effect at this time
```

For all clear:

Use color:

```text
#2E8540
```

Keep same structure:

```text
Headline: Warning-Level Space Weather Event Has Ended
Subheadline: Conditions have decreased to advisory-level concern
Confidence card: Medium to High
What We Know: previous Warning ended, Advisory remains, minimal/minor residual impacts
Footer: Continue routine monitoring
```

### Advisory Template

Use for:

```json
"product_type": "space_weather_advisory"
```

Color:

```text
#F28C28
```

Structure:

```text
Headline: Lingering Geomagnetic Activity
Subheadline: Elevated Radiation Levels Continue
Confidence card: Medium to High
What We Know: 3–5 bullets
Impact strip: Power, HF Radio, GNSS, Satellites, Aviation
Footer: Advisory replaces previous Warning / continue monitoring
```

### Watch Template

Use for:

```json
"product_type": "space_weather_watch"
```

Color:

```text
#F4B000
```

Structure:

```text
Headline: Significant Geomagnetic Activity Possible
Subheadline: Friday into the Weekend
Confidence card: Low to Medium / Medium to High
What We Know: 3–5 bullets
Impact strip: Power, HF Radio, GNSS, Satellites, Aurora
Footer: Watch updated at least every 12 hours
```

### Warning Template

Use for:

```json
"product_type": "space_weather_warning"
```

Color:

```text
#D94A1E
```

Structure:

```text
Headline: Significant Geomagnetic Activity Expected
or
Renewed Severe to Extreme Geomagnetic Activity Possible
Subheadline: Friday into the Weekend / Sunday
Confidence card: Medium to High / High
What We Know: 3–5 bullets
Impact strip: Power, HF Radio, GNSS, Satellites, Aurora
Footer: Warning updated at least every 12 hours while in effect
```

Do not include all official text sections in social graphics. The graphic should summarize.

### Observed Alert Template

Use for:

```json
"product_type": "observed_space_weather_alert"
```

Color:

```text
#B31B1B
```

Structure:

```text
Headline: Strong Geomagnetic Conditions Reached
or
Extreme Geomagnetic Conditions Reached

Observed card:
G3 at 1637 UTC
or
G5 at 2254 UTC

What We Know:
- condition reached
- observation period
- magnetometer network basis
- station list if space allows

Impact strip:
Power, HF Radio, GNSS, Satellites, Aurora

Footer:
Event-level alert issued
Warning remains in effect
```

Observed alerts should not repeat every synoptic period. They are event-level alerts.

### Notice Template

Use for:

```json
"product_type": "space_weather_notice"
```

Color:

```text
#5C6B7A
```

Structure:

```text
Headline: CME Analysis May Be Affected
or
Coronagraph Imagery Degraded

Status card:
ONGOING / RESOLVED

What We Know:
- what system/data is affected
- what forecast process is affected
- official products remain in effect

Operational Impacts:
- degraded timeliness of updates
- possible unanalyzed CME lift-offs
- confidence in timing/duration/strength may change

Footer:
Forecast updates continue
Monitor SWPC products for changes
```

Notice is not a hazard product. Do not show hazard impact sectors unless they are relevant to why the degraded data matters.

### Summary Template

Use for:

```json
"product_type": "space_weather_summary"
```

Color:

```text
#0065B3
```

For mid-event summary:

```text
Headline: Significant Space Weather Event Ongoing
Subheadline: Mid-Event Recap
Status card: Warning in Effect
Three columns: Event Overview / Observed Conditions / Current Status
Impact strip: ongoing concerns
Footer: Warning remains in effect
```

For final summary:

```text
Headline: Historic Geomagnetic Storm Recap
Subheadline: Review of the May 10–12 CME Impacts
No confidence card
No What We Know card
Full-width Event Summary block
Operational Areas Affected strip
Footer: Event is over; return to normal monitoring
```

## Social Content Extraction Rules

The application should generate social media content from the product JSON using these rules:

### Headline

Prefer:

```json
rendering.social_media.headline
```

Fallback:

```json
message.title
```

Fallback:

```json
product.headline
```

### Subheadline

Prefer:

```json
rendering.social_media.subheadline
```

Fallback:

```json
timing.plain_language_time
```

### Confidence Card

Use when product type is:

```text
statement
watch
advisory
warning
```

Do not use for final summary products unless explicitly provided.

Confidence card content:

```json
confidence.display
confidence.summary
```

If `rendering.social_media.confidence_card` exists, use that instead.

### What We Know

Prefer:

```json
rendering.social_media.what_we_know
```

Fallback to selected facts from:

```json
probabilities[]
timing
hazard.expected_levels
sections.CONFIDENCE
sections.WHEN
sections.DURATION
```

Limit to 5 bullets.

### Impact Strip

Use:

```json
rendering.social_media.impact_icons
```

Fallback:

```json
impacts[].sector
```

Use labels under icons. No explanatory text in the impact strip unless the template explicitly supports it.

## Standard Footer Language

### Outlook

```text
Outlooks are issued once weekly on Mondays.
```

### Statement, event under analysis

```text
SWPC is analyzing the event and will issue updates as confidence changes.
No Watch or Warning in effect at this time.
```

### Watch

```text
Watch will be updated at least every 12 hours.
Monitor SWPC updates as confidence changes.
```

### Advisory

```text
Advisory replaces the previous Warning.
Continue monitoring SWPC products as conditions decrease.
```

### Warning

```text
Warning will be updated at least every 12 hours while in effect.
Monitor SWPC updates and follow sector-specific procedures.
```

### Observed Alert

```text
Event-level alert issued.
Warning remains in effect.
```

### Notice

```text
Forecast updates continue.
Monitor SWPC products for changes.
```

### Summary

```text
Event is over. SWPC will continue to monitor the Sun and near-Earth space environment.
Partners may return to normal monitoring of SWPC products and sector-specific guidance.
```

## Automation Trigger Guidance

### Forecast Console Triggers

When a forecaster issues or updates:

* Outlook
* Advisory
* Watch
* Warning
* Statement

the system should generate:

1. official text preview
2. website card
3. social media draft
4. partner briefing draft if product type is Watch, Warning, Advisory, or Summary

### Observations Monitor Triggers

When a threshold is observed:

* G3
* G4
* G5
* S-scale threshold
* R-scale threshold

the system should generate:

1. Observed Space Weather Alert JSON
2. website observed alert card
3. social media draft
4. event timeline entry

Do not issue repeated event-level alerts for the same threshold unless conditions wane below threshold and later re-intensify in a meaningful new phase.

### Notice Triggers

When data/model/product availability affects interpretation:

* coronagraph imagery delayed or degraded
* magnetometers unavailable
* GOES data delayed
* model outage
* product/API outage

the system should generate:

1. Space Weather Notice JSON
2. notice-style website card
3. notice-style social media draft if public/partner relevance is high

## Final Rule

The product JSON is the source of truth. Social graphics should never introduce a new forecast message. They should simplify, visualize, and amplify the official product message.
