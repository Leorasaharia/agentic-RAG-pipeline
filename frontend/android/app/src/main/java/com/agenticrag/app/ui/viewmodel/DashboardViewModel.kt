package com.agenticrag.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.agenticrag.app.repository.DocumentRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.io.File

class DashboardViewModel : ViewModel() {
    private val documentRepository = DocumentRepository()

    private val _uploadState = MutableStateFlow<UploadState>(UploadState.Idle)
    val uploadState: StateFlow<UploadState> = _uploadState

    fun uploadDocument(token: String, file: File) {
        viewModelScope.launch {
            _uploadState.value = UploadState.Uploading
            val result = documentRepository.uploadDocument(token, file)
            if (result.isSuccess) {
                _uploadState.value = UploadState.Success
            } else {
                _uploadState.value = UploadState.Error(result.exceptionOrNull()?.message ?: "Upload failed")
            }
        }
    }

    fun resetUploadState() {
        _uploadState.value = UploadState.Idle
    }
}

sealed class UploadState {
    object Idle : UploadState()
    object Uploading : UploadState()
    object Success : UploadState()
    data class Error(val message: String) : UploadState()
}
