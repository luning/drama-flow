package com.dramaflow.data.remote

import com.dramaflow.BuildConfig
import com.dramaflow.data.local.PreferencesManager
import com.dramaflow.DramaFlowApp
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import okhttp3.Authenticator
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import okhttp3.Route
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * Global session expiry signal.
 * Authenticator emits on refresh failure; MainActivity observes and navigates to login.
 * Thread-safe: MutableSharedFlow.tryEmit is lock-free and can be called from any thread.
 */
object SessionManager {
    private val _sessionExpired = MutableSharedFlow<Unit>(extraBufferCapacity = 1, replay = 0)
    val sessionExpired: SharedFlow<Unit> = _sessionExpired.asSharedFlow()

    fun notifySessionExpired() {
        _sessionExpired.tryEmit(Unit)
    }
}

/**
 * Unified token access layer.
 * Readers get in-memory token first, fall back to EncryptedSharedPreferences.
 * Writers control persistence via `persist` flag (for remember-me).
 *
 * Thread safety: memoryAccessToken and memoryRefreshToken are @Volatile,
 * making reads visible across OkHttp's background threads and coroutine dispatchers.
 */
object TokenProvider {
    @Volatile
    private var memoryAccessToken: String? = null
    @Volatile
    private var memoryRefreshToken: String? = null

    fun getAccessToken(prefs: PreferencesManager): String? {
        return memoryAccessToken ?: prefs.accessToken
    }

    fun getRefreshToken(prefs: PreferencesManager): String? {
        return memoryRefreshToken ?: prefs.refreshToken
    }

    fun setTokens(access: String, refresh: String, persist: Boolean, prefs: PreferencesManager) {
        memoryAccessToken = access
        memoryRefreshToken = refresh
        if (persist) {
            prefs.accessToken = access
            prefs.refreshToken = refresh
        }
    }

    fun clear() {
        memoryAccessToken = null
        memoryRefreshToken = null
    }
}

object ApiClient {

    private val moshi = Moshi.Builder()
        .addLast(KotlinJsonAdapterFactory())
        .build()

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
                else HttpLoggingInterceptor.Level.NONE
    }

    /**
     * 自动注入 Authorization header，统一管理 Token。
     * 所有 API 请求通过此 Interceptor 注入 Token，无需在每个 Repository 中手动添加。
     */
    private val authInterceptor = Interceptor { chain ->
        val original = chain.request()
        val prefs = PreferencesManager(DramaFlowApp.instance)
        val token = TokenProvider.getAccessToken(prefs)

        val request = if (token != null) {
            original.newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
        } else {
            original
        }

        chain.proceed(request)
    }

    private val lock = Any()

    /**
     * OkHttp Authenticator that intercepts 401 responses and attempts token refresh.
     *
     * Flow:
     * 1. Skip if the failed request was to auth/refresh (prevent recursion)
     * 2. Read refresh_token from TokenProvider
     * 3. Synchronized block to prevent thundering herd on concurrent 401s:
     *    a. Re-check refresh_token (another thread may have already refreshed)
     *    b. Call POST /api/auth/refresh synchronously
     *    c. On success: store new tokens via TokenProvider, retry original request with new access_token
     *    d. On failure: clear session, emit SessionExpired signal, return null (give up)
     *
     * OkHttp calls Authenticator from a background thread pool, so blocking is safe here.
     */
    private val authenticator = Authenticator { route: Route?, response: Response ->
        // ---- Guard 1: Never retry the refresh endpoint itself ----
        val requestPath = response.request.url.encodedPath
        if (requestPath.contains("auth/refresh")) {
            return@Authenticator null
        }

        // ---- Guard 2: Only handle 401 for requests that had Bearer auth ----
        val failedToken = response.request.header("Authorization")
        if (failedToken == null || !failedToken.startsWith("Bearer ")) {
            return@Authenticator null
        }

        val prefs = PreferencesManager(DramaFlowApp.instance)
        val originalRefreshToken = TokenProvider.getRefreshToken(prefs)
            ?: return@Authenticator null

        synchronized(lock) {
            // ---- Guard 3: Check if another thread already refreshed ----
            val currentRefreshToken = TokenProvider.getRefreshToken(prefs)
            if (currentRefreshToken != originalRefreshToken) {
                // Token already updated by another thread — retry with new access token
                val newAccessToken = TokenProvider.getAccessToken(prefs)
                    ?: return@Authenticator null
                return@Authenticator response.request.newBuilder()
                    .header("Authorization", "Bearer $newAccessToken")
                    .build()
            }

            // ---- Build and execute refresh request synchronously ----
            try {
                val refreshBody = JSONObject().apply {
                    put("refresh_token", currentRefreshToken)
                }.toString()

                val refreshRequest = Request.Builder()
                    .url("${BuildConfig.API_BASE_URL}auth/refresh")
                    .post(refreshBody.toRequestBody("application/json".toMediaType()))
                    .build()

                // Use a minimal OkHttpClient for the refresh call (no interceptors/authenticator)
                val refreshClient = OkHttpClient.Builder()
                    .connectTimeout(15, TimeUnit.SECONDS)
                    .readTimeout(15, TimeUnit.SECONDS)
                    .build()

                val refreshResponse = refreshClient.newCall(refreshRequest).execute()

                if (refreshResponse.isSuccessful) {
                    // ---- Success: parse response, store new tokens, retry ----
                    val bodyString = refreshResponse.body?.string() ?: return@Authenticator null
                    val json = JSONObject(bodyString)
                    val newAccessToken = json.getString("access_token")
                    val newRefreshToken = json.getString("refresh_token")

                    TokenProvider.setTokens(
                        access = newAccessToken,
                        refresh = newRefreshToken,
                        persist = true,
                        prefs = prefs
                    )

                    return@Authenticator response.request.newBuilder()
                        .header("Authorization", "Bearer $newAccessToken")
                        .build()
                } else {
                    // ---- Failure: clear session, signal UI, give up ----
                    TokenProvider.clear()
                    prefs.clearSession()
                    SessionManager.notifySessionExpired()
                    return@Authenticator null
                }
            } catch (e: Exception) {
                // Network error or parse error: clear session, signal UI, give up
                TokenProvider.clear()
                prefs.clearSession()
                SessionManager.notifySessionExpired()
                return@Authenticator null
            }
        }
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .addInterceptor(loggingInterceptor)
        .addInterceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("Content-Type", "application/json")
                .build()
            chain.proceed(request)
        }
        .authenticator(authenticator)
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.API_BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(MoshiConverterFactory.create(moshi))
        .build()

    inline fun <reified T> create(): T = retrofit.create(T::class.java)
}
