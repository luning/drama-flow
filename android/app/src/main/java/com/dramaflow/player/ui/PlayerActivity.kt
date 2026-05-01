package com.dramaflow.player.ui

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import com.dramaflow.databinding.ActivityPlayerBinding
import com.dramaflow.player.viewmodel.PlayerViewModel
import com.dramaflow.player.viewmodel.PlaybackSpeed
import kotlinx.coroutines.*
import android.view.WindowManager

class PlayerActivity : AppCompatActivity() {

    private lateinit var binding: ActivityPlayerBinding
    private val viewModel: PlayerViewModel by viewModels()
    private var player: ExoPlayer? = null
    private var progressJob: Job? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPlayerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val videoUrl = intent.getStringExtra("video_url") ?: ""
        initPlayer(videoUrl)
        setupControls()
        observeViewModel()
    }

    private fun initPlayer(videoUrl: String) {
        player = ExoPlayer.Builder(this).build().apply {
            binding.playerView.player = this
            val mediaItem = MediaItem.fromUri(videoUrl)
            setMediaItem(mediaItem)
            prepare()
            playWhenReady = true
        }

        startProgressReporting()
    }

    private fun startProgressReporting() {
        progressJob = lifecycleScope.launch(Dispatchers.IO) {
            while (isActive) {
                delay(15_000) // every 15 seconds
                player?.let { p ->
                    val episodeId = intent.getIntExtra("episode_id", 0)
                    viewModel.reportProgress(episodeId, p.currentPosition, p.duration)
                }
            }
        }
    }

    private fun setupControls() {
        binding.btnPlayPause.setOnClickListener {
            player?.let { p ->
                if (p.isPlaying) { p.pause(); binding.btnPlayPause.text = "▶" }
                else { p.play(); binding.btnPlayPause.text = "⏸" }
            }
        }

        binding.btnSpeed.setOnClickListener {
            binding.speedMenu.visibility = if (binding.speedMenu.visibility == View.VISIBLE)
                View.GONE else View.VISIBLE
        }

        binding.speedValues.forEach { btn ->
            btn.setOnClickListener {
                val speed = when (btn.text) {
                    "0.5x" -> PlaybackSpeed.SPEED_0_5X
                    "0.75x" -> PlaybackSpeed.SPEED_0_75X
                    "1.5x" -> PlaybackSpeed.SPEED_1_5X
                    "2.0x" -> PlaybackSpeed.SPEED_2X
                    else -> PlaybackSpeed.SPEED_1X
                }
                viewModel.setSpeed(speed)
                binding.speedMenu.visibility = View.GONE
            }
        }

        binding.btnFullscreen.setOnClickListener {
            viewModel.toggleFullscreen()
        }

        binding.btnBack.setOnClickListener { finish() }
    }

    private fun observeViewModel() {
        viewModel.currentSpeed.observe(this) { speed ->
            player?.setPlaybackSpeed(speed.value)
            binding.btnSpeed.text = "${speed.value}x"
        }

        viewModel.isFullscreen.observe(this) { fullscreen ->
            if (fullscreen) {
                window.addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN)
                supportActionBar?.hide()
            } else {
                window.clearFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN)
                supportActionBar?.show()
            }
        }
    }

    override fun onStop() {
        super.onStop()
        player?.pause()
    }

    override fun onDestroy() {
        super.onDestroy()
        progressJob?.cancel()
        player?.release()
        player = null
    }

    override fun onResume() {
        super.onResume()
        binding.speedMenu.visibility = View.GONE
    }
}
