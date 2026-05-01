package com.dramaflow.repository;

import com.dramaflow.model.WatchRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface WatchRecordRepository extends JpaRepository<WatchRecord, Integer> {
    Optional<WatchRecord> findByUserIdAndEpisodeId(Integer userId, Integer episodeId);
    Page<WatchRecord> findByUserIdOrderByUpdatedAtDesc(Integer userId, Pageable pageable);
    List<WatchRecord> findTop5ByUserIdAndCompletedFalseOrderByUpdatedAtDesc(Integer userId);
}
