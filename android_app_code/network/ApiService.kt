package com.example.contextassistant.network

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Header

// Data Model safely mapping our Flask JSON Response
data class ContextResponse(
    val status: String,
    val alert: String,
    val suggestion: String
)

interface ApiService {
    // Phase 4 Context Engine Endpoint
    @GET("context/status")
    suspend fun getContextStatus(
        @Header("Authorization") token: String
    ): Response<ContextResponse>
}
