# Product Requirements Document: onData Skills

## Overview

A curated collection of AI skills maintained by the [onData](https://www.ondata.it/) association. The project aims to make powerful AI-assisted workflows accessible to everyone, with a focus on data work: reading, transforming, analyzing, and visualizing data. Skills are designed to be tool-agnostic: usable with any AI assistant or agent platform that supports the skill format.

## Guiding Philosophy

The project is modeled on open source culture: a public repository, open contributions, transparent evolution, and community ownership. Skills are shared artifacts — anyone can use them, improve them, or propose new ones. The collection takes shape over time through collective effort, not top-down planning.

## Problem Statement

The value is not in filling a gap — many skill collections already exist. The value is in doing it together: a group of people passionate about the same topics, pooling what they find useful in the hope that it will be useful to others too.

## Goals

- Provide a **ready-to-use collection** of skills that anyone can install and start using immediately.
- Maintain a **browsable catalog** with clear titles and descriptions so people can find what they need.
- Write everything in **English** to maximize reach and LLM comprehension.
- Keep the barrier to entry **as low as possible**: simple installation, clear documentation, minimal prerequisites.

## Scope

### Skill Categories

There is no strict constraint on skill types. The collection will grow organically, but the core focus areas — reflecting the onData community's expertise — are:

- **Data reading** — importing, parsing, and inspecting data from various sources and formats.
- **Data transformation** — cleaning, reshaping, merging, and enriching datasets.
- **Data visualization** — generating charts, maps, and visual summaries.
- **Data quality** — validating, profiling, and auditing data.
- **Productivity & support** — any skill that facilitates, supports, or improves workflows related to the above.

There are no thematic constraints. Any skill that has proven useful to someone in the community — regardless of topic — is welcome, on the assumption that it may be useful to others too.

### What a Skill Contains

Each skill is a self-contained directory with:

- A **skill manifest** (`skill.md` or equivalent) with metadata: name, description, category, usage instructions.
- The **skill prompt** and any supporting files (templates, examples, reference docs).
- A **short entry** in the project catalog for discovery.

## User Experience

### Discovery

A user should be able to:

1. Open the catalog (initially a Markdown file in the repo).
2. Browse skills by title and short description.
3. Click through to a skill's directory for full documentation and usage examples.

### Installation

A user should be able to:

1. Clone or download the repository.
2. Follow a simple README guide to register one or more skills in their AI tool of choice.
3. Start using the skills immediately — no build steps, minimal external dependencies.

## Phases

### Phase 1 — Foundation

- Define the project structure and skill format.
- Write the README with installation instructions.
- Create the catalog (Markdown-based).
- Seed the collection with an initial set of skills.

### Phase 2 — Web Catalog

- Build a lightweight website that renders the catalog as a browsable, searchable interface.
- Each skill gets its own page with full description, usage examples, and install instructions.
- The site is generated from the same source data used by the Markdown catalog (single source of truth).

### Phase 3 — Community Growth

- Publish contribution guidelines.
- Accept skill submissions via pull request: anyone can open a PR to add their own skill to the collection.
- Introduce a review process to maintain quality.

## Constraints

- All content must be in English.
- Skills must work without external dependencies unless strictly necessary.
- The project structure must remain simple and navigable even without the web catalog.

## Success Criteria

- A non-technical user can install and use a skill within 5 minutes of reading the README.
- The catalog provides enough information to choose a skill without reading its full source.
- The collection covers at least the core data workflow (read → transform → visualize) at launch.

## Open Questions

- Should individual skills be versioned independently?
- What is the curation process for community-submitted skills?
- Should skills have maturity labels (e.g. experimental, stable)?
- What technology should the Phase 2 website use (static site generator, GitHub Pages, etc.)?
