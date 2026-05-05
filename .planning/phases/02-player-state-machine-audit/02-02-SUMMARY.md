---
phase: 02-player-state-machine-audit
plan: 02
type: execute
subsystem: android-player
tags:
  - player-state-machine
  - ac-annotation
  - error-recovery
  - ac-compliance
requires:
  - 02-01 (speed menu expansion with id-based click handlers)
provides:
  - AC-annotated source code for state machine traceability
  - Working recover() path with ExoPlayer reset
  - IDLE state cleanup on player release
affects:
  - android/app/src/main/java/com/dramaflow/player/viewmodel/PlayerViewModel.kt
  - android/app/src/main/java/com/dramaflow/player/ui/PlayerActivity.kt
tech-stack:
  added: []
  patterns:
    - AC-number comment annotations for spec traceability
    - State observer guard pattern: `state == BUFFERING && playbackState == STATE_IDLE`
key-files:
  created: []
  modified:
    - android/app/src/main/java/com/dramaflow/player/viewmodel/PlayerViewModel.kt
    - android/app/src/main/java/com/dramaflow/player/ui/PlayerActivity.kt
decisions:
  - "State observer is the correct bridge for ExoPlayer reset on recover() — ViewModel must not handle ExoPlayer lifecycle (关注点分离)"
  - "Dual IDLE path (ExoPlayer listener callback + explicit setState) provides defense in depth without harm due to setState guard"
  - "player?.playbackState == STATE_IDLE guard prevents duplicate prepare() during normal buffering"
metrics:
  duration: null
  completed_date: "2026-05-05"
---

# Phase 02 Plan 02: ExoPlayer State Machine AC Annotation and Fixes

Audit of the ExoPlayer state machine against all 12 AC-PLAYER-10~21 transitions, with inline AC-number annotations added for traceability, fixes to the recover() path and player release cleanup.

## What Was Built

1. **State machine comment block** in `PlayerViewModel.kt` documenting all 7 states and their legal transitions with AC-PLAYER-10~21 references
2. **AC-annotated `onPlaybackStateChanged`** listener in `PlayerActivity.kt` — each `when` branch annotated with the relevant AC number (AC-12 initial load, AC-12/14 buffering, AC-12/14 ready, AC-13 play/pause decision, AC-15 ended)
3. **AC-annotated `onPlayerError`** with // AC-PLAYER-16 comment
4. **AC-annotated state observer** with // AC-PLAYER-16/15 for controls auto-show on error/end
5. **AC-PLAYER-17 fix**: State observer now detects `state == BUFFERING && player?.playbackState == STATE_IDLE` and calls `player?.prepare()` with `playWhenReady = true` — this actually resumes playback after `recover()`, which previously only set the ViewModel state without triggering ExoPlayer
6. **AC-PLAYER-18 fix**: `onDestroy()` now calls `viewModel.setState(PlayerState.IDLE)` after `player?.release()`, providing defense in depth alongside the ExoPlayer listener callback which also fires STATE_IDLE on release

## Deviation Handling

None — all tasks were executed as specified in the plan without deviations.

## Verifications

### AC Numbers in Source Code

- **PlayerViewModel.kt**: 2 AC-PLAYER references (state machine comment block lines 29-38, recover() line 70)
- **PlayerActivity.kt**: 9 AC-PLAYER references covering AC-12, AC-13, AC-14, AC-15, AC-16, AC-17, AC-18

### Automated Checks

```bash
# AC annotations in ViewModel
grep -c "AC-PLAYER" PlayerViewModel.kt  # => 2 (expected >= 2)

# AC annotations in PlayerActivity
grep -c "AC-PLAYER" PlayerActivity.kt  # => 9 (expected >= 5)

# configChanges in AndroidManifest
grep configChanges AndroidManifest.xml  # => confirmed present (AC-11)

# STATE_IDLE guard in observer
grep "STATE_IDLE" PlayerActivity.kt  # => 3 occurrences (listener + comment + guard)

# Release→IDLE
grep "setState.*PlayerState.IDLE" PlayerActivity.kt  # => 2 occurrences (listener + onDestroy)
```

### Pre-Existing Compliance Verified

| AC-ID | Description | Status |
|-------|-------------|--------|
| AC-PLAYER-11 | configChanges=orientation|screenSize|keyboardHidden | Already present |
| AC-PLAYER-19 | Speed changes do not affect state machine | setSpeed() only changes _currentSpeed, no setState() call |
| AC-PLAYER-20 | 6-speed enum, default 1.0x | PlaybackSpeed enum has 6 values, _currentSpeed initial value SPEED_1X |
| AC-PLAYER-21 | Speed immediate, time display unaffected | currentSpeed observer calls player?.setPlaybackSpeed() directly |

## Known Stubs

None — no stubs introduced or detected.

## Threat Surface Scan

No new security-relevant surface introduced. Changes are limited to:
- AC annotations (comments only)
- State observer guard (existing observer, additional condition check)
- setState(IDLE) call in onDestroy (existing method, single line addition)

## Commits

| # | Commit | Message |
|---|--------|---------|
| 1 | 208ccbd | docs: annotate all 12 AC-PLAYER-10~21 transitions in source code |
| 2 | 95c1deb | fix: add ExoPlayer reset handler in state observer for ERROR->BUFFERING |
| 3 | f21a2e1 | fix: set IDLE state on player release in onDestroy() |

### Post-commit Deletion Checks

No file deletions in any of the 3 commits.

## Self-Check: PASSED

All modified files verified present, all commits verified in git log, all acceptance criteria met.
