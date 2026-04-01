package com.agenticrag.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.agenticrag.app.ui.screens.ChatScreen
import com.agenticrag.app.ui.screens.DashboardScreen
import com.agenticrag.app.ui.screens.LoginScreen
import com.agenticrag.app.ui.viewmodel.AuthViewModel
import com.agenticrag.app.ui.viewmodel.ChatViewModel
import com.agenticrag.app.ui.viewmodel.DashboardViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val navController = rememberNavController()
            val authViewModel: AuthViewModel = viewModel()
            val dashboardViewModel: DashboardViewModel = viewModel()
            val chatViewModel: ChatViewModel = viewModel()

            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    NavHost(navController = navController, startDestination = "login") {
                        composable("login") {
                            LoginScreen(
                                authViewModel = authViewModel,
                                onLoginSuccess = {
                                    navController.navigate("dashboard") {
                                        popUpTo("login") { inclusive = true }
                                    }
                                }
                            )
                        }
                        composable("dashboard") {
                            val token = authViewModel.currentToken ?: return@composable
                            DashboardScreen(
                                token = token,
                                dashboardViewModel = dashboardViewModel,
                                onNavigateToChat = { navController.navigate("chat") },
                                onLogout = {
                                    authViewModel.logout()
                                    navController.navigate("login") {
                                        popUpTo("dashboard") { inclusive = true }
                                    }
                                }
                            )
                        }
                        composable("chat") {
                            val token = authViewModel.currentToken ?: return@composable
                            ChatScreen(
                                token = token,
                                chatViewModel = chatViewModel,
                                onNavigateBack = { navController.popBackStack() }
                            )
                        }
                    }
                }
            }
        }
    }
}
