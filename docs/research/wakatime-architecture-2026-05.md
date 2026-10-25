---
title: WakaTime Architecture Findings — coding-harness-eval
description: WakaTime stack layers, capture surfaces and self-hosted backends; informs the WakaTime module design (#6)
category: research
created: 2026-05-26
updated: 2026-10-25
version: 1.0.0
---

# WakaTime Architecture Findings

Background research for #6 (WakaTime module: models, client, session_tagger,
quality_collector, correlator), first recorded in issue #20. Documents the WakaTime stack so
the module can target the right layer.

Re-checked at source on 2026-10-25 where reachable; claims that could not be re-checked from
this environment are marked **(unverified)**.

## Architecture

`vscode-wakatime` and every other editor plugin are thin wrappers around **`wakatime-cli`**,
the "command line interface to WakaTime used by all WakaTime text editor plugins" (a Go
binary). It handles heartbeats, project detection, offline buffering
(`~/.wakatime/offline_heartbeats.bdb`, synced later) and API sync. Config is a shared INI
file, `$WAKATIME_HOME/.wakatime.cfg` (default `~/.wakatime.cfg`), with `api_url` as the API
base URL.

**Implication for #6:** read aggregates (summaries, durations, projects) from the WakaTime
**REST API** directly. Invoking `wakatime-cli` only matters if the module *emits* heartbeats
(for example to tag agent runs as separate sessions). The CLI is the write-side tool; the
REST API is the read-side surface.

## Capture surfaces

What data the module can see depends on which surfaces feed it:

- **IDE plugins** — 70+ official (Vim, JetBrains, ...) **(unverified count)**; all wrap the CLI.
- **Linux shell hooks** — bash/zsh/fish community plugins; capture agent-shell activity outside
  the IDE (filed under a single `Terminal` project by default) **(unverified)**.
- **macOS / Windows desktop apps** — full-OS active-window tracking. No Linux desktop tracker
  exists **(unverified)**.
- **[ActivityWatch](https://activitywatch.net/)** — system-wide tracker that supports Linux;
  it has its own REST API and is not documented as WakaTime-API-compatible, so it would need a
  separate adapter if used as a parallel source.

## Self-hosted backends

[Wakapi](https://wakapi.dev) ("a minimalist, self-hosted WakaTime-compatible backend",
self-described as *partially* compatible) and [Hackatime](https://hackatime.hackclub.com)
("WakaTime-compatible coding time tracker") accept WakaTime clients repointed via `api_url`.
This removes the SaaS free-tier history limit (2 weeks **(unverified)**), which matters for
long-horizon agent studies that need more historical depth.

## Implications for #6

1. **Client** — target the WakaTime REST API; the same surface works against SaaS or a
   self-hosted Wakapi without code changes (within Wakapi's partial compatibility).
2. **session_tagger** — if tagging agent sessions, the heartbeat-emission path
   (`POST /users/current/heartbeats` **(unverified)**) is the right hook; the CLI is not
   required.
3. **Data window** — design assuming a self-hosted backend for unlimited history; SaaS becomes
   a degraded mode.
4. **Source coverage** — document which surfaces (IDE / shell / desktop) feed the data per
   platform: Linux is IDE + shell only, macOS/Windows can add full-OS desktop tracking. This
   affects what "coding activity" means in correlation outputs.

## Cross-references

- #6 — WakaTime module (implementation)
- [qte77/multi-tasking-quality-benchmark](https://github.com/qte77/multi-tasking-quality-benchmark)
  — downstream correlation consumer with the same retention pain point
- [qte77/dotfiles](https://github.com/qte77/dotfiles) — `.config/wakatime.cfg` (config source of
  truth)
- [qte77/polyforge-orchestrator](https://github.com/qte77/polyforge-orchestrator) — hosts the
  agent runs being evaluated

## Sources

- <https://github.com/wakatime/wakatime-cli> (README, `USAGE.md`)
- <https://wakatime.com/plugins>
- <https://github.com/muety/wakapi> / <https://wakapi.dev>
- <https://github.com/hackclub/hackatime> / <https://hackatime.hackclub.com>
- <https://github.com/ActivityWatch/activitywatch> / <https://activitywatch.net/>
