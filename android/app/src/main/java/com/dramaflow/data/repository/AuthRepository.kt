package com.dramaflow.data.repository

import com.dramaflow.data.local.PreferencesManager
import com.dramaflow.data.remote.AuthApi
import com.dramaflow.data.remote.ApiClient
import com.dramaflow.data.remote.RegisterRequest
import com.dramaflow.data.remote.LoginRequest
import com.dramaflow.data.remote.RefreshRequest
import com.dramaflow.data.remote.TokenResponse

class AuthRepository(
    private val api: AuthApi = ApiClient.create(),
    private val prefs: PreferencesManager,
) {
    private var currentToken: TokenResponse? = null

    suspend fun register(nickname: String, email: String, password: String) {
        val resp = api.register(RegisterRequest(nickname, email, password))
        if (!resp.isSuccessful) {
            val detail = resp.errorBody()?.string()?.let { body ->
                try {
                    org.json.JSONObject(body).optString("detail", "注册失败")
                } catch (_: Exception) { "注册失败" }
            } ?: "注册失败"
            throw Exception(detail)
        }
    }

    suspend fun login(email: String, password: String, remember: Boolean): TokenResponse {
        val resp = api.login(LoginRequest(email, password))
        if (!resp.isSuccessful) {
            val detail = resp.errorBody()?.string()?.let { body ->
                try {
                    org.json.JSONObject(body).optString("detail", "邮箱或密码错误")
                } catch (_: Exception) { "邮箱或密码错误" }
            } ?: "邮箱或密码错误"
            throw Exception(detail)
        }

        val token = resp.body()!!
        currentToken = token

        // 始终持久化 Token，AuthInterceptor 从 SharedPreferences 读取
        prefs.accessToken = token.access_token
        prefs.refreshToken = token.refresh_token
        if (remember) {
            prefs.isRemembered = true
        }

        return token
    }

    suspend fun tryRestoreSession(): TokenResponse? {
        if (!prefs.isRemembered) return null
        val refresh = prefs.refreshToken ?: return null
        val resp = api.refresh(RefreshRequest(refresh))
        if (!resp.isSuccessful) {
            prefs.clearSession()
            return null
        }
        val token = resp.body()!!
        prefs.accessToken = token.access_token
        prefs.refreshToken = token.refresh_token
        currentToken = token
        return token
    }

    fun logout() {
        currentToken = null
        prefs.clearSession()
    }

    fun getAccessToken(): String? = currentToken?.access_token ?: prefs.accessToken
}
