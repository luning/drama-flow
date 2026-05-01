package com.dramaflow.service;

import com.dramaflow.dto.*;
import com.dramaflow.model.Category;
import com.dramaflow.model.Drama;
import com.dramaflow.repository.CategoryRepository;
import com.dramaflow.repository.DramaRepository;
import com.dramaflow.repository.EpisodeRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class DramaService {

    private final DramaRepository dramaRepository;
    private final CategoryRepository categoryRepository;
    private final EpisodeRepository episodeRepository;

    public DramaService(DramaRepository dramaRepository,
                        CategoryRepository categoryRepository,
                        EpisodeRepository episodeRepository) {
        this.dramaRepository = dramaRepository;
        this.categoryRepository = categoryRepository;
        this.episodeRepository = episodeRepository;
    }

    public PageResult<DramaListItem> listDramas(String category, int page, int size) {
        Page<Drama> dramaPage;
        if (category != null && !category.isBlank() && !category.equals("all")) {
            dramaPage = dramaRepository.findByCategory_Slug(category, PageRequest.of(page - 1, size, Sort.by(Sort.Direction.DESC, "updatedAt")));
        } else {
            dramaPage = dramaRepository.findAll(PageRequest.of(page - 1, size, Sort.by(Sort.Direction.DESC, "updatedAt")));
        }

        List<DramaListItem> items = dramaPage.getContent().stream()
                .map(d -> new DramaListItem(
                        d.getId(), d.getTitle(),
                        d.getCategory() != null ? d.getCategory().getId() : null,
                        d.getRating(), d.getCoverUrl(), d.getYear(), d.getStatus(),
                        episodeRepository.countByDramaId(d.getId())))
                .collect(Collectors.toList());

        return new PageResult<>(items, dramaPage.getTotalElements(), page, size);
    }

    public DramaDetail getDramaDetail(Integer dramaId) {
        Drama d = dramaRepository.findById(dramaId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "剧集不存在"));

        long epCount = episodeRepository.countByDramaId(d.getId());
        return new DramaDetail(
                d.getId(), d.getTitle(), d.getDescription(),
                d.getCategory() != null ? d.getCategory().getId() : null,
                d.getCategory() != null ? d.getCategory().getName() : "",
                d.getRating(), d.getCoverUrl(), d.getYear(), d.getStatus(),
                epCount, d.getCreatedAt());
    }

    public List<CategoryItem> listCategories() {
        return categoryRepository.findAllByOrderBySortOrder().stream()
                .map(c -> new CategoryItem(c.getId(), c.getName(), c.getSlug(), c.getSortOrder()))
                .collect(Collectors.toList());
    }

    public List<BannerItem> listBanners() {
        List<Drama> top = dramaRepository.findTop5ByOrderByRatingDesc();
        int[] i = {0};
        return top.stream()
                .map(d -> new BannerItem(d.getId(), d.getTitle(), d.getCoverUrl(), i[0]++))
                .collect(Collectors.toList());
    }
}
