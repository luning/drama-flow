---
phase: 04-test-coverage
plan: 02
subsystem: testing
tags: kotlin, android, viewmodel, livedata, unit-test, jvm

requires:
  - phase: 02-player-state-machine-audit
    provides: PlayerViewModel with setState/setSpeed/recover/toggleFullscreen methods
provides:
  - JVM unit tests for PlayerViewModel state machine transitions
  - Test infrastructure (InstantTaskExecutorRule) for synchronous LiveData assertions
  - Lazy initialization pattern for api field enabling direct ViewModel instantiation in tests
affects: []

tech-stack:
  added: androidx.arch.core:core-testing:2.2.0
  patterns:
    - LiveData synchronous testing via InstantTaskExecutorRule
    - by lazy for Android-context-dependent fields in ViewModel unit tests

key-files:
  created:
    - android/app/src/test/java/com/dramaflow/player/viewmodel/PlayerViewModelTest.kt
  modified:
    - android/app/build.gradle.kts
    - android/app/src/main/java/com/dramaflow/player/viewmodel/PlayerViewModel.kt

key-decisions:
  - "Used by lazy on api field instead of constructor parameter injection to keep ViewModelProvider backward compatible"
  - "Used InstantTaskExecutorRule for synchronous LiveData assertions in JVM unit tests"
  - "Individual test methods for each speed (6 tests) plus cycle test covering AC-PLAYER-20"

patterns-established:
  - "Unit test pattern: InstantTaskExecutorRule + ViewModel() direct instantiation + LiveData .value assertions"

requirements-completed: [TEST-02]
duration: 3min
completed: 2026-05-05
---

# Phase 04 Plan 02: PlayerViewModel Unit Tests Summary

**PlayerViewModel unit tests with 19 JVM test cases covering 7-state state machine, 6-speed switching, and 4-way recover path using InstantTaskExecutorRule for synchronous LiveData assertion**

## Performance

- **Duration:** 3 min
- **Started:** 2026-05-05T22:17:29+08:00
- **Completed:** 2026-05-05T22:18:48+08:00
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Added `androidx.arch.core:core-testing:2.2.0` for `InstantTaskExecutorRule` enabling synchronous LiveData assertions in JVM unit tests
- Changed `PlayerViewModel.api` field from eager `ApiClient.create()` initialization to `by lazy` so JVM unit tests can instantiate `PlayerViewModel()` without Android runtime context
- Created `PlayerViewModelTest.kt` with 19 test methods across 3 categories:
  - State machine (8 tests): initial IDLE state, transitions to all 6 states (PLAYING/PAUSED/BUFFERING/READY/ERROR/ENDED), same-state no-op
  - Speed switching (7 tests): initial 1X, all 6 speeds individually (0.5X through 2X), cycle through all values
  - Recover path (4 tests): from ERROR, PLAYING, PAUSED, ENDED -- all transition to BUFFERING

## Task Commits

Each task was committed atomically:

1. **Task 1: Add test dependency and make api field lazy** -- `384b144` (feat)
2. **Task 2: Create PlayerViewModelTest.kt** -- `21a5196` (test)

**Total commits:** 2

## Files Created/Modified

- `android/app/build.gradle.kts` -- Added `testImplementation("androidx.arch.core:core-testing:2.2.0")`
- `android/app/src/main/java/com/dramaflow/player/viewmodel/PlayerViewModel.kt` -- Changed `api` field from eager to `by lazy` initialization
- `android/app/src/test/java/com/dramaflow/player/viewmodel/PlayerViewModelTest.kt` -- Created with 19 test methods across state machine, speed switching, and recover path categories

## Decisions Made

- **by lazy over constructor injection:** Changing `api` to `by lazy` avoids constructor signature changes, keeping `ViewModelProvider` backward compatible. The `api` field is only accessed by `reportProgress()` and `fetchLastPosition()` which are not in scope for TEST-02.
- **Synchronous LiveData testing:** `InstantTaskExecutorRule` makes LiveData post values synchronously on the calling thread, enabling direct `.value` assertions. This is the simplest JVM-compatible approach compared to `observeForever` patterns.
- **Individual speed tests:** Testing all 6 speed values individually (not just 0.5X and 2X) ensures full enum wiring per AC-PLAYER-20.

## Deviations from Plan

None - plan executed exactly as written.

**Note:** The plan's `Output` section states "17 test cases" but the task content defines 19 test methods (8 state machine + 7 speed + 4 recover = 19). This is a minor counting discrepancy in the plan document; the actual implementation matches the specified task content exactly.

## Issues Encountered

None. Both tasks executed cleanly.

## Known Stubs

None. All test methods are fully implemented with assertions. No placeholder text or mock data stubs.

## Threat Surface

No new threat surface introduced. Unit tests operate entirely on JVM with in-memory LiveData. No network calls, no secrets, no tokens in test code. The `by lazy` change is semantically equivalent for `api` callers.

## Self-Check: PASSED

- Created file: `PlayerViewModelTest.kt` -- FOUND
- Modified file: `build.gradle.kts` with `core-testing` dependency -- FOUND
- Modified file: `PlayerViewModel.kt` with `by lazy` -- FOUND
- Commit `384b144` -- FOUND
- Commit `21a5196` -- FOUND

## Next Phase Readiness

- TEST-02 requirement satisfied: PlayerViewModel state machine, speed switching, and recover path all covered by unit tests
- Ready for any follow-up testing plans or player module refactoring

---
*Phase: 04-test-coverage*
*Completed: 2026-05-05*
