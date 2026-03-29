---
name: istat-sdmx-explorer
description: Explore ISTAT SDMX datasets step by step before downloading data. Use when the user wants to find an ISTAT dataflow, understand its dimensions, see valid filter values, decode codelists, or fetch a small sample without already knowing SDMX codes.
license: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike 4.0 International)
---

# ISTAT SDMX Explorer

Use this skill to explore ISTAT SDMX dataflows safely and efficiently before attempting full downloads or pipeline ingestion.

It works with any SDMX-aware toolchain that lets you:

- discover dataflows
- inspect structure
- inspect valid constraints
- decode codelists
- fetch a very small sample

The goal is not to fetch a huge dataset immediately. The goal is to:

1. identify the right dataflow
2. understand the structure
3. inspect valid values for the dimensions
4. decode the relevant codelists
5. fetch only a small sample to confirm the shape

## Definition of done

A task is complete when:

- the correct ISTAT dataflow has been identified
- the main dimensions are known
- valid filter values are available for the dimensions that matter
- at least one important codelist has been decoded when needed
- a small sample has been fetched successfully
- the response explains what the user can do next

## Preferred workflow

### Step 1 - Discover the dataflow

Start with a keyword search on dataflows.

Use a dataflow listing tool first. Search with simple topic keywords in Italian when possible.

Good examples:

- `occupazione`
- `popolazione`
- `reddito`
- `salute`
- `mobilita`

Do not guess the dataflow ID if you can discover it first.

### Step 2 - Inspect the structure

Once a candidate dataflow is selected:

- inspect the structure
- list the dimensions
- identify which dimensions look territorial, temporal, categorical, or measure-like

At this stage, explain the shape in plain language:

- what one row or observation likely represents
- which dimensions are likely mandatory filters
- whether time is explicit

### Step 3 - Get valid constraints

Before trying to build a query, inspect the valid values for each dimension.

This is the most important anti-error step.

Look for:

- territorial dimensions such as `REF_AREA`
- frequency dimensions such as `FREQ`
- time-related dimensions
- topic-specific dimensions

If a dimension has many values, summarize the count first and only expand the relevant ones.

### Step 4 - Decode codelists when needed

If a dimension uses coded values, decode the linked codelist before suggesting filters.

Prioritize:

- territorial codelists
- frequency codelists
- topic codelists relevant to the user question

When possible, provide both:

- code
- human label

If the codelist is hierarchical, mention parent-child relations when they matter.

### Step 5 - Fetch only a small sample

Only after the previous steps:

- fetch a small sample
- confirm that the sample matches the expected structure

Use a very small limit.
The sample is for validation, not for final analysis.

### Step 6 - Explain the next move

End with a short practical conclusion. For example:

- ready to build a filtered request
- ready for a source-check
- ready for pipeline ingestion
- not ready because the dimensions are still ambiguous

## Output style

Keep the output structured and practical.

Recommended sections:

- `Dataflow`
- `Structure`
- `Valid filters`
- `Decoded codelists`
- `Sample`
- `Next step`

## Rules

- Do not start with a full data download
- Do not invent SDMX codes
- Do not assume territorial codes without decoding or constraints
- Prefer Italian labels when available
- If the sample endpoint is slow or incomplete, say so clearly
- If the dataflow looks wrong, go back to discovery instead of forcing the workflow

## Typical user intents

Use this skill when the user says things like:

- "find an ISTAT dataset about employment"
- "what dimensions does this ISTAT flow have?"
- "which values are valid for this ISTAT dimension?"
- "decode these ISTAT codes"
- "show me a sample of this ISTAT dataflow"

## Notes

This skill is about exploration and validation.

It does not replace:

- a pipeline connector
- a bulk ingestion workflow
- a public analysis
