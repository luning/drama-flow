package com.dramaflow.dto;

public class DramaListItem {
    private Integer id;
    private String title;
    private Integer categoryId;
    private Double rating;
    private String coverUrl;
    private Integer year;
    private String status;
    private long episodeCount;

    public DramaListItem(Integer id, String title, Integer categoryId, Double rating,
                         String coverUrl, Integer year, String status, long episodeCount) {
        this.id = id;
        this.title = title;
        this.categoryId = categoryId;
        this.rating = rating;
        this.coverUrl = coverUrl;
        this.year = year;
        this.status = status;
        this.episodeCount = episodeCount;
    }

    public Integer getId() { return id; }
    public String getTitle() { return title; }
    public Integer getCategoryId() { return categoryId; }
    public Double getRating() { return rating; }
    public String getCoverUrl() { return coverUrl; }
    public Integer getYear() { return year; }
    public String getStatus() { return status; }
    public long getEpisodeCount() { return episodeCount; }
}
