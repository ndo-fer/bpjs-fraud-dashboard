# Editorial Console UI Redesign

## Goal

Redesign the `dashboard-v2` Streamlit UI so it feels more credible, intentional, and premium while staying easy to scan and easy to use.

The target outcome is a dashboard that:

- improves usability first, especially for claim input, batch review, and result scanning
- builds a stronger visual identity so the app no longer feels generic or AI-generated
- preserves the current workflow and information architecture rather than introducing a new product scope
- remains appropriate for academic demo, sidang, and prototype review contexts

## Product Direction

The approved visual direction is:

- primary style: `clinical editorial`
- tone: `premium medical modern`
- priorities: `usability first` and `identity first`
- selected concept: `editorial console`

This means the redesign should avoid both extremes:

- not a sterile enterprise dashboard with generic admin-tool styling
- not a flashy showcase UI that sacrifices scanning, trust, or task flow

The result should feel like a modern health analytics workspace with refined hierarchy, calmer surfaces, and stronger product character.

## Problems In Current UI

The current dashboard is readable and functional, but it has several presentation issues:

- page structure is too linear, with title followed by stacked components and little visual rhythm
- Streamlit defaults are still visually dominant, which makes the app feel templated
- summary metrics, warnings, and tables have weak hierarchy and similar visual weight
- the single-claim experience feels like a raw form plus result output, not a guided decision-support flow
- the batch page is usable but still looks like a simple upload-and-table screen rather than an operational review workspace
- the artifacts page presents useful information, but the layout still feels like a technical dump rather than a trust center
- the visual language does not yet communicate a clear premium-medical identity

## Design Principles

The redesign should follow these principles:

1. Clarity before decoration
The UI should always make the next important action and the current state obvious.

2. Premium through restraint
The interface should feel elevated through spacing, typography, surface layering, and hierarchy rather than heavy effects.

3. Editorial rhythm
Pages should read as intentional sections with strong pacing, not as stacked widgets.

4. Trust-oriented tone
Scoring output should feel evidence-based and careful, never theatrical or alarmist.

5. Default-light, not default-plain
The design may remain simple, but it must no longer look like untouched Streamlit.

## Information Architecture

The page set remains the same:

- Overview
- Single Claim Scoring
- Batch Upload
- Artifacts and Notes
- History

The redesign does not introduce new top-level pages. It improves the shell, section structure, and component hierarchy inside the existing navigation.

## Visual System

### Color Direction

Use a bright premium base with restrained medical accents:

- page background: soft off-white or warm clinical stone
- primary text: deep slate
- secondary text: muted graphite or blue-grey
- primary accent: deep teal or muted medical blue
- supporting accent: desaturated sage or soft steel
- borders: subtle cool grey lines
- surfaces: layered ivory or near-white cards with gentle contrast

Status colors should remain recognizable but refined:

- high priority: controlled brick-red or dark coral
- medium priority: muted amber
- low priority: calm teal-green

Avoid:

- saturated dashboard primaries
- pure white everywhere
- flat dark backgrounds as the main direction
- harsh red warning blocks unless the state truly deserves escalation

### Typography

Typography should feel editorial rather than default app UI:

- page titles: strong, compact, high-contrast
- eyebrow labels: small uppercase or tracked labels for framing sections
- body copy: short, quiet, supportive
- numbers and metrics: prominent, crisp, and spaced for quick reading

The typography system should emphasize:

- fewer paragraphs
- more concise framing copy
- better separation between title, subtitle, metrics, and detail text

### Surfaces and Depth

Use a restrained surface system:

- main canvas
- elevated cards for important content
- softer inset or secondary blocks for notes, metadata, and helper content

Depth should come from:

- spacing
- border treatment
- subtle shadow
- contrast between surfaces

Do not rely on loud gradients, glossy cards, or heavy neumorphism.

## Shell Layout

### Sidebar

The sidebar should feel like a calm product shell rather than a plain page list.

Required changes:

- clearer app identity block at the top
- more deliberate spacing between identity, navigation, and secondary utility content
- stronger active state for the current page
- quieter inactive states

The sidebar should support quick orientation without visually competing with the content area.

### Page Header Band

Every page should start with a structured header band containing:

- small framing label
- strong page title
- one-line explanatory subtitle
- optional status pill or contextual action row

This creates consistency and gives each page an immediate point of orientation.

### Section Rhythm

Pages should follow a repeated section rhythm:

- header band
- summary or primary action block
- secondary context or evidence
- detail tables and extended content

The goal is to reduce the feeling of one long vertical column of widgets.

