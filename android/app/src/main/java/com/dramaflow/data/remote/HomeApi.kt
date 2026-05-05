package com.dramaflow.data.remote

import retrofit2.Response
import retrofit2.http.*

interface HomeApi {

    @GET("dramas")
    suspend fun listDramas(
        @Query("category") category: String? = null,
        @Query("page") page: Int = 1,
        @Query("size") size: Int = 20,
    ): Response<PaginatedDramas>

    @GET("dramas/{id}")
    suspend fun getDramaDetail(@Path("id") id: Int): Response<DramaDetail>

    @GET("banners")
    suspend fun getBanners(): Response<List<BannerItem>>

    @GET("categories")
    suspend fun getCategories(): Response<List<CategoryItem>>

    @GET("dramas/{dramaId}/episodes")
    suspend fun listEpisodes(@Path("dramaId") dramaId: Int): Response<List<EpisodeItem>>

    @GET("episodes/{episodeId}/video-url")
    suspend fun getVideoUrl(@Path("episodeId") episodeId: Int): Response<VideoUrlResponse>
}

data class PaginatedDramas(val items: List<DramaItem>, val total: Int, val page: Int, val size: Int)
data class DramaItem(val id: Int, val title: String, val rating: Double, val episode_count: Int)
data class DramaDetail(val id: Int, val title: String, val description: String, val rating: Double, val episode_count: Int)
data class BannerItem(val drama_id: Int, val title: String, val image_url: String)
data class CategoryItem(val id: Int, val name: String, val slug: String)
data class EpisodeItem(val id: Int, val episode_number: Int, val title: String, val duration: String, val video_url: String = "")
data class VideoUrlResponse(val url: String, val expires_at: String)
