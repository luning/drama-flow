package com.dramaflow.player.viewmodel

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.dramaflow.data.remote.ApiClient
import com.dramaflow.data.remote.WatchRecordApi
import com.dramaflow.data.remote.WatchRecordBody
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
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

// Player State Machine — AC-PLAYER-10~21
// States: IDLE, BUFFERING, READY, PLAYING, PAUSED, ENDED, ERROR
// Transitions:
//   AC-12: IDLE → BUFFERING → READY (initial prepare)
//   AC-13: READY → PLAYING (playWhenReady=true) / PAUSED (playWhenReady=false)
//   AC-14: PLAYING/PAUSED → BUFFERING → PLAYING/PAUSED (seek)
//   AC-15: PLAYING → ENDED (playback completes)
//   AC-16: PLAYING/PAUSED/BUFFERING → ERROR (playback error)
//   AC-17: ERROR → BUFFERING → READY (recover)
//   AC-18: PLAYING/PAUSED/ENDED/ERROR → IDLE (release)
//   AC-19: Speed changes do NOT affect state machine state
class PlayerViewModel : ViewModel() {

    private val api = ApiClient.create<WatchRecordApi>()

    private val _playerState = MutableLiveData(PlayerState.IDLE)
    val playerState: LiveData<PlayerState> = _playerState

    private val _currentSpeed = MutableLiveData(PlaybackSpeed.SPEED_1X)
    val currentSpeed: LiveData<PlaybackSpeed> = _currentSpeed

    private val _isFullscreen = MutableLiveData(false)
    val isFullscreen: LiveData<Boolean> = _isFullscreen

    private var progressReportJob: Job? = null
    private var currentEpisodeId: Int = 0
    private var lastReportedPosition: Long = 0
    private var lastReportedDuration: Long = 0

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

    // AC-PLAYER-17: recover triggers BUFFERING state; ExoPlayer reset handled in PlayerActivity observer
    fun recover() {
        setState(PlayerState.BUFFERING)
    }

    fun toggleFullscreen() {
        _isFullscreen.value = !(_isFullscreen.value ?: false)
    }

    fun startPeriodicReporting(episodeId: Int) {
        stopPeriodicReporting()
        currentEpisodeId = episodeId
        progressReportJob = viewModelScope.launch {
            while (isActive) {
                delay(15_000L)
                if (lastReportedDuration > 0 && currentEpisodeId > 0) {
                    reportProgress(currentEpisodeId, lastReportedPosition, lastReportedDuration)
                }
            }
        }
    }

    fun stopPeriodicReporting() {
        progressReportJob?.cancel()
        progressReportJob = null
    }

    fun updatePlaybackPosition(position: Long, duration: Long) {
        lastReportedPosition = position
        lastReportedDuration = duration
    }

    fun reportProgress(episodeId: Int, position: Long, duration: Long) {
        val progress = if (duration > 0) (position.toDouble() / duration * 100) else 0.0
        Log.d("PlayerViewModel", "reportProgress: ep=$episodeId pos=$position dur=$duration progress=$progress")
        kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.IO) {
            try {
                val response = api.upsertRecord(episodeId, WatchRecordBody(
                    progress = progress,
                    last_position = position.toDouble(),
                    completed = progress > 90,
                ))
                Log.d("PlayerViewModel", "reportProgress response: ${response.code()} ${response.message()}")
            } catch (e: Exception) {
                Log.e("PlayerViewModel", "reportProgress failed", e)
            }
        }
    }

    fun fetchLastPosition(episodeId: Int, onResult: (Long) -> Unit) {
        viewModelScope.launch {
            try {
                val response = api.getRecord(episodeId)
                Log.d("PlayerViewModel", "fetchLastPosition: status=${response.code()}, success=${response.isSuccessful}")
                if (response.isSuccessful) {
                    val body = response.body()
                    Log.d("PlayerViewModel", "fetchLastPosition: body=$body")
                    if (body != null && body.last_position > 0) {
                        Log.d("PlayerViewModel", "fetchLastPosition: seeking to ${body.last_position.toLong()}")
                        onResult(body.last_position.toLong())
                    } else {
                        Log.d("PlayerViewModel", "fetchLastPosition: no valid position (body=${body != null}, last_position=${body?.last_position})")
                    }
                } else {
                    Log.w("PlayerViewModel", "fetchLastPosition: failed with ${response.code()} ${response.message()}")
                }
            } catch (e: Exception) {
                Log.e("PlayerViewModel", "fetchLastPosition: exception", e)
            }
        }
    }
}
