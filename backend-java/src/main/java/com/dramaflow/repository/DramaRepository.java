package com.dramaflow.repository;

import com.dramaflow.model.Drama;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DramaRepository extends JpaRepository<Drama, Integer> {
    Page<Drama> findByCategory_Slug(String categorySlug, Pageable pageable);
    List<Drama> findTop5ByOrderByRatingDesc();
}
