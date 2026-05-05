---
phase: 02-player-state-machine-audit
plan: 01
subsystem: ui
tags: android, exoplayer, speed-selector, playback-speed

# Dependency graph
requires: []
provides:
  - speed_menu LinearLayout with 6 Button children, each with unique android:id
  - id-based speed button click handler in setupControls()
affects: [02-player-state-machine-audit]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "id-based binding: UI elements use android:id + findViewById instead of position-based/child-iteration matching, preventing breakage when elements are added or reordered"

key-files:
  created: []
  modified:
    - android/app/src/main/res/layout/activity_player.xml
    - android/app/src/main/java/com/dramaflow/player/ui/PlayerActivity.kt

key-decisions:
  - "Speed buttons use unique android:id (btn_speed_05/075/10/125/15/20) rather than position index or text matching, ensuring robustness against future layout changes (D-01)"

patterns-established:
  - "Speed button click handling uses id-based findViewById for each button individually, mapping R.id.btn_speed_XX to PlaybackSpeed enum values"

requirements-completed: [PLAYER-01]

# Metrics
duration: 2min
completed: 2026-05-05
---

# Phase 02 Plan 01: Speed Menu Expansion and Id-Based Click Handler Summary

**Added missing 0.75x and 1.25x speed buttons to the ExoPlayer speed selector menu and refactored click handling from text-matching to id-based findViewById binding**

## Performance

- **Duration:** 2 min
- **Started:** 2026-05-05T20:49:03+08:00
- **Completed:** 2026-05-05T20:50:07+08:00
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Added 0.75x and 1.25x speed buttons to speed_menu layout, bringing total to 6 options (0.5x~2.0x)
- Gave all 6 speed buttons unique android:id values (btn_speed_05/075/10/125/15/20) for reliable programmatic access
- Replaced child-iteration loop with text-matching click handler with individual id-based findViewById bindings
- Each button maps to its corresponding PlaybackSpeed enum value, eliminating the brittle default-to-1.0x fallback behavior

## Task Commits

Each task was committed atomically:

1. **Task 1: Add 0.75x and 1.25x buttons to speed_menu, give all 6 buttons unique IDs** - `d48e8b6` (feat)
2. **Task 2: Refactor speed button click handler to use id-based binding** - `5cd8c2e` (refactor)

## Files Created/Modified
- `android/app/src/main/res/layout/activity_player.xml` - Added 0.75x and 1.25x Button children to speed_menu, added unique android:id to all 6 buttons
- `android/app/src/main/java/com/dramaflow/player/ui/PlayerActivity.kt` - Replaced text-matching click handler loop with id-based findViewById bindings for all 6 speed buttons

## Decisions Made
- Used `binding.speedMenu.findViewById<Button>(R.id.btn_speed_XX)` pattern for each button individually rather than a single loop — follows the plan's intent of explicit id-based mapping (D-01)
- Kept the existing `viewModel.currentSpeed.observe` observer in `observeViewModel()` completely unchanged, preserving backward compatibility
- Used the same layout attributes and color scheme as existing buttons: `#B0B0B0` for non-default speeds, `#A29BFE` (Primary Light design token) for 1.0x default

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Speed menu UI is complete with all 6 required options
- Click handler is robust against future button additions/reordering
- Ready for Phase 02 Plan 02 (player state machine audit and cleanup tasks)

---
*Phase: 02-player-state-machine-audit*
*Completed: 2026-05-05*
