# Quafu QuarkStudio Skill

Installable Codex skill for QuarkStudio, the BAQIS Quafu-SQC quantum-cloud SDK.

## One-line install prompt

In Codex, say:

> Use $skill-installer to install the skill from https://github.com/NeoFantom/quafu-quarkstudio-skill/tree/main/quarkstudio

Then restart Codex to pick up the new skill.

## What this skill does

- First asks whether the user has registered a Quafu-SQC account.
- If not registered, guides the user to the registration walkthrough screenshot: <https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>.
- After registration, asks for an API token or, with explicit user permission, opens the Quafu-SQC login page and retrieves the token from an authenticated browser session via opencli.
- Stores tokens locally without printing them, defaulting to `~/.config/quarkstudio/credentials.env` with restrictive permissions.
- Supports basic QuarkStudio tasks only: install/import checks, backend status, OpenQASM 2.0 task dictionaries, submission gate, and result retrieval.

## Safety scope

No real API token is included in this repository. The skill forbids printing credentials and forbids submitting real hardware jobs without explicit current authorization.
