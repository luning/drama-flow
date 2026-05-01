package com.dramaflow.dto;

public class CategoryItem {
    private Integer id;
    private String name;
    private String slug;
    private Integer sortOrder;

    public CategoryItem(Integer id, String name, String slug, Integer sortOrder) {
        this.id = id;
        this.name = name;
        this.slug = slug;
        this.sortOrder = sortOrder;
    }

    public Integer getId() { return id; }
    public String getName() { return name; }
    public String getSlug() { return slug; }
    public Integer getSortOrder() { return sortOrder; }
}
