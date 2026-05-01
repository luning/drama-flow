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
class DramaControllerTest {

    @Autowired
    private TestRestTemplate restTemplate;

    // --- List Dramas ---

    @Test
    void listDramas_Default_ShouldReturn200WithSeedData() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/dramas", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.total", Integer.class)).isEqualTo(5);
        assertThat(doc.read("$.page", Integer.class)).isEqualTo(1);
        assertThat(doc.read("$.size", Integer.class)).isEqualTo(20);
        assertThat((List<?>) doc.read("$.items")).hasSize(5);

        // Verify drama structure
        Integer id = doc.read("$.items[0].id", Integer.class);
        String title = doc.read("$.items[0].title", String.class);
        Integer categoryId = doc.read("$.items[0].category_id", Integer.class);
        Double rating = doc.read("$.items[0].rating", Double.class);
        String coverUrl = doc.read("$.items[0].cover_url", String.class);
        String status = doc.read("$.items[0].status", String.class);
        Integer episodeCount = doc.read("$.items[0].episode_count", Integer.class);
        assertThat(id).isPositive();
        assertThat(title).isNotBlank();
        assertThat(categoryId).isPositive();
        assertThat(rating).isPositive();
        assertThat(coverUrl).isNotBlank();
        assertThat(status).isIn("ongoing", "completed");
        assertThat(episodeCount).isEqualTo(10);
    }

    @Test
    void listDramas_WithCategoryFilter_ShouldReturnFiltered() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/dramas?category=fantasy", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.total", Integer.class)).isEqualTo(1);
        assertThat(doc.read("$.items[0].title", String.class)).isEqualTo("重生之女王归来");
    }

    @Test
    void listDramas_WithPagination_ShouldRespectPageSize() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/dramas?page=1&size=2", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.page", Integer.class)).isEqualTo(1);
        assertThat(doc.read("$.size", Integer.class)).isEqualTo(2);
        assertThat((List<?>) doc.read("$.items")).hasSize(2);
        assertThat(doc.read("$.total", Integer.class)).isEqualTo(5);
    }

    @Test
    void listDramas_InvalidCategory_ShouldReturnEmptyList() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/dramas?category=nonexistent", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.total", Integer.class)).isEqualTo(0);
        assertThat((List<?>) doc.read("$.items")).isEmpty();
    }

    // --- Drama Detail ---

    @Test
    void getDramaDetail_ExistingId_ShouldReturn200() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/dramas/1", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat(doc.read("$.id", Integer.class)).isEqualTo(1);
        assertThat(doc.read("$.title", String.class)).isNotBlank();
        assertThat(doc.read("$.description", String.class)).isNotBlank();
        assertThat(doc.read("$.category_id", Integer.class)).isPositive();
        assertThat(doc.read("$.category_name", String.class)).isNotBlank();
        assertThat(doc.read("$.rating", Double.class)).isPositive();
        assertThat(doc.read("$.cover_url", String.class)).isNotBlank();
        assertThat(doc.read("$.year", Integer.class)).isPositive();
        assertThat(doc.read("$.status", String.class)).isNotBlank();
        assertThat(doc.read("$.episode_count", Integer.class)).isEqualTo(10);
        assertThat(doc.read("$.created_at", String.class)).isNotBlank();
    }

    @Test
    void getDramaDetail_NonExistentId_ShouldReturn404() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/dramas/99999", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }

    // --- Categories ---

    @Test
    void listCategories_ShouldReturn200WithAllCategories() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/categories", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat((List<?>) doc.read("$")).hasSize(5);

        // Verify category structure
        assertThat(doc.read("$[0].id", Integer.class)).isPositive();
        assertThat(doc.read("$[0].name", String.class)).isNotBlank();
        assertThat(doc.read("$[0].slug", String.class)).isNotBlank();
        assertThat(doc.read("$[0].sort_order", Integer.class)).isNotNull();
    }

    // --- Banners ---

    @Test
    void listBanners_ShouldReturn200WithTopRated() {
        ResponseEntity<String> resp = restTemplate.getForEntity("/api/banners", String.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.OK);
        DocumentContext doc = JsonPath.parse(resp.getBody());
        assertThat((List<?>) doc.read("$")).hasSize(5);

        // Verify banner structure
        Integer dramaId = doc.read("$[0].drama_id", Integer.class);
        String title = doc.read("$[0].title", String.class);
        String imageUrl = doc.read("$[0].image_url", String.class);
        assertThat(dramaId).isPositive();
        assertThat(title).isNotBlank();
        assertThat(imageUrl).isNotBlank();
    }
}