## Page Strategy

### Overview

The overview becomes a landing workspace rather than a generic explanation page.

Target structure:

- header band
- short product framing
- three capability cards
- current artifact or model status
- short "how to use" sequence

The overview should answer:

- what this dashboard is
- what workflows it supports
- how to start

### Single Claim Scoring

This page becomes a guided assessment flow.

Target structure:

- header band
- core input area in a strong primary card
- advanced input in a quieter secondary panel
- API/model status presented as contextual utility, not as a loud banner
- result panel as the visual centerpiece after scoring
- supporting explanation for top factors and detail view

The result card should feel like a decision-support summary, not a generic alert.

### Batch Upload

This page becomes the most operational page in the app.

Target structure:

- header band
- upload action area and template download
- preview block
- summary metric strip
- distribution visualization
- result table and filtering tools

This page should feel like a review desk for many claims, with strong scanability and less visual noise.

### Artifacts and Notes

This page becomes the model trust center.

Target structure:

- header band
- artifact identity and threshold summary
- evaluation metrics
- model limitations and caveats
- feature importance
- pipeline explanation and disclaimer

The goal is to make the page feel curated and trustworthy rather than like a notebook appendix.

### History

This page becomes a lightweight audit trail.

Target structure:

- header band
- small filter/search utilities
- compact summary of recent activity
- scan-friendly historical table

Priority, score, and timestamp should carry the strongest visual emphasis.

## Component Strategy

### Metric Strip

Metric cards must stop feeling like equal-weight defaults.

Required improvements:

- stronger numeric scale
- clearer primary-to-secondary hierarchy
- tighter label styling
- more spacing and cleaner grouping

One metric on a page may carry more emphasis than the others when the context justifies it.

### Result Card

The single-claim result card should be redesigned into a composed decision panel with:

- clear priority marker
- large risk percentage
- short interpretation sentence
- subtle supporting metadata

This component is a signature element of the new UI and should visually anchor the scoring experience.

### Form Groups

Forms should be grouped semantically and visually:

- core claim inputs feel quick and approachable
- advanced inputs feel available but non-threatening
- helper copy explains why advanced fields exist

Inputs should not look like a raw scroll of controls.

### Upload Area

The batch upload area should feel like a deliberate ingestion surface:

- clear drop/upload focus
- template guidance nearby
- concise explanation of expected file structure

### Tables

Tables should emphasize decision-relevant fields first:

- priority
- risk percent
- score
- threshold or supporting signal

Lower-value technical columns should be visually secondary even if still present.

### Status and Disclaimer Blocks

Warnings and notes should be redesigned as reusable contextual blocks:

- less loud by default
- clearer distinction between information, caution, and system status
- more integrated with the page aesthetic

## Content Style

Copy should be tightened throughout the UI:

- fewer generic explanations
- more action-oriented phrasing
- less repeated disclaimer weight on every screen
- more concise contextual framing

Disclaimers remain important, but they should be styled and placed in a way that supports trust instead of interrupting flow.

## Scope

This redesign includes:

- app shell styling
- page header system
- visual system tokens and styling direction
- layout and spacing updates across all main pages
- redesigned result, metric, and status patterns
- improved usability of core and advanced sections

This redesign does not include:

- changing the underlying scoring logic
- changing data contracts or model artifacts
- adding new product capabilities
- introducing a separate frontend framework

## Implementation Shape

The implementation should likely center around:

- a shared styling layer injected into Streamlit
- reusable helper functions for page headers, metric strips, and status blocks
- page-by-page refactors to reorder content and apply the new structure

The work should preserve existing functionality while improving presentation and interaction clarity.

## Risks and Mitigations

### Risk: Over-styling reduces clarity

Mitigation:

- prefer spacing and structure over visual ornament
- test pages against quick scanability

### Risk: Premium styling becomes too dark or too dramatic

Mitigation:

- keep the primary direction bright and editorial
- use accent colors carefully and sparingly

### Risk: Identity improvements make the app feel less academic or trustworthy

Mitigation:

- maintain evidence-first copy
- keep metrics, caveats, and threshold explanations easy to find

### Risk: Streamlit styling becomes brittle

Mitigation:

- centralize style tokens and layout helpers
- avoid excessive selector fragility where possible

## Success Criteria

The redesign is successful if:

- the app no longer feels like a default Streamlit prototype
- the dashboard still feels simple, but intentionally simple
- new users can understand page purpose faster
- single-claim scoring feels guided and premium
- batch review feels operational and easier to scan
- the dashboard looks appropriate for academic presentation and product demo

