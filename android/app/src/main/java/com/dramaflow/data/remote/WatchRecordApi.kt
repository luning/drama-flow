package com.dramaflow.data.remote

import retrofit2.Response
import retrofit2.http.*

interface WatchRecordApi {

    @PUT("watch-records/{episodeId}")
    suspend fun upsertRecord(
        @Path("episodeId") episodeId: Int,
        @Body body: WatchRecordBody,
    ): Response<WatchRecordResponse>

    @GET("watch-records/{episodeId}")
    suspend fun getRecord(@Path("episodeId") episodeId: Int): Response<WatchRecordResponse>

    @GET("watch-records/continue-watching")
    suspend fun continueWatching(): Response<List<ContinueWatchingItem>>
}

data class WatchRecordBody(val progress: Double, val last_position: Double, val completed: Boolean)
data class WatchRecordResponse(val id: Int, val progress: Double, val last_position: Double, val completed: Boolean)
data class ContinueWatchingItem(val drama_title: String, val episode_title: String, val progress: Double)
