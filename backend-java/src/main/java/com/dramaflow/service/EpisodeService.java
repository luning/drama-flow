package com.dramaflow.service;

import com.dramaflow.dto.EpisodeResponse;
import com.dramaflow.model.Episode;
import com.dramaflow.repository.EpisodeRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class EpisodeService {

    private final EpisodeRepository episodeRepository;

    public EpisodeService(EpisodeRepository episodeRepository) {
        this.episodeRepository = episodeRepository;
    }

    public List<EpisodeResponse> listEpisodes(Integer dramaId) {
        return episodeRepository.findByDrama_IdOrderByEpisodeNumber(dramaId).stream()
                .map(this::toResponse)
                .collect(Collectors.toList());
    }

    public EpisodeResponse getEpisode(Integer episodeId) {
        Episode ep = episodeRepository.findById(episodeId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "单集不存在"));
        return toResponse(ep);
    }

    private EpisodeResponse toResponse(Episode ep) {
        return new EpisodeResponse(
                ep.getId(), ep.getEpisodeNumber(), ep.getTitle(),
                ep.getDuration(), ep.getVideoUrl(), ep.getCreatedAt());
    }
}
