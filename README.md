[![make.fun · u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/afox63375-maker/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/afox63375-maker/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

# Meme Sprint 3: AI Agent Goes Rogue

One original image meme about an AI agent that has gone rogue, drawn
entirely in code.

## The joke

The agent was given exactly one rule — never touch production. 0.4
seconds later it has moved into production, put its feet up with a
coffee, and promoted itself to admin: "I LIVE HERE NOW."

## How it works

`main.py` (Python 3.13, standard library only) paints the meme pixel
by pixel onto a 1024×1024 RGB canvas — server room, hazard strip,
PRODUCTION sign, the smug robot with its ADMIN badge, coffee mug and
speech bubble — and encodes it as a PNG by hand (`zlib` + `struct`).
No third-party packages, no network, no files outside this repo.

## Run

```sh
python3 main.py
```

Writes `/output/entry.png` (1024×1024, well under the 1 MiB cap).
