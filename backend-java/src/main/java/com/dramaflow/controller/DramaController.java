package com.dramaflow.controller;

import com.dramaflow.dto.PageResult;
import com.dramaflow.dto.DramaListItem;
import com.dramaflow.dto.DramaDetail;
import com.dramaflow.dto.BannerItem;
import com.dramaflow.dto.CategoryItem;
import com.dramaflow.service.DramaService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
public class DramaController {

    private final DramaService dramaService;

    public DramaController(DramaService dramaService) {
        this.dramaService = dramaService;
    }

    @GetMapping("/dramas")
    public PageResult<DramaListItem> listDramas(
            @RequestParam(required = false) String category,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        return dramaService.listDramas(category, page, size);
    }

    @GetMapping("/dramas/{dramaId}")
    public DramaDetail dramaDetail(@PathVariable Integer dramaId) {
        return dramaService.getDramaDetail(dramaId);
    }

    @GetMapping("/categories")
    public List<CategoryItem> categories() {
        return dramaService.listCategories();
    }

    @GetMapping("/banners")
    public List<BannerItem> banners() {
        return dramaService.listBanners();
    }
}
