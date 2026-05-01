package com.dramaflow.controller;

import com.dramaflow.dto.*;
import com.dramaflow.service.WatchRecordService;
import jakarta.validation.Valid;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/watch-records")
public class WatchRecordController {

    private final WatchRecordService watchRecordService;

    public WatchRecordController(WatchRecordService watchRecordService) {
        this.watchRecordService = watchRecordService;
    }

    @PutMapping("/{episodeId}")
    public WatchRecordResponse upsertRecord(
            @PathVariable Integer episodeId,
            @Valid @RequestBody WatchRecordRequest data,
            Authentication auth) {
        Integer userId = (Integer) auth.getPrincipal();
        return watchRecordService.upsertRecord(userId, episodeId, data);
    }

    @GetMapping("/{episodeId}")
    public WatchRecordResponse getRecord(
            @PathVariable Integer episodeId,
            Authentication auth) {
        Integer userId = (Integer) auth.getPrincipal();
        return watchRecordService.getRecord(userId, episodeId);
    }

    @GetMapping
    public PageResult<WatchRecordResponse> listRecords(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            Authentication auth) {
        Integer userId = (Integer) auth.getPrincipal();
        return watchRecordService.listRecords(userId, page, size);
    }

    @GetMapping("/continue-watching")
    public List<ContinueWatchingItem> continueWatching(Authentication auth) {
        Integer userId = (Integer) auth.getPrincipal();
        return watchRecordService.continueWatching(userId);
    }
}
