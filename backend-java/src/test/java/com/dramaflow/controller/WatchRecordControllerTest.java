package com.dramaflow.controller;

import com.jayway.jsonpath.DocumentContext;
import com.jayway.jsonpath.JsonPath;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class WatchRecordControllerTest {

    @Autowired
    private TestRestTemplate restTemplate;

    private String uniqueEmail() {
        return "wr_" + System.nanoTime() + "@test.com";
    }

    private AuthSession registerAndLogin() {
        String email = uniqueEmail();
        restTemplate.postForEntity("/api/auth/register",
                Map.of("nickname", "WatchUser", "email", email, "password", "Test1234"),
                String.class);
        ResponseEntity<String> loginResp = restTemplate.postForEntity("/api/auth/login",
                Map.of("email", email, "password", "Test1234"),
                String.class);
        DocumentContext doc = JsonPath.parse(loginResp.getBody());
        String accessToken = doc.read("$.access_token", String.class);
        Integer userId = doc.read("$.user.id", Integer.class);
        return new AuthSession(accessToken, userId);
    }

    private HttpEntity<Map<String, Object>> authEntity(Map<String, Object> body, String token) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(token);
        return new HttpEntity<>(body, headers);
    }

    private HttpEntity<Void> authEntity(String token) {
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        return new HttpEntity<>(headers);
    }

    record AuthSession(String accessToken, Integer userId) {}

    // --- Upsert ---

    @Test
    void upsertRecord_Create_ShouldReturn200() {
        AuthSession session = registerAndLogin();
        Map<String, Object> body = new HashMap<>();
        body.put("progress", 50.0);
        body.put("last_position", 120.5);
        body.put("completed", false);

        ResponseEntity<String> resp = restTemplate.exchange(
                "/api/watch-records/1",
                HttpMethod.PUT,
                authEntity(body, session.accessToken),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.id", Integer.class)).isPositive();
        assertThat(doc.read("$.user_id", Integer.class)).isEqualTo(session.userId);
        assertThat(doc.read("$.episode_id", Integer.class)).isEqualTo(1);
        assertThat(doc.read("$.progress", Double.class)).isEqualTo(50.0);
        assertThat(doc.read("$.last_position", Double.class)).isEqualTo(120.5);
        assertThat(doc.read("$.completed", Boolean.class)).isFalse();
        assertThat(doc.read("$.updated_at", String.class)).isNotBlank();
    }

    @Test
    void upsertRecord_Update_ShouldReturnUpdatedValues() {
        AuthSession session = registerAndLogin();

        // Create initial record
        Map<String, Object> createBody = new HashMap<>();
        createBody.put("progress", 30.0);
        createBody.put("last_position", 60.0);
        createBody.put("completed", false);
        restTemplate.exchange("/api/watch-records/1", HttpMethod.PUT,
                authEntity(createBody, session.accessToken), String.class);

        // Update record
        Map<String, Object> updateBody = new HashMap<>();
        updateBody.put("progress", 100.0);
        updateBody.put("last_position", 300.0);
        updateBody.put("completed", true);

        ResponseEntity<String> resp = restTemplate.exchange(
                "/api/watch-records/1",
                HttpMethod.PUT,
                authEntity(updateBody, session.accessToken),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.progress", Double.class)).isEqualTo(100.0);
        assertThat(doc.read("$.last_position", Double.class)).isEqualTo(300.0);
        assertThat(doc.read("$.completed", Boolean.class)).isTrue();
    }

    // --- Get Record ---

    @Test
    void getRecord_Existing_ShouldReturn200() {
        AuthSession session = registerAndLogin();

        // Create a record first
        Map<String, Object> createBody = new HashMap<>();
        createBody.put("progress", 75.0);
        createBody.put("last_position", 200.0);
        createBody.put("completed", false);
        restTemplate.exchange("/api/watch-records/1", HttpMethod.PUT,
                authEntity(createBody, session.accessToken), String.class);

        ResponseEntity<String> resp = restTemplate.exchange(
                "/api/watch-records/1",
                HttpMethod.GET,
                authEntity(session.accessToken),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.user_id", Integer.class)).isEqualTo(session.userId);
        assertThat(doc.read("$.progress", Double.class)).isEqualTo(75.0);
    }

    @Test
    void getRecord_NoRecord_ShouldReturn200WithDefaultValues() {
        AuthSession session = registerAndLogin();

        ResponseEntity<String> resp = restTemplate.exchange(
                "/api/watch-records/999",
                HttpMethod.GET,
                authEntity(session.accessToken),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        Object id = doc.read("$.id");
        assertThat(id).isNull();
        assertThat(doc.read("$.user_id", Integer.class)).isEqualTo(session.userId);
        assertThat(doc.read("$.episode_id", Integer.class)).isEqualTo(999);
        assertThat(doc.read("$.progress", Double.class)).isEqualTo(0.0);
        assertThat(doc.read("$.completed", Boolean.class)).isFalse();
    }

    // --- List Records ---

    @Test
    void listRecords_ShouldReturnPageResult() {
        AuthSession session = registerAndLogin();

        // Create multiple records
        for (int epId = 1; epId <= 3; epId++) {
            Map<String, Object> body = new HashMap<>();
            body.put("progress", epId * 10.0);
            body.put("last_position", epId * 50.0);
            body.put("completed", false);
            restTemplate.exchange("/api/watch-records/" + epId, HttpMethod.PUT,
                    authEntity(body, session.accessToken), String.class);
        }

        ResponseEntity<String> resp = restTemplate.exchange(
                "/api/watch-records?page=1&size=20",
                HttpMethod.GET,
                authEntity(session.accessToken),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.total", Integer.class)).isEqualTo(3);
        assertThat(doc.read("$.page", Integer.class)).isEqualTo(1);
        assertThat(doc.read("$.size", Integer.class)).isEqualTo(20);
        assertThat((List<?>) doc.read("$.items")).hasSize(3);
    }

    // --- Continue Watching ---

    @Test
    void continueWatching_ShouldReturnIncompleteRecords() {
        AuthSession session = registerAndLogin();

        // Create completed record for ep1
        Map<String, Object> completedBody = new HashMap<>();
        completedBody.put("progress", 100.0);
        completedBody.put("last_position", 500.0);
        completedBody.put("completed", true);
        restTemplate.exchange("/api/watch-records/1", HttpMethod.PUT,
                authEntity(completedBody, session.accessToken), String.class);

        // Create incomplete record for ep2 (should appear in continue-watching)
        Map<String, Object> incompleteBody = new HashMap<>();
        incompleteBody.put("progress", 45.0);
        incompleteBody.put("last_position", 120.0);
        incompleteBody.put("completed", false);
        restTemplate.exchange("/api/watch-records/2", HttpMethod.PUT,
                authEntity(incompleteBody, session.accessToken), String.class);

        ResponseEntity<String> resp = restTemplate.exchange(
                "/api/watch-records/continue-watching",
                HttpMethod.GET,
                authEntity(session.accessToken),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat((List<?>) doc.read("$")).isNotEmpty();

        // Verify structure of continue-watching item
        Integer dramaId = doc.read("$[0].drama_id", Integer.class);
        String dramaTitle = doc.read("$[0].drama_title", String.class);
        Integer episodeId = doc.read("$[0].episode_id", Integer.class);
        Integer episodeNumber = doc.read("$[0].episode_number", Integer.class);
        double progress = doc.read("$[0].progress", Double.class);
        assertThat(dramaId).isPositive();
        assertThat(dramaTitle).isNotBlank();
        assertThat(episodeId).isPositive();
        assertThat(episodeNumber).isPositive();
        assertThat(progress).isPositive();
    }

    // --- Unauthenticated Access ---

    @Test
    void watchRecordEndpoints_WithoutAuth_ShouldReturn4xx() {
        ResponseEntity<String> getResp = restTemplate.getForEntity("/api/watch-records/1", String.class);
        assertThat(getResp.getStatusCode().is4xxClientError()).isTrue();

        ResponseEntity<String> listResp = restTemplate.getForEntity("/api/watch-records", String.class);
        assertThat(listResp.getStatusCode().is4xxClientError()).isTrue();

        ResponseEntity<String> continueResp = restTemplate.getForEntity("/api/watch-records/continue-watching", String.class);
        assertThat(continueResp.getStatusCode().is4xxClientError()).isTrue();
    }
}
