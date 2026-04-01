package com.agenticrag.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.agenticrag.app.network.ChatHistoryItem
import com.agenticrag.app.network.ChatWebSocketClient
import com.agenticrag.app.network.RetrofitInstance
import com.agenticrag.app.repository.ChatRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ChatMessage(
    val id: String = java.util.UUID.randomUUID().toString(),
    val text: String,
    val isUser: Boolean,
    var isStreaming: Boolean = false,
    var isLoading: Boolean = false
)

class ChatViewModel : ViewModel() {
    private val chatRepository = ChatRepository()
    private var webSocketClient: ChatWebSocketClient? = null

    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages

    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected

    // Stores the current streaming message ID
    private var currentAssistantMsgId: String? = null

    fun connectWebSocket(token: String) {
        if (webSocketClient != null) return

        webSocketClient = ChatWebSocketClient(
            client = RetrofitInstance.client,
            baseUrl = RetrofitInstance.BASE_URL.replace("http://", "ws://").replace("https://", "wss://"),
            onMessageReceived = { text ->
                handleIncomingStreamToken(text)
            },
            onClosed = {
                _isConnected.value = false
            },
            onFailure = { error ->
                _isConnected.value = false
                appendSystemMessage("Connection error: $error")
            }
        )
        webSocketClient?.connect(token)
        _isConnected.value = true
    }

    fun sendMessage(query: String) {
        if (query.isBlank()) return
        
        // Add User Message
        _messages.update { current ->
            current + ChatMessage(text = query, isUser = true)
        }

        // Add Emtpy Assistant Message as Placeholder
        val assistantId = java.util.UUID.randomUUID().toString()
        currentAssistantMsgId = assistantId
        _messages.update { current ->
            current + ChatMessage(id = assistantId, text = "", isUser = false, isStreaming = true, isLoading = true)
        }

        webSocketClient?.sendMessage(query)
    }

    private fun handleIncomingStreamToken(token: String) {
        val msgId = currentAssistantMsgId ?: return
        _messages.update { currentList ->
            currentList.map { msg ->
                if (msg.id == msgId) {
                    msg.copy(
                        text = msg.text + token,
                        isLoading = false
                    )
                } else msg
            }
        }
        
        // Usually, the backend will send a specific token to indicate completion, e.g., "[DONE]"
        if (token.contains("[DONE]")) {
            _messages.update { currentList ->
                currentList.map { msg ->
                    if (msg.id == msgId) {
                        msg.copy(
                            text = msg.text.replace("[DONE]", "").trim(),
                            isStreaming = false
                        )
                    } else msg
                }
            }
            currentAssistantMsgId = null
        }
    }

    fun loadHistory(token: String) {
        viewModelScope.launch {
            val result = chatRepository.getHistory(token)
            if (result.isSuccess) {
                val history = result.getOrNull() ?: emptyList()
                val mappedMessages = mutableListOf<ChatMessage>()
                for (item in history) {
                    mappedMessages.add(ChatMessage(id = item.id.toString(), text = item.query, isUser = true))
                    mappedMessages.add(ChatMessage(id = item.id.toString() + "_bot", text = item.response, isUser = false))
                }
                _messages.value = mappedMessages
            }
        }
    }

    fun submitFeedback(token: String, messageId: String, score: Int) {
        viewModelScope.launch {
            chatRepository.sendFeedback(token, messageId, score)
        }
    }

    private fun appendSystemMessage(text: String) {
        _messages.update { current ->
            current + ChatMessage(text = text, isUser = false, isStreaming = false)
        }
    }

    override fun onCleared() {
        super.onCleared()
        webSocketClient?.disconnect()
    }
}
