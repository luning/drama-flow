package com.dramaflow.service;

import com.dramaflow.dto.*;
import com.dramaflow.model.Drama;
import com.dramaflow.model.Episode;
import com.dramaflow.model.WatchRecord;
import com.dramaflow.repository.DramaRepository;
import com.dramaflow.repository.EpisodeRepository;
import com.dramaflow.repository.WatchRecordRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

import org.springframework.transaction.annotation.Transactional;
import java.util.ArrayList;
import java.util.List;

@Service
public class WatchRecordService {

    private final WatchRecordRepository watchRecordRepository;
    private final EpisodeRepository episodeRepository;
    private final DramaRepository dramaRepository;

    public WatchRecordService(WatchRecordRepository watchRecordRepository,
                              EpisodeRepository episodeRepository,
                              DramaRepository dramaRepository) {
        this.watchRecordRepository = watchRecordRepository;
        this.episodeRepository = episodeRepository;
        this.dramaRepository = dramaRepository;
    }

    public WatchRecordResponse upsertRecord(Integer userId, Integer episodeId, WatchRecordRequest data) {
        WatchRecord record = watchRecordRepository
                .findByUserIdAndEpisodeId(userId, episodeId)
                .orElse(new WatchRecord());

        record.setUserId(userId);
        record.setEpisodeId(episodeId);
        record.setProgress(data.getProgress());
        record.setLastPosition(data.getLastPosition());
        record.setCompleted(data.isCompleted());
        watchRecordRepository.save(record);

        return toResponse(record);
    }

    public WatchRecordResponse getRecord(Integer userId, Integer episodeId) {
        WatchRecord record = watchRecordRepository
                .findByUserIdAndEpisodeId(userId, episodeId)
                .orElse(null);
        if (record == null) {
            return new WatchRecordResponse(null, userId, episodeId, 0, 0, false, null);
        }
        return toResponse(record);
    }

    public PageResult<WatchRecordResponse> listRecords(Integer userId, int page, int size) {
        Page<WatchRecord> recordPage = watchRecordRepository
                .findByUserIdOrderByUpdatedAtDesc(userId, PageRequest.of(page - 1, size));

        List<WatchRecordResponse> items = recordPage.getContent().stream()
                .map(this::toResponse)
                .toList();

        return new PageResult<>(items, recordPage.getTotalElements(), page, size);
    }

    @Transactional(readOnly = true)
    public List<ContinueWatchingItem> continueWatching(Integer userId) {
        List<WatchRecord> records = watchRecordRepository
                .findTop5ByUserIdAndCompletedFalseOrderByUpdatedAtDesc(userId);

        List<ContinueWatchingItem> result = new ArrayList<>();
        for (WatchRecord r : records) {
            Episode ep = episodeRepository.findById(r.getEpisodeId()).orElse(null);
            if (ep == null) continue;
            Drama drama = ep.getDrama();
            if (drama == null) continue;

            result.add(new ContinueWatchingItem(
                    drama.getId(), drama.getTitle(), drama.getCoverUrl(),
                    ep.getId(), ep.getEpisodeNumber(), ep.getTitle(),
                    r.getProgress(), r.getLastPosition(), r.getUpdatedAt()));
        }
        return result;
    }

    private WatchRecordResponse toResponse(WatchRecord r) {
        return new WatchRecordResponse(
                r.getId(), r.getUserId(), r.getEpisodeId(),
                r.getProgress(), r.getLastPosition(),
                r.getCompleted(), r.getUpdatedAt());
    }
}
