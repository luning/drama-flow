package com.dramaflow.data.repository

import com.dramaflow.data.local.PreferencesManager
import com.dramaflow.data.remote.AuthApi
import com.dramaflow.data.remote.ApiClient
import com.dramaflow.data.remote.RegisterRequest
import com.dramaflow.data.remote.LoginRequest
import com.dramaflow.data.remote.RefreshRequest
import com.dramaflow.data.remote.TokenProvider
import com.dramaflow.DramaFlowApp
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

        val token = resp.body() ?: throw Exception("登录成功但响应体为空")
        currentToken = token

        if (remember) {
            // Set isRemembered BEFORE token persistence to prevent inconsistent state on crash
            prefs.isRemembered = true
        }
        // 根据 remember 标记条件持久化 Token
        TokenProvider.setTokens(
            access = token.access_token,
            refresh = token.refresh_token,
            persist = remember,
            prefs = prefs
        )

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
        val token = resp.body() ?: return null
        TokenProvider.setTokens(
            access = token.access_token,
            refresh = token.refresh_token,
            persist = true,
            prefs = prefs
        )
        currentToken = token
        return token
    }

    fun logout() {
        currentToken = null
        TokenProvider.clear()
        prefs.clearSession()
    }

    fun getAccessToken(): String? {
        val prefs = PreferencesManager(DramaFlowApp.instance)
        return TokenProvider.getAccessToken(prefs) ?: currentToken?.access_token
    }
}
