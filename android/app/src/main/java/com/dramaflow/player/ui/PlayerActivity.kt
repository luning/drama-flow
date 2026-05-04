package com.dramaflow.player.ui

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.common.AudioAttributes
import androidx.media3.common.C
import androidx.media3.exoplayer.ExoPlayer
import androidx.lifecycle.lifecycleScope
import com.dramaflow.databinding.ActivityPlayerBinding
import com.dramaflow.data.remote.ApiClient
import com.dramaflow.data.remote.HomeApi
import com.dramaflow.data.remote.EpisodeItem
import com.dramaflow.player.viewmodel.PlayerViewModel
import com.dramaflow.player.viewmodel.PlaybackSpeed
import kotlinx.coroutines.*
import android.view.WindowManager

class PlayerActivity : AppCompatActivity() {

    private lateinit var binding: ActivityPlayerBinding
    private val viewModel: PlayerViewModel by viewModels()
    private var player: ExoPlayer? = null
    private var progressJob: Job? = null
    private var nextEpisodeJob: Job? = null

    // 连播状态
    private var dramaId: Int = 0
    private var currentEpisodeId: Int = 0
    private var currentEpisodeNumber: Int = 1
    private var episodeCache: List<EpisodeItem> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPlayerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        currentEpisodeId = intent.getIntExtra("episode_id", 0)
        val videoUrl = intent.getStringExtra("video_url") ?: ""
        dramaId = intent.getIntExtra("drama_id", 0)
        currentEpisodeNumber = intent.getIntExtra("episode_number", 1)

        initPlayer(videoUrl)
        setupControls()
        observeViewModel()
    }

    private fun initPlayer(videoUrl: String) {
        player = ExoPlayer.Builder(this).build().apply {
            binding.playerView.player = this
            setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(C.USAGE_MEDIA)
                    .setContentType(C.AUDIO_CONTENT_TYPE_MOVIE)
                    .build(),
                /* handleAudioFocus= */ true
            )
            setMediaItem(MediaItem.fromUri(videoUrl))
            prepare()
            playWhenReady = true
            addListener(object : Player.Listener {
                override fun onPlaybackStateChanged(playbackState: Int) {
                    if (playbackState == Player.STATE_ENDED) {
                        onCurrentEpisodeEnded()
                    }
                }

                override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
                    Toast.makeText(this@PlayerActivity, "播放出错: ${error.localizedMessage}", Toast.LENGTH_SHORT).show()
                }
            })
        }

        startProgressReporting()
    }

    private fun startProgressReporting() {
        progressJob = lifecycleScope.launch {
            while (isActive) {
                delay(15_000) // every 15 seconds
                player?.let { p ->
                    viewModel.reportProgress(currentEpisodeId, p.currentPosition, p.duration)
                }
            }
        }
    }

    private fun onCurrentEpisodeEnded() {
        // 上报当前集完成
        player?.let { p ->
            viewModel.reportProgress(currentEpisodeId, p.duration, p.duration)
        }

        // 单集播放（没有 drama_id），播完即退
        if (dramaId <= 0) {
            finish()
            return
        }

        // 加载下一集（取消前一次任务避免竞态）
        nextEpisodeJob?.cancel()
        nextEpisodeJob = lifecycleScope.launch {
            try {
                if (episodeCache.isEmpty()) {
                    val api = ApiClient.create<HomeApi>()
                    val response = api.listEpisodes(dramaId)
                    episodeCache = if (response.isSuccessful) response.body() ?: emptyList()
                    else emptyList()
                }

                if (episodeCache.isEmpty()) {
                    Toast.makeText(this@PlayerActivity, "暂无剧集信息", Toast.LENGTH_SHORT).show()
                    delay(1200)
                    finish()
                    return@launch
                }

                val currentIndex = episodeCache.indexOfFirst { it.id == currentEpisodeId }
                if (currentIndex < 0) {
                    // 当前集未找到，尝试播放第一集
                    playEpisode(episodeCache.first())
                    return@launch
                }

                val nextIndex = currentIndex + 1
                if (nextIndex < episodeCache.size) {
                    playEpisode(episodeCache[nextIndex])
                } else {
                    Toast.makeText(this@PlayerActivity, "全部剧集已播放完毕", Toast.LENGTH_SHORT).show()
                    delay(1200)
                    finish()
                }
            } catch (e: Exception) {
                Toast.makeText(this@PlayerActivity, "加载下一集失败", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun playEpisode(ep: EpisodeItem) {
        if (ep.video_url.isBlank()) {
            Toast.makeText(this, "该集视频地址无效", Toast.LENGTH_SHORT).show()
            return
        }

        currentEpisodeId = ep.id
        currentEpisodeNumber = ep.episode_number

        Toast.makeText(this, "正在播放第 ${ep.episode_number} 集", Toast.LENGTH_SHORT).show()

        player?.apply {
            val mediaItem = MediaItem.fromUri(ep.video_url)
            setMediaItem(mediaItem)
            prepare()
            playWhenReady = true
        }
    }

    private fun setupControls() {
        binding.btnPlayPause.setOnClickListener {
            player?.let { p ->
                if (p.isPlaying) {
                    p.pause()
                    binding.btnPlayPause.setImageResource(android.R.drawable.ic_media_play)
                } else {
                    p.play()
                    binding.btnPlayPause.setImageResource(android.R.drawable.ic_media_pause)
                }
            }
        }

        binding.btnSpeed.setOnClickListener {
            binding.speedMenu.visibility = if (binding.speedMenu.visibility == View.VISIBLE)
                View.GONE else View.VISIBLE
        }

        for (i in 0 until binding.speedMenu.childCount) {
            val btn = binding.speedMenu.getChildAt(i) as? Button ?: continue
            btn.setOnClickListener {
                val speed = when (btn.text.toString()) {
                    "0.5x" -> PlaybackSpeed.SPEED_0_5X
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
        nextEpisodeJob?.cancel()
        player?.release()
        player = null
    }

    override fun onResume() {
        super.onResume()
        binding.speedMenu.visibility = View.GONE
    }
}
