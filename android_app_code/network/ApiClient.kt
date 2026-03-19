package com.example.contextassistant.network

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    // CRITICAL: 10.0.2.2 is the special IP for Android Emulator to connect to PC's localhost
    private const val BASE_URL = "http://10.0.2.2:5000/api/"

    val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create()) // Uses GSON to parse JSON
            .build()
    }

    val apiService: ApiService by lazy {
        retrofit.create(ApiService::class.java)
    }
}
