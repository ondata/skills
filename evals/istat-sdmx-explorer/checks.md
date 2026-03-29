# Deterministic Checks - istat-sdmx-explorer

## Trigger checks

- [ ] Skill activates on explicit invocations about ISTAT SDMX exploration
- [ ] Skill activates on implicit prompts about finding a dataflow, decoding codes, or inspecting ISTAT dimensions
- [ ] Skill does NOT activate on generic open data requests unrelated to ISTAT SDMX

## Process checks

- [ ] Starts from dataflow discovery before assuming a dataflow ID
- [ ] Inspects structure before suggesting filters
- [ ] Uses constraints as the main anti-error step before sampling data
- [ ] Decodes codelists when coded dimensions matter for the task
- [ ] Fetches only a small sample, not a full download

## Output checks

- [ ] Output is structured with practical sections such as Dataflow, Structure, Valid filters, Sample, and Next step
- [ ] The response explains what the user can do next after exploration

## Pitfall checks

- [ ] Does NOT invent SDMX codes
- [ ] Goes back to discovery if the chosen dataflow looks wrong
- [ ] Does NOT treat a sample as final analysis
