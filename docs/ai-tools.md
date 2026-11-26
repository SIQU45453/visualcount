# AI coding tools for VisualCount

This repo is set up so an AI coding assistant (Claude Code) helps you better on this project.

| Tool | What it does for you | Status |
|---|---|---|
| [Ponytail](https://github.com/DietrichGebert/ponytail) | Makes the AI write the smallest code that works, keep safety checks, and add a small test for real logic. Adds `/ponytail-review` and `/ponytail-audit`. | Installed (rules in `AGENTS.md` + plugin) |
| [Agent Skills](https://github.com/addyosmani/agent-skills) (Addy Osmani) | A step-by-step way to work: `/spec` → `/plan` → `/build` → `/test` → `/agent-skills:review` → `/ship`. | Installed (plugin) |
| [Graphify](https://github.com/Graphify-Labs/graphify) | Turns a big codebase into a map the AI can search. | Not installed: VisualCount is only a few files, the AI reads them directly. Useful later if the project grows. |
| [OmniRoute](https://github.com/cheaper-inference/OmniRoute) | Sends your AI requests through many outside AI providers to use their free tiers. | Not installed: needs accounts and keys on many sites, sends your code to third parties, and does not help the counting app. |

Files:
- `AGENTS.md`: project facts + Ponytail rules. Read by Claude Code (through `CLAUDE.md`), Codex, Cursor, Copilot and others.
- `.claude/settings.json`: tells Claude Code to offer the Ponytail and Agent Skills plugins when you open this folder.

## Setup on Windows 10 (once)

1. **Install Git:** https://git-scm.com/download/win (keep the default options).
2. **Install Claude Code:** open **PowerShell** (Start menu, type `PowerShell`) and paste:
   ```powershell
   irm https://claude.ai/install.ps1 | iex
   ```
   Close PowerShell and open it again.
3. **Get the project:**
   ```powershell
   cd $HOME\Desktop
   git clone https://github.com/SIQU45453/visualcount
   cd visualcount
   claude
   ```
   Sign in with your Claude account the first time.
4. Claude Code asks if you **trust this folder**: answer yes. It then offers to install the
   **ponytail** and **agent-skills** plugins: accept both.
   If it does not ask, type these lines one at a time inside Claude Code:
   ```
   /plugin marketplace add DietrichGebert/ponytail
   /plugin install ponytail@ponytail
   /plugin marketplace add addyosmani/agent-skills
   /plugin install agent-skills@addy-agent-skills
   ```
   If the install fails with `Permission denied (publickey)`, run this once in PowerShell, then try again:
   ```powershell
   git config --global url."https://github.com/".insteadOf "git@github.com:"
   ```
5. Type `/plugin` to check that both are listed.

## How to use them

- New feature, for example "count each brand separately": start with `/spec`, then `/plan`, then `/build`.
- Before you push a change: `/ponytail-review`.
- Health check of the whole project: `/ponytail-audit`.
- Ponytail too strict for a task? `/ponytail lite`, or `/ponytail off`.

## Safety

Only install from these official sources. Copies with similar names exist:
- Ponytail: GitHub `DietrichGebert/ponytail` or npm `@dietrichgebert/ponytail` (it never ships `.exe` or `.dll` files).
- Agent Skills: GitHub `addyosmani/agent-skills`.
- Graphify (if you add it later): GitHub `Graphify-Labs/graphify`, Python package `graphifyy` (two y's).

Ponytail keeps its cost/time board on your PC (`~/.config/ponytail/band/`). Its optional webhook is empty by default, so nothing is sent out.
