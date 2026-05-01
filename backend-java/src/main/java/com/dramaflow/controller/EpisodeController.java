package com.dramaflow.controller;

import com.dramaflow.dto.EpisodeResponse;
import com.dramaflow.service.EpisodeService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
public class EpisodeController {

    private final EpisodeService episodeService;

    public EpisodeController(EpisodeService episodeService) {
        this.episodeService = episodeService;
    }

    @GetMapping("/dramas/{dramaId}/episodes")
    public List<EpisodeResponse> listEpisodes(@PathVariable Integer dramaId) {
        return episodeService.listEpisodes(dramaId);
    }

    @GetMapping("/episodes/{episodeId}")
    public EpisodeResponse episodeDetail(@PathVariable Integer episodeId) {
        return episodeService.getEpisode(episodeId);
    }
}
