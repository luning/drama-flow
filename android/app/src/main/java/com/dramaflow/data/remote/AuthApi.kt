package com.dramaflow.data.remote

import com.dramaflow.data.remote.model.*
import retrofit2.Response
import retrofit2.http.*

interface AuthApi {

    @POST("auth/register")
    suspend fun register(@Body body: RegisterRequest): Response<UserResponse>

    @POST("auth/login")
    suspend fun login(@Body body: LoginRequest): Response<TokenResponse>

    @POST("auth/logout")
    suspend fun logout(): Response<Unit>

    @POST("auth/refresh")
    suspend fun refresh(@Body body: RefreshRequest): Response<TokenResponse>
}

data class RegisterRequest(val nickname: String, val email: String, val password: String)
data class LoginRequest(val email: String, val password: String)
data class RefreshRequest(val refresh_token: String)
data class TokenResponse(val access_token: String, val refresh_token: String, val user: UserResponse)
data class UserResponse(val id: Int, val nickname: String, val email: String)
