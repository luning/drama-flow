package com.dramaflow.dto;

import java.time.LocalDateTime;

public class WatchRecordResponse {
    private Integer id;
    private Integer userId;
    private Integer episodeId;
    private double progress;
    private double lastPosition;
    private boolean completed;
    private LocalDateTime updatedAt;

    public WatchRecordResponse(Integer id, Integer userId, Integer episodeId,
                               double progress, double lastPosition,
                               boolean completed, LocalDateTime updatedAt) {
        this.id = id;
        this.userId = userId;
        this.episodeId = episodeId;
        this.progress = progress;
        this.lastPosition = lastPosition;
        this.completed = completed;
        this.updatedAt = updatedAt;
    }

    public Integer getId() { return id; }
    public Integer getUserId() { return userId; }
    public Integer getEpisodeId() { return episodeId; }
    public double getProgress() { return progress; }
    public double getLastPosition() { return lastPosition; }
    public boolean isCompleted() { return completed; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
