package com.agenticrag.app.repository

import com.agenticrag.app.network.LoginRequest
import com.agenticrag.app.network.RetrofitInstance

class AuthRepository {
    private val api = RetrofitInstance.api

    suspend fun login(username: String, password: String): Result<String> {
        return try {
            val response = api.login(LoginRequest(username, password))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.access_token)
            } else {
                Result.failure(Exception(response.message()))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun signup(username: String, password: String): Result<String> {
        return try {
            val response = api.signup(LoginRequest(username, password))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.access_token)
            } else {
                Result.failure(Exception(response.message()))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
