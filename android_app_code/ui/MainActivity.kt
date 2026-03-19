package com.example.contextassistant.ui

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.NotificationCompat
import com.example.contextassistant.R
import com.example.contextassistant.network.ApiClient
import kotlinx.coroutines.*

class MainActivity : AppCompatActivity() {

    private lateinit var suggestionText: TextView
    private lateinit var refreshBtn: Button
    
    // Pro Tip: In a real app, you'd get this token from Login Logic (Phase 2), saved in SharedPreferences
    private val fakeToken = "Bearer YOUR_JWT_TOKEN_HERE" 

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        suggestionText = findViewById(R.id.suggestionText)
        refreshBtn = findViewById(R.id.refreshBtn)
        
        createNotificationChannel()

        refreshBtn.setOnClickListener {
            checkContextEngine()
        }
        
        // Initial Fetch
        checkContextEngine()
    }

    private fun checkContextEngine() {
        suggestionText.text = "Fetching from Python server..."
        
        // Execute network call on Background IO Thread using Coroutines (Prevents UI freezing)
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = ApiClient.apiService.getContextStatus(fakeToken)
                
                // Switch back to Main UI Thread to update the views
                withContext(Dispatchers.Main) {
                    if (response.isSuccessful) {
                        val body = response.body()
                        suggestionText.text = body?.suggestion ?: "No suggestion available"
                        
                        // Phase 4 context integration: Trigger Android push notification on burnout warning!
                        if (body?.alert == "long_session" || body?.alert == "check_in") {
                            sendNotification("Context Alert ⚠️", body.suggestion)
                        }
                    } else {
                        suggestionText.text = "Error: Invalid JWT Token or Server rejected"
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    suggestionText.text = "Failed to connect to Localhost. $e"
                    Log.e("API_ERROR", e.toString())
                }
            }
        }
    }

    private fun sendNotification(title: String, message: String) {
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val builder = NotificationCompat.Builder(this, "context_channel")
            .setSmallIcon(android.R.drawable.ic_dialog_info) // Default warning icon 
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_HIGH) // Shows Heads-up Notification

        manager.notify(1, builder.build())
    }

    private fun createNotificationChannel() {
        // Android 8.0+ strict requirement for channels
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "context_channel",
                "Context Alerts",
                NotificationManager.IMPORTANCE_HIGH
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }
}
