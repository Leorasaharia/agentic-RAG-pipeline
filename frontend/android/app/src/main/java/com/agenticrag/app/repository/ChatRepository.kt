package com.agenticrag.app.repository

import com.agenticrag.app.network.ChatHistoryItem
import com.agenticrag.app.network.FeedbackRequest
import com.agenticrag.app.network.RetrofitInstance

class ChatRepository {
    private val api = RetrofitInstance.api

    suspend fun getHistory(token: String): Result<List<ChatHistoryItem>> {
        return try {
            val response = api.getHistory("Bearer $token")
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.message()))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun sendFeedback(token: String, messageId: String, score: Int): Result<String> {
        return try {
            val response = api.submitFeedback("Bearer $token", FeedbackRequest(messageId, score))
            if (response.isSuccessful) {
                Result.success("Feedback submitted successfully")
            } else {
                Result.failure(Exception(response.message()))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
