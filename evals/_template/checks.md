# Deterministic Checks — [skill-name]

List the concrete, verifiable behaviors to check after each run.
These do not require code — they describe what to look for.

## Trigger checks

- [ ] Skill activates on all `should_trigger=true` prompts
- [ ] Skill does NOT activate on `should_trigger=false` prompts

## Process checks

- [ ] [Describe a command or step the agent must execute]
- [ ] [Describe another required step or tool call]
- [ ] [Describe any ordering constraint between steps]

## Output checks

- [ ] [Describe a file that must be created]
- [ ] [Describe the expected format or content of the output]

## Pitfall checks

- [ ] [Describe a known mistake the agent must avoid]
- [ ] [Describe another pitfall listed in SKILL.md]
