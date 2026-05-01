package com.dramaflow.repository;

import com.dramaflow.model.Category;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface CategoryRepository extends JpaRepository<Category, Integer> {
    List<Category> findAllByOrderBySortOrder();
    Optional<Category> findBySlug(String slug);
}
