package com.dramaflow.auth.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.dramaflow.data.local.PreferencesManager
import com.dramaflow.data.repository.AuthRepository
import com.dramaflow.DramaFlowApp
import kotlinx.coroutines.launch

sealed class AuthState {
    object Idle : AuthState()
    object Loading : AuthState()
    data class Success(val token: String) : AuthState()
    data class Error(val message: String) : AuthState()
}

class AuthViewModel : ViewModel() {

    private val prefs = PreferencesManager(DramaFlowApp.instance)
    private val repository = AuthRepository(prefs = prefs)

    private val _loginState = MutableLiveData<AuthState>(AuthState.Idle)
    val loginState: LiveData<AuthState> = _loginState

    private val _registerState = MutableLiveData<AuthState>(AuthState.Idle)
    val registerState: LiveData<AuthState> = _registerState

    fun login(email: String, password: String, remember: Boolean) {
        _loginState.value = AuthState.Loading
        viewModelScope.launch {
            try {
                val token = repository.login(email, password, remember)
                _loginState.value = AuthState.Success(token.access_token)
            } catch (e: Exception) {
                _loginState.value = AuthState.Error(e.message ?: "登录失败")
            }
        }
    }

    fun register(nickname: String, email: String, password: String) {
        _registerState.value = AuthState.Loading
        viewModelScope.launch {
            try {
                repository.register(nickname, email, password)
                _registerState.value = AuthState.Success("")
            } catch (e: Exception) {
                _registerState.value = AuthState.Error(e.message ?: "注册失败")
            }
        }
    }

    fun logout() {
        repository.logout()
        _loginState.value = AuthState.Idle
    }

    fun tryAutoLogin() {
        viewModelScope.launch {
            val token = repository.tryRestoreSession()
            if (token != null) {
                _loginState.value = AuthState.Success(token.access_token)
            }
        }
    }
}
