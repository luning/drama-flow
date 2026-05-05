package com.dramaflow.player.viewmodel

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.dramaflow.data.remote.ApiClient
import com.dramaflow.data.remote.WatchRecordApi
import com.dramaflow.data.remote.WatchRecordBody
import kotlinx.coroutines.launch

enum class PlaybackSpeed(val value: Float) {
    SPEED_0_5X(0.5f),
    SPEED_0_75X(0.75f),
    SPEED_1X(1.0f),
    SPEED_1_25X(1.25f),
    SPEED_1_5X(1.5f),
    SPEED_2X(2.0f),
}

enum class PlayerState {
    IDLE, BUFFERING, READY, PLAYING, PAUSED, ERROR, ENDED
}

class PlayerViewModel : ViewModel() {

    private val api = ApiClient.create<WatchRecordApi>()

    private val _playerState = MutableLiveData(PlayerState.IDLE)
    val playerState: LiveData<PlayerState> = _playerState

    private val _currentSpeed = MutableLiveData(PlaybackSpeed.SPEED_1X)
    val currentSpeed: LiveData<PlaybackSpeed> = _currentSpeed

    private val _isFullscreen = MutableLiveData(false)
    val isFullscreen: LiveData<Boolean> = _isFullscreen

    fun setState(state: PlayerState) {
        val previous = _playerState.value
        if (previous != state) {
            Log.d("PlayerStateMachine", "${previous} → ${state}")
            _playerState.value = state
        }
    }

    fun setSpeed(speed: PlaybackSpeed) {
        _currentSpeed.value = speed
    }

    fun recover() {
        setState(PlayerState.BUFFERING)
    }

    fun toggleFullscreen() {
        _isFullscreen.value = !(_isFullscreen.value ?: false)
    }

    fun reportProgress(episodeId: Int, position: Long, duration: Long) {
        val progress = if (duration > 0) (position.toDouble() / duration * 100) else 0.0
        viewModelScope.launch {
            try {
                api.upsertRecord(episodeId, WatchRecordBody(
                    progress = progress,
                    last_position = position.toDouble(),
                    completed = progress > 90,
                ))
            } catch (_: Exception) { }
        }
    }
}
