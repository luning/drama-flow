package com.dramaflow.controller;

import com.jayway.jsonpath.DocumentContext;
import com.jayway.jsonpath.JsonPath;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class EpisodeControllerTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void listEpisodes_ValidDramaId_ShouldReturn10Episodes() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/dramas/1/episodes", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat((List<?>) doc.read("$")).hasSize(10);

        // Verify episode structure
        Integer id = doc.read("$[0].id", Integer.class);
        Integer epNum = doc.read("$[0].episode_number", Integer.class);
        String title = doc.read("$[0].title", String.class);
        String duration = doc.read("$[0].duration", String.class);
        String videoUrl = doc.read("$[0].video_url", String.class);
        assertThat(id).isPositive();
        assertThat(epNum).isEqualTo(1);
        assertThat(title).isEqualTo("第1集");
        assertThat(duration).isNotBlank();
        assertThat(videoUrl).isNotBlank();
        assertThat(videoUrl).contains("/videos/");
    }

    @Test
    void listEpisodes_NonExistentDrama_ShouldReturnEmptyList() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/dramas/99999/episodes", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat((List<?>) doc.read("$")).isEmpty();
    }

    @Test
    void getEpisode_ValidId_ShouldReturn200() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/episodes/1", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        Integer id = doc.read("$.id", Integer.class);
        Integer epNum = doc.read("$.episode_number", Integer.class);
        String title = doc.read("$.title", String.class);
        String duration = doc.read("$.duration", String.class);
        String videoUrl = doc.read("$.video_url", String.class);
        assertThat(id).isEqualTo(1);
        assertThat(epNum).isEqualTo(1);
        assertThat(title).isEqualTo("第1集");
        assertThat(duration).isNotBlank();
        assertThat(videoUrl).isNotBlank();
        assertThat(doc.read("$.created_at", String.class)).isNotBlank();
    }

    @Test
    void getEpisode_NonExistentId_ShouldReturn404() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/episodes/99999", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }
}
