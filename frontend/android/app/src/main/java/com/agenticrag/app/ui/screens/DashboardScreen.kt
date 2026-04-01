package com.agenticrag.app.ui.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.agenticrag.app.ui.viewmodel.DashboardViewModel
import com.agenticrag.app.ui.viewmodel.UploadState
import java.io.File
import java.io.FileOutputStream

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    token: String,
    dashboardViewModel: DashboardViewModel,
    onNavigateToChat: () -> Unit,
    onLogout: () -> Unit
) {
    val uploadState by dashboardViewModel.uploadState.collectAsState()
    val context = LocalContext.current

    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        if (uri != null) {
            val contentResolver = context.contentResolver
            val inputStream = contentResolver.openInputStream(uri)
            val tempFile = File(context.cacheDir, "upload_document.pdf")
            inputStream?.use { input ->
                FileOutputStream(tempFile).use { output ->
                    input.copyTo(output)
                }
            }
            dashboardViewModel.uploadDocument(token, tempFile)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Dashboard") },
                actions = {
                    IconButton(onClick = onLogout) {
                        Text("Log Out")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("Welcome to AgenticRAG", style = MaterialTheme.typography.headlineMedium)
            Spacer(modifier = Modifier.height(32.dp))

            Button(onClick = { filePickerLauncher.launch("*/*") }) {
                Text("Upload Document")
            }
            Spacer(modifier = Modifier.height(16.dp))

            when (uploadState) {
                is UploadState.Uploading -> CircularProgressIndicator()
                is UploadState.Success -> {
                    Text("Upload Successful!", color = MaterialTheme.colorScheme.primary)
                    LaunchedEffect(Unit) { dashboardViewModel.resetUploadState() }
                }
                is UploadState.Error -> {
                    Text("Error: ${(uploadState as UploadState.Error).message}", color = MaterialTheme.colorScheme.error)
                }
                else -> {}
            }

            Spacer(modifier = Modifier.height(32.dp))

            Button(onClick = onNavigateToChat) {
                Text("Go to Chat")
            }
        }
    }
}
