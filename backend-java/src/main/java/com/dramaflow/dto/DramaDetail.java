package com.dramaflow.dto;

import java.time.LocalDateTime;

public class DramaDetail {
    private Integer id;
    private String title;
    private String description;
    private Integer categoryId;
    private String categoryName;
    private Double rating;
    private String coverUrl;
    private Integer year;
    private String status;
    private long episodeCount;
    private LocalDateTime createdAt;

    public DramaDetail(Integer id, String title, String description, Integer categoryId,
                       String categoryName, Double rating, String coverUrl, Integer year,
                       String status, long episodeCount, LocalDateTime createdAt) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.categoryId = categoryId;
        this.categoryName = categoryName;
        this.rating = rating;
        this.coverUrl = coverUrl;
        this.year = year;
        this.status = status;
        this.episodeCount = episodeCount;
        this.createdAt = createdAt;
    }

    public Integer getId() { return id; }
    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public Integer getCategoryId() { return categoryId; }
    public String getCategoryName() { return categoryName; }
    public Double getRating() { return rating; }
    public String getCoverUrl() { return coverUrl; }
    public Integer getYear() { return year; }
    public String getStatus() { return status; }
    public long getEpisodeCount() { return episodeCount; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
