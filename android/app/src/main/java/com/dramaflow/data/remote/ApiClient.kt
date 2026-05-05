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
import java.util.concurrent.TimeUnit

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

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .addInterceptor(loggingInterceptor)
        .addInterceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("Content-Type", "application/json")
                .build()
            chain.proceed(request)
        }
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
