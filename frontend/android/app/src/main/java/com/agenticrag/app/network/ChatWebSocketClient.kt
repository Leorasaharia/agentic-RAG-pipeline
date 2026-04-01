package com.agenticrag.app.network

import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okio.ByteString

class ChatWebSocketClient(
    private val client: OkHttpClient,
    private val baseUrl: String,
    private val onMessageReceived: (String) -> Unit,
    private val onClosed: () -> Unit,
    private val onFailure: (String) -> Unit
) {
    private var webSocket: WebSocket? = null

    fun connect(token: String) {
        val request = Request.Builder()
            .url("$baseUrl/ws/chat?token=$token")
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: okhttp3.Response) {
                // Connected
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                onMessageReceived(text)
            }

            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                onMessageReceived(bytes.utf8())
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                webSocket.close(1000, null)
                onClosed()
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: okhttp3.Response?) {
                onFailure(t.message ?: "Unknown socket error")
            }
        })
    }

    fun sendMessage(message: String) {
        webSocket?.send(message)
    }

    fun disconnect() {
        webSocket?.close(1000, "User disconnected")
        webSocket = null
    }
}
