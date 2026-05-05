package com.dramaflow.player.viewmodel

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

class PlayerViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    // =====================================================================
    // State Machine Transitions (TEST-02: "状态机转换")
    // Covers: AC-PLAYER-10 through AC-PLAYER-16, AC-PLAYER-18, AC-PLAYER-19
    // =====================================================================

    @Test
    fun initialState_idle() {
        val viewModel = PlayerViewModel()
        assertEquals(PlayerState.IDLE, viewModel.playerState.value)
    }

    @Test
    fun setState_transitionsToPlaying() {
        val viewModel = PlayerViewModel()
        viewModel.setState(PlayerState.PLAYING)
        assertEquals(PlayerState.PLAYING, viewModel.playerState.value)
    }

    @Test
    fun setState_transitionsToPaused() {
        val viewModel = PlayerViewModel()
        viewModel.setState(PlayerState.PLAYING)
        viewModel.setState(PlayerState.PAUSED)
        assertEquals(PlayerState.PAUSED, viewModel.playerState.value)
    }

    @Test
    fun setState_transitionsToBuffering() {
        val viewModel = PlayerViewModel()
        viewModel.setState(PlayerState.BUFFERING)
        assertEquals(PlayerState.BUFFERING, viewModel.playerState.value)
    }

    @Test
    fun setState_transitionsToReady() {
        val viewModel = PlayerViewModel()
        viewModel.setState(PlayerState.READY)
        assertEquals(PlayerState.READY, viewModel.playerState.value)
    }

    @Test
    fun setState_transitionsToError() {
        val viewModel = PlayerViewModel()
        viewModel.setState(PlayerState.ERROR)
        assertEquals(PlayerState.ERROR, viewModel.playerState.value)
    }

    @Test
    fun setState_transitionsToEnded() {
        val viewModel = PlayerViewModel()
        viewModel.setState(PlayerState.ENDED)
        assertEquals(PlayerState.ENDED, viewModel.playerState.value)
    }

    @Test
    fun setState_noopOnSameState() {
        val viewModel = PlayerViewModel()
        viewModel.setState(PlayerState.PLAYING)
        viewModel.setState(PlayerState.PLAYING) // second call should be no-op
        assertEquals(PlayerState.PLAYING, viewModel.playerState.value)
    }

    // =====================================================================
    // Speed Switching (TEST-02: "速度切换")
    // Covers: AC-PLAYER-05, AC-PLAYER-19, AC-PLAYER-20, AC-PLAYER-21
    // =====================================================================

    @Test
    fun initialSpeed_is1X() {
        val viewModel = PlayerViewModel()
        assertEquals(PlaybackSpeed.SPEED_1X, viewModel.currentSpeed.value)
    }

    @Test
    fun setSpeed_0_5X() {
        val viewModel = PlayerViewModel()
        viewModel.setSpeed(PlaybackSpeed.SPEED_0_5X)
        assertEquals(PlaybackSpeed.SPEED_0_5X, viewModel.currentSpeed.value)
    }

    @Test
    fun setSpeed_0_75X() {
        val viewModel = PlayerViewModel()
        viewModel.setSpeed(PlaybackSpeed.SPEED_0_75X)
        assertEquals(PlaybackSpeed.SPEED_0_75X, viewModel.currentSpeed.value)
    }

    @Test
    fun setSpeed_1_25X() {
        val viewModel = PlayerViewModel()
        viewModel.setSpeed(PlaybackSpeed.SPEED_1_25X)
        assertEquals(PlaybackSpeed.SPEED_1_25X, viewModel.currentSpeed.value)
    }

    @Test
    fun setSpeed_1_5X() {
        val viewModel = PlayerViewModel()
        viewModel.setSpeed(PlaybackSpeed.SPEED_1_5X)
        assertEquals(PlaybackSpeed.SPEED_1_5X, viewModel.currentSpeed.value)
    }

    @Test
    fun setSpeed_2X() {
        val viewModel = PlayerViewModel()
        viewModel.setSpeed(PlaybackSpeed.SPEED_2X)
        assertEquals(PlaybackSpeed.SPEED_2X, viewModel.currentSpeed.value)
    }

    @Test
    fun setSpeed_cyclesThroughAllValues() {
        val viewModel = PlayerViewModel()
        val speeds = PlaybackSpeed.values()
        for (speed in speeds) {
            viewModel.setSpeed(speed)
            assertEquals(speed, viewModel.currentSpeed.value)
        }
    }

    // =====================================================================
    // Recover Path (TEST-02: "recover 路径")
    // Covers: AC-PLAYER-17 (ERROR -> BUFFERING via recover())
    // =====================================================================

    @Test
    fun recover_fromError_transitionsToBuffering() {
        val viewModel = PlayerViewModel()
        viewModel.setState(PlayerState.ERROR)
        assertEquals(PlayerState.ERROR, viewModel.playerState.value)

        viewModel.recover()
        assertEquals(PlayerState.BUFFERING, viewModel.playerState.value)
    }

    @Test
    fun recover_fromPlaying_transitionsToBuffering() {
        val viewModel = PlayerViewModel()
        viewModel.setState(PlayerState.PLAYING)
        viewModel.recover()
        assertEquals(PlayerState.BUFFERING, viewModel.playerState.value)
    }

    @Test
    fun recover_fromPaused_transitionsToBuffering() {
        val viewModel = PlayerViewModel()
        viewModel.setState(PlayerState.PAUSED)
        viewModel.recover()
        assertEquals(PlayerState.BUFFERING, viewModel.playerState.value)
    }

    @Test
    fun recover_fromEnded_transitionsToBuffering() {
        val viewModel = PlayerViewModel()
        viewModel.setState(PlayerState.ENDED)
        viewModel.recover()
        assertEquals(PlayerState.BUFFERING, viewModel.playerState.value)
    }
}
