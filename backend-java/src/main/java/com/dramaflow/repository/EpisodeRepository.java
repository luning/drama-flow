package com.dramaflow.repository;

import com.dramaflow.model.Episode;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface EpisodeRepository extends JpaRepository<Episode, Integer> {
    List<Episode> findByDrama_IdOrderByEpisodeNumber(Integer dramaId);

    @Query("SELECT COUNT(e) FROM Episode e WHERE e.drama.id = :dramaId")
    long countByDramaId(@Param("dramaId") Integer dramaId);
}
