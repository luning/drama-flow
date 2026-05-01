package com.dramaflow.dto;

import java.time.LocalDateTime;

public class ContinueWatchingItem {
    private Integer dramaId;
    private String dramaTitle;
    private String dramaCover;
    private Integer episodeId;
    private Integer episodeNumber;
    private String episodeTitle;
    private double progress;
    private double lastPosition;
    private LocalDateTime updatedAt;

    public ContinueWatchingItem(Integer dramaId, String dramaTitle, String dramaCover,
                                Integer episodeId, Integer episodeNumber, String episodeTitle,
                                double progress, double lastPosition, LocalDateTime updatedAt) {
        this.dramaId = dramaId;
        this.dramaTitle = dramaTitle;
        this.dramaCover = dramaCover;
        this.episodeId = episodeId;
        this.episodeNumber = episodeNumber;
        this.episodeTitle = episodeTitle;
        this.progress = progress;
        this.lastPosition = lastPosition;
        this.updatedAt = updatedAt;
    }

    public Integer getDramaId() { return dramaId; }
    public String getDramaTitle() { return dramaTitle; }
    public String getDramaCover() { return dramaCover; }
    public Integer getEpisodeId() { return episodeId; }
    public Integer getEpisodeNumber() { return episodeNumber; }
    public String getEpisodeTitle() { return episodeTitle; }
    public double getProgress() { return progress; }
    public double getLastPosition() { return lastPosition; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
