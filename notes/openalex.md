# openalex

## Installing on Claude Desktop

To use this skill in Claude Desktop:

1. Create a ZIP archive that contains the `openalex/` folder at the top level, with `SKILL.md` directly inside that folder.
2. In Claude Desktop, open the skill installation wizard and load the ZIP file.
3. After installation, open the skill settings and add the required domains to the **Domain allowlist**.

### Required domains

Under *Additional allowed domains*, add:

- `openalex.org`
- `api.openalex.org`
- `content.openalex.org`

![Domain allowlist in Claude Desktop](assets/openalex-claude-desktop-domain-allowlist.png)

Without at least these domains, the sandbox will block core OpenAlex API calls and the skill will not work correctly.

Note: OpenAlex PDF downloads may also use additional hosts (for example, publisher sites or aggregators such as Europe PMC). If you need PDF retrieval to work, you may need to add those specific PDF host domains to the allowlist as well.
