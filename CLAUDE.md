# CLAUDE.md — Claude Code overlay

`AGENTS.md` is the repository-wide policy. Do not duplicate it here.

At the start of substantive work:

1. read `AGENTS.md`;
2. read the active goal file (`goal.md` if present);
3. read `RESEARCH_STATE.md`;
4. read `wiki/index.md` and only the pages needed for the current experiment.

Treat `RESEARCH_STATE.md` as the concise current frontier, not as an infallible
authority. Resolve conflicts by inspecting the linked code, tests, reports, and
wiki evidence.

For autonomous research, follow the loop in `AGENTS.md`:

> one falsifiable hypothesis → one minimal discriminating intervention → fixed
> verifier → keep/reject → append experiment log → update state/wiki → repeat.

Do not broaden the experiment just because more compute is available. Prefer
the cheapest decisive calculation.

Use the project's existing evidence labels exactly:
`PROVED`, `VERIFIED_NUMERICALLY`, `PRELIMINARY_NUMERIC`, `CONJECTURE`,
`FALSIFIED`, `OPEN`.

Update `RESEARCH_STATE.md` only when the current frontier, champion, evidence
status, or next priority changes. Put detailed derivations/history in `wiki/`
or `research_reports/`, and raw run records in the experiment log.

Use `.agents/skills/zeus-hpc/SKILL.md` for production Zeus work,
`.agents/skills/high-impact-academic-scientific-writing/SKILL.md` for
manuscript work, and `.agents/skills/karpathy-llm-wiki/SKILL.md` for
maintaining the knowledge base (`wiki/`, `raw/`, index, and grounding).
Their boundaries and workflows remain in force.
