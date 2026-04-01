package com.agenticrag.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.ThumbDown
import androidx.compose.material.icons.filled.ThumbUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.agenticrag.app.ui.viewmodel.ChatMessage
import com.agenticrag.app.ui.viewmodel.ChatViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    token: String,
    chatViewModel: ChatViewModel,
    onNavigateBack: () -> Unit
) {
    val messages by chatViewModel.messages.collectAsState()
    val isConnected by chatViewModel.isConnected.collectAsState()
    var inputText by remember { mutableStateOf("") }

    LaunchedEffect(Unit) {
        chatViewModel.connectWebSocket(token)
        chatViewModel.loadHistory(token)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(if (isConnected) "Chat (Connected)" else "Chat (Disconnected)") },
                navigationIcon = {
                    Button(onClick = onNavigateBack, modifier = Modifier.padding(start = 8.dp)) {
                        Text("Back")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .padding(horizontal = 8.dp),
                reverseLayout = false
            ) {
                items(messages) { msg ->
                    MessageBubble(
                        message = msg,
                        onFeedback = { score -> chatViewModel.submitFeedback(token, msg.id, score) }
                    )
                }
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    modifier = Modifier.weight(1f),
                    placeholder = { Text("Ask something...") }
                )
                Spacer(modifier = Modifier.width(8.dp))
                IconButton(
                    onClick = {
                        chatViewModel.sendMessage(inputText)
                        inputText = ""
                    },
                    enabled = isConnected && inputText.isNotBlank()
                ) {
                    Icon(Icons.Default.Send, contentDescription = "Send")
                }
            }
        }
    }
}

@Composable
fun MessageBubble(message: ChatMessage, onFeedback: (Int) -> Unit) {
    val alignment = if (message.isUser) Alignment.CenterEnd else Alignment.CenterStart
    val bgColor = if (message.isUser) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalAlignment = alignment
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .background(bgColor, RoundedCornerShape(12.dp))
                    .padding(12.dp)
                    .widthIn(max = 280.dp)
            ) {
                if (message.isLoading) {
                    CircularProgressIndicator(modifier = Modifier.size(24.dp), strokeWidth = 2.dp)
                } else {
                    Text(text = message.text, color = MaterialTheme.colorScheme.onSurface)
                }
            }

            if (!message.isUser && !message.isStreaming && !message.isLoading) {
                Spacer(modifier = Modifier.width(4.dp))
                Column {
                    IconButton(onClick = { onFeedback(1) }, modifier = Modifier.size(24.dp)) {
                        Icon(Icons.Default.ThumbUp, contentDescription = "Thumbs Up", tint = Color.Gray)
                    }
                    IconButton(onClick = { onFeedback(-1) }, modifier = Modifier.size(24.dp)) {
                        Icon(Icons.Default.ThumbDown, contentDescription = "Thumbs Down", tint = Color.Gray)
                    }
                }
            }
        }
    }
}
