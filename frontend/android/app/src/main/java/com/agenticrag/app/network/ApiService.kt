package com.agenticrag.app.network

import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.*

data class LoginRequest(val username: String, val password: String)
data class LoginResponse(val access_token: String, val token_type: String)

data class ChatHistoryItem(val id: Int, val query: String, val response: String)

data class FeedbackRequest(val messageId: String, val score: Int) // score: 1 (up), -1 (down)
data class FeedbackResponse(val status: String)

interface ApiService {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @POST("auth/signup")
    suspend fun signup(@Body request: LoginRequest): Response<LoginResponse>

    @Multipart
    @POST("upload")
    suspend fun uploadDocument(
        @Header("Authorization") token: String,
        @Part file: MultipartBody.Part
    ): Response<Map<String, Any>>

    @GET("history")
    suspend fun getHistory(@Header("Authorization") token: String): Response<List<ChatHistoryItem>>

    @POST("feedback")
    suspend fun submitFeedback(
        @Header("Authorization") token: String,
        @Body request: FeedbackRequest
    ): Response<FeedbackResponse>
}
