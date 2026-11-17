---
title: "To-Do: Add a Linux Interactive Session and Logon Feed"
type: diagnostic
confidence: medium
grounded_by:
  - streamlit/projects/HostActivity/queries.py
  - streamlit/projects/HostActivity/main.py
  - https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html
  - https://man7.org/linux/man-pages/man8/pam_exec.8.html
  - https://man7.org/linux/man-pages/man5/utmp.5.html
policy: agent-editable
last_validated: 2026-11-16
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/linux/sensor; ../wintap/shared/WintapAPI; streamlit/projects/HostActivity
tags: [todo, backlog, linux, session-events, logon-events, interactive-activity, telemetry-semantics, wintap]
---

# To-Do: Add a Linux Interactive Session and Logon Feed

**Priority:** P2 — Medium (provisional; the current dashboard signal is useful
only as a temporary approximation).
**State:** Open — intake finding; sensor/schema design has not started.
**Likely next step:** Prototype a small `systemd-logind` D-Bus consumer on a
supported Linux host, then define the common event contract and a PAM fallback
for hosts without logind.

## Finding

The Recent Host Activity dashboard's user heatmap is a barely acceptable
implementation of the user's question. It counts distinct process names from
`raw_process` Start events by normalized username and 15-minute bucket. The
aggregation is efficient and SQL-based, but the source event does not establish
that a user logged in, has an active interactive session, or was present when a
process started.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/queries.py §_process_activity_expression/_process_activity_user_expression/aggregate_family; streamlit/projects/HostActivity/main.py §_process_activity_chart -->

The heuristic can overstate activity from scheduled work, user services,
background agents, inherited credentials, or noninteractive automation. It can
also miss a genuinely active session when no qualifying process starts occur.
The deny-lists reduce obvious noise but cannot repair this semantic gap. Keep
the chart explicitly labeled as a likely-user-activity proxy; do not present it
as session or logon detection.

## Recommended simple Linux design

### Preferred path: systemd-logind

On hosts running systemd, subscribe to the system bus interface
`org.freedesktop.login1`. The manager exposes `SessionNew` and
`SessionRemoved` signals, and `ListSessions`/`ListSessionsEx` for an initial
snapshot. The session object exposes the username, session ID, creation
timestamp, service, TTY/display, local/remote flag, session type/class, state,
and leader information. This is a small event-driven feed and avoids process
start inference.
<!-- SOURCE: https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html -->

The first implementation should:

1. Take an initial `ListSessions` snapshot before subscribing or reconcile the
   snapshot after subscription so a startup race cannot lose a session.
2. Emit `SessionStart` and `SessionEnd` records keyed by the logind session ID.
3. Fetch the session properties after `SessionNew`; retain the session type,
   class, service, TTY/display indicator, remote flag, and timestamps.
4. Treat `Class=user` sessions with interactive types such as `tty`, `x11`,
   `wayland`, or `mir` as the initial activity population. Preserve the raw
   type/class so downstream policy can change without recollection.
5. Keep active/idle and screen-lock state separate from login/logout. A locked
   session is not necessarily logged out, and a foreground session is not
   necessarily being actively used.

This should be the canonical Linux implementation where logind is present. It
provides a clean lifecycle identity and supports multiple simultaneous sessions
for one user without pretending that process diversity is a session signal.

### Fallback path: PAM session hooks

For non-systemd hosts, or where logind coverage is insufficient, use an optional
PAM session hook. Linux-PAM's `pam_exec` can invoke a local helper for
`open_session` and `close_session` and supplies `PAM_USER`, `PAM_TTY`,
`PAM_RHOST`, `PAM_RUSER`, `PAM_SERVICE`, and `PAM_TYPE` in the child
environment.
<!-- SOURCE: https://man7.org/linux/man-pages/man8/pam_exec.8.html -->

The helper should write a small event to a local Unix socket or durable spool,
not perform network I/O or block the login path. Configure it as an explicitly
optional session module and qualify each target distribution's PAM stack. The
feed must document that coverage depends on every relevant login service calling
PAM and that close events can be lost during abrupt failure.

### Limited fallback: utmp/wtmp

`utmp` is a simple source for a current-login snapshot and `wtmp` contains login
and logout records, but the Linux manual warns that not all programs use utmp
logging. Treat it as a compatibility or reconciliation source, not the
canonical event feed. It lacks the lifecycle and coverage guarantees needed to
replace logind/PAM evidence.
<!-- SOURCE: https://man7.org/linux/man-pages/man5/utmp.5.html -->

## Proposed minimal event contract

Use a new raw family such as `raw_session` or `raw_logon` with:

- `EventTime` and `ActivityType`: `Start` or `Stop`;
- stable `SessionId` within the host's observation lifetime;
- normalized `UserName` and numeric `Uid`;
- `SessionType`, `SessionClass`, `Service`, and optional TTY/display;
- `Remote` plus optional remote-origin metadata subject to the existing privacy
  policy;
- source/backend and an evidence or completeness indicator.

The downstream model should turn paired start/stop events into session
intervals, retain open intervals at the observation boundary, and distinguish
session existence from foreground/idle/locked state. The dashboard can then
render user-by-time presence or active-session minutes. The current process
heatmap should remain available only as a clearly marked fallback until the new
feed has adequate coverage.

## Acceptance checks

- Validate console/TTY login, SSH login, graphical login where available,
  logout, disconnect, lock/unlock, multiple sessions for one user, and sensor
  restart recovery.
- Compare live session snapshots with `loginctl` on logind hosts and with the
  configured PAM services on fallback hosts.
- Verify no process command lines, paths, or individual process details are
  needed for the session metric.
- Quantify missing close events, duplicate starts, reconnect behavior, and
  coverage differences between logind and PAM before promoting the feed to
  canonical status.

## References

- [systemd-logind D-Bus interface](https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html)
  documents session lifecycle signals, enumeration, and session properties.
- [Linux-PAM `pam_exec(8)`](https://man7.org/linux/man-pages/man8/pam_exec.8.html)
  documents session hooks and exported PAM context.
- [Linux `utmp(5)`](https://man7.org/linux/man-pages/man5/utmp.5.html)
  documents current and historical login records and their coverage warning.
