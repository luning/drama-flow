package com.dramaflow.dto;

import java.time.LocalDateTime;

public class EpisodeResponse {
    private Integer id;
    private Integer episodeNumber;
    private String title;
    private String duration;
    private String videoUrl;
    private LocalDateTime createdAt;

    public EpisodeResponse(Integer id, Integer episodeNumber, String title,
                           String duration, String videoUrl, LocalDateTime createdAt) {
        this.id = id;
        this.episodeNumber = episodeNumber;
        this.title = title;
        this.duration = duration;
        this.videoUrl = videoUrl;
        this.createdAt = createdAt;
    }

    public Integer getId() { return id; }
    public Integer getEpisodeNumber() { return episodeNumber; }
    public String getTitle() { return title; }
    public String getDuration() { return duration; }
    public String getVideoUrl() { return videoUrl; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
