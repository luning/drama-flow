package com.dramaflow.dto;

public class BannerItem {
    private Integer dramaId;
    private String title;
    private String imageUrl;
    private int sortOrder;

    public BannerItem(Integer dramaId, String title, String imageUrl, int sortOrder) {
        this.dramaId = dramaId;
        this.title = title;
        this.imageUrl = imageUrl;
        this.sortOrder = sortOrder;
    }

    public Integer getDramaId() { return dramaId; }
    public String getTitle() { return title; }
    public String getImageUrl() { return imageUrl; }
    public int getSortOrder() { return sortOrder; }
}
