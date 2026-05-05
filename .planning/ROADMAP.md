# Roadmap: DramaFlow — 首页推荐改版验收

## Overview

This roadmap covers the validation and verification of the homepage recommendation revamp (Iteration 3). The personalized recommendation logic (WatchRecord-based sorting, completed drama demotion, graceful degradation) has already been implemented in the backend. This phase ensures every requirement and acceptance criterion is fully covered, verified by automated tests and end-to-end behavior checks.

## Phases

- [ ] **Phase 1: Homepage Recommendation Validation** - Ensure personalized recommendation works for logged-in users, degrades gracefully, and preserves unauthenticated behavior

## Phase Details

### Phase 1: Homepage Recommendation Validation
**Goal**: Personalized recommendation is correctly implemented — logged-in users see WatchRecord-based sorting, unauthenticated users see default sorting, and the system degrades gracefully
**Depends on**: Nothing (standalone verification)
**Requirements**: REC-01, REC-02, REC-03, REC-04
**Success Criteria** (what must be TRUE):
  1. Logged-in user with watch history receives drama list sorted with same-category dramas prioritized
  2. Completed dramas appear at lower positions in the recommended list (lower weight)
  3. Unauthenticated user receives default-sorted drama list (unchanged behavior)
  4. User with no watch history (or insufficient history) receives default-sorted drama list as fallback
  5. Backend sorting logic and H5 data binding are verified by automated tests (pytest for API, Cypress/Playwright for H5)
**Plans**: 2 plans
**UI hint**: yes

Plans:
- [ ] 01-01-PLAN.md — Implement personalized recommendation backend logic (service + route)
- [ ] 01-02-PLAN.md — Add automated tests for AC-DRAMA-07/08/09 and fallback behavior

## Progress

**Execution Order:**
Phases execute in numeric order: 1

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Homepage Recommendation Validation | 0/2 | Not started | - |
