package com.dramaflow.controller;

import com.jayway.jsonpath.DocumentContext;
import com.jayway.jsonpath.JsonPath;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.*;
import org.springframework.web.client.DefaultResponseErrorHandler;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class AuthControllerTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @BeforeEach
    void setUp() {
        // Use Apache HttpClient to avoid HttpURLConnection's broken auth challenge handling
        // (HttpURLConnection throws HttpRetryException on 401 with streamed POST bodies)
        restTemplate.getRestTemplate().setRequestFactory(new HttpComponentsClientHttpRequestFactory());
        restTemplate.getRestTemplate().setErrorHandler(new DefaultResponseErrorHandler() {
            @Override
            public boolean hasError(HttpStatusCode statusCode) {
                return false;
            }
        });
    }

    private String uniqueEmail() {
        return "auth_" + System.nanoTime() + "@test.com";
    }

    // --- Register ---

    @Test
    void register_ShouldReturn201() {
        String email = uniqueEmail();
        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/register",
                Map.of("nickname", "TestUser", "email", email, "password", "Test1234"),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.id", Integer.class)).isPositive();
        assertThat(doc.read("$.nickname", String.class)).isEqualTo("TestUser");
        assertThat(doc.read("$.email", String.class)).isEqualTo(email);
    }

    @Test
    void register_DuplicateEmail_ShouldReturn409() {
        String email = uniqueEmail();
        Map<String, String> body = Map.of("nickname", "User1", "email", email, "password", "Test1234");
        restTemplate.postForEntity("/api/auth/register", body, String.class);

        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/register", body, String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.CONFLICT);
        assertThat(JsonPath.parse(resp.getBody()).read("$.detail", String.class)).contains("邮箱已被注册");
    }

    @Test
    void register_InvalidEmail_ShouldReturn422() {
        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/register",
                Map.of("nickname", "TestUser", "email", "not-an-email", "password", "Test1234"),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.UNPROCESSABLE_ENTITY);
    }

    @Test
    void register_WeakPassword_WithoutDigit_ShouldReturn422() {
        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/register",
                Map.of("nickname", "TestUser", "email", uniqueEmail(), "password", "Password!"),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.UNPROCESSABLE_ENTITY);
    }

    @Test
    void register_WeakPassword_TooShort_ShouldReturn422() {
        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/register",
                Map.of("nickname", "TestUser", "email", uniqueEmail(), "password", "Ab1"),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.UNPROCESSABLE_ENTITY);
    }

    // --- Login ---

    @Test
    void login_ShouldReturn200WithTokens() {
        String email = uniqueEmail();
        restTemplate.postForEntity("/api/auth/register",
                Map.of("nickname", "TestUser", "email", email, "password", "Test1234"),
                String.class);

        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/login",
                Map.of("email", email, "password", "Test1234"),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.access_token", String.class)).isNotBlank();
        assertThat(doc.read("$.refresh_token", String.class)).isNotBlank();
        assertThat(doc.read("$.user.id", Integer.class)).isPositive();
        assertThat(doc.read("$.user.nickname", String.class)).isEqualTo("TestUser");
        assertThat(doc.read("$.user.email", String.class)).isEqualTo(email);
    }

    @Test
    void login_WrongPassword_ShouldReturn401() {
        String email = uniqueEmail();
        restTemplate.postForEntity("/api/auth/register",
                Map.of("nickname", "TestUser", "email", email, "password", "Test1234"),
                String.class);

        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/login",
                Map.of("email", email, "password", "WrongPass1"),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    void login_NonExistentEmail_ShouldReturn401() {
        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/login",
                Map.of("email", uniqueEmail(), "password", "Test1234"),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    // --- Logout ---

    @Test
    void logout_ShouldReturn200() {
        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/logout", null, String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(JsonPath.parse(resp.getBody()).read("$.message", String.class)).isEqualTo("已登出");
    }

    // --- Refresh ---

    @Test
    void refresh_ValidToken_ShouldReturn200() {
        String email = uniqueEmail();
        restTemplate.postForEntity("/api/auth/register",
                Map.of("nickname", "TestUser", "email", email, "password", "Test1234"),
                String.class);
        ResponseEntity<String> loginResp = restTemplate.postForEntity("/api/auth/login",
                Map.of("email", email, "password", "Test1234"),
                String.class);
        String refreshToken = JsonPath.parse(loginResp.getBody()).read("$.refresh_token", String.class);

        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/refresh",
                Map.of("refresh_token", refreshToken),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.access_token", String.class)).isNotBlank();
        assertThat(doc.read("$.refresh_token", String.class)).isNotBlank();
    }

    @Test
    void refresh_InvalidToken_ShouldReturn401() {
        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/refresh",
                Map.of("refresh_token", "invalid-token-value"),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    void refresh_AccessToken_ShouldReturn401() {
        String email = uniqueEmail();
        restTemplate.postForEntity("/api/auth/register",
                Map.of("nickname", "TestUser", "email", email, "password", "Test1234"),
                String.class);
        ResponseEntity<String> loginResp = restTemplate.postForEntity("/api/auth/login",
                Map.of("email", email, "password", "Test1234"),
                String.class);
        String accessToken = JsonPath.parse(loginResp.getBody()).read("$.access_token", String.class);

        ResponseEntity<String> resp = restTemplate.postForEntity("/api/auth/refresh",
                Map.of("refresh_token", accessToken),
                String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }
}
