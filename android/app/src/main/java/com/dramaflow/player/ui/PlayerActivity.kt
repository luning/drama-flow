package com.dramaflow.player.ui

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.SeekBar
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.common.AudioAttributes
import androidx.media3.common.C
import androidx.media3.exoplayer.ExoPlayer
import androidx.lifecycle.lifecycleScope
import com.dramaflow.R
import com.dramaflow.databinding.ActivityPlayerBinding
import com.dramaflow.data.remote.ApiClient
import com.dramaflow.data.remote.EpisodeItem
import com.dramaflow.data.remote.HomeApi
import com.dramaflow.player.viewmodel.PlayerState
import com.dramaflow.player.viewmodel.PlaybackSpeed
import com.dramaflow.player.viewmodel.PlayerViewModel
import kotlinx.coroutines.*
import android.view.WindowManager
import java.util.concurrent.TimeUnit

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
    private var hasResumedFromPosition = false

    // 是否正在拖拉进度条
    private var isSeeking = false

    // 控制条自动隐藏
    private var controlsVisible = true
    private var autoHideJob: Job? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPlayerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        currentEpisodeId = intent.getIntExtra("episode_id", 0)
        val videoUrl = intent.getStringExtra("video_url") ?: ""
        dramaId = intent.getIntExtra("drama_id", 0)
        currentEpisodeNumber = intent.getIntExtra("episode_number", 1)

        // 多集模式显示切换按钮
        if (dramaId > 0) {
            binding.btnSkipPrev.visibility = View.VISIBLE
            binding.btnSkipNext.visibility = View.VISIBLE
        }

        initPlayer(videoUrl)
        setupControls()
        observeViewModel()

        // 预加载剧集列表供 skip 按钮使用
        if (dramaId > 0) {
            loadEpisodeCache()
        }
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
                    when (playbackState) {
                        Player.STATE_IDLE -> {
                            // AC-PLAYER-12: Initial IDLE (after ViewModel init) / AC-PLAYER-18: Release → IDLE
                            viewModel.setState(PlayerState.IDLE)
                        }
                        Player.STATE_BUFFERING -> {
                            // AC-PLAYER-12/14: IDLE→BUFFERING (initial load) or PLAYING/PAUSED→BUFFERING (seek)
                            viewModel.setState(PlayerState.BUFFERING)
                        }
                        Player.STATE_READY -> {
                            // AC-PLAYER-12/14: BUFFERING → READY
                            viewModel.setState(PlayerState.READY)
                            // AC-PLAYER-13: READY → PLAYING or PAUSED based on playWhenReady
                            if (playWhenReady) {
                                viewModel.setState(PlayerState.PLAYING)
                            } else {
                                viewModel.setState(PlayerState.PAUSED)
                            }
                            // 首次就绪时续播
                            if (!hasResumedFromPosition) {
                                hasResumedFromPosition = true
                                viewModel.fetchLastPosition(currentEpisodeId) { lastPosition ->
                                    player?.seekTo(lastPosition)
                                }
                            }
                        }
                        Player.STATE_ENDED -> {
                            // AC-PLAYER-15: Playback complete → ENDED
                            viewModel.setState(PlayerState.ENDED)
                            onCurrentEpisodeEnded()
                        }
                    }
                }

                override fun onIsPlayingChanged(isPlaying: Boolean) {
                    if (isPlaying) {
                        binding.btnPlayPause.setImageResource(android.R.drawable.ic_media_pause)
                        viewModel.startPeriodicReporting(currentEpisodeId)
                    } else {
                        binding.btnPlayPause.setImageResource(android.R.drawable.ic_media_play)
                        viewModel.stopPeriodicReporting()
                        // 暂停时即时上报进度
                        player?.let { p ->
                            viewModel.reportProgress(currentEpisodeId, p.currentPosition, p.duration)
                        }
                    }
                }

                override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
                    // AC-PLAYER-16: Playback error → ERROR state
                    viewModel.setState(PlayerState.ERROR)
                    when (error.errorCode) {
                        androidx.media3.common.PlaybackException.ERROR_CODE_IO_BAD_HTTP_STATUS -> {
                            // 401/403 — 可能是签名 URL 过期，尝试自动刷新
                            Toast.makeText(this@PlayerActivity, "视频地址已过期，正在重新获取…", Toast.LENGTH_SHORT).show()
                            refreshVideoUrl()
                        }
                        androidx.media3.common.PlaybackException.ERROR_CODE_IO_NETWORK_CONNECTION_FAILED -> {
                            // 断网 — 不自动恢复，显示错误浮层让用户手动重试
                            Toast.makeText(this@PlayerActivity, "网络连接失败", Toast.LENGTH_SHORT).show()
                        }
                        else -> {
                            Toast.makeText(this@PlayerActivity, "播放出错: ${error.localizedMessage}", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            })
        }

        startProgressUpdater()
    }

    private fun refreshVideoUrl() {
        lifecycleScope.launch {
            try {
                val api = ApiClient.create<HomeApi>()
                val resp = api.getVideoUrl(currentEpisodeId)
                if (resp.isSuccessful) {
                    val body = resp.body()
                    val url = body?.url
                    if (!url.isNullOrBlank()) {
                        viewModel.recover()
                        player?.apply {
                            val mediaItem = MediaItem.fromUri(url)
                            setMediaItem(mediaItem)
                            prepare()
                            playWhenReady = true
                        }
                        return@launch
                    }
                }
                Toast.makeText(this@PlayerActivity, "无法获取视频地址", Toast.LENGTH_SHORT).show()
            } catch (_: Exception) {
                Toast.makeText(this@PlayerActivity, "重新获取视频地址失败", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun startProgressUpdater() {
        progressJob = lifecycleScope.launch {
            while (isActive) {
                delay(250)
                player?.let { p ->
                    if (!isSeeking && p.playbackState == Player.STATE_READY) {
                        val current = p.currentPosition
                        val duration = p.duration
                        updateProgressUi(current, duration)
                        viewModel.updatePlaybackPosition(current, duration)
                    }
                }
            }
        }
    }

    private fun updateProgressUi(currentMs: Long, durationMs: Long) {
        binding.tvCurrentTime.text = formatTime(currentMs)
        binding.tvTotalTime.text = formatTime(durationMs)
        if (durationMs > 0) {
            binding.progressSeekbar.progress = ((currentMs.toFloat() / durationMs) * 1000).toInt()
        }
    }

    private fun formatTime(ms: Long): String {
        if (ms <= 0) return "00:00"
        val h = TimeUnit.MILLISECONDS.toHours(ms)
        val m = TimeUnit.MILLISECONDS.toMinutes(ms) % 60
        val s = TimeUnit.MILLISECONDS.toSeconds(ms) % 60
        return if (h > 0) {
            String.format("%d:%02d:%02d", h, m, s)
        } else {
            String.format("%02d:%02d", m, s)
        }
    }

    private fun loadEpisodeCache() {
        lifecycleScope.launch {
            try {
                val api = ApiClient.create<HomeApi>()
                val response = api.listEpisodes(dramaId)
                episodeCache = if (response.isSuccessful) response.body() ?: emptyList()
                else emptyList()
                updateSkipButtons()
            } catch (_: Exception) { }
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

        // 切换剧集：重置续播标记，下一轮 STATE_READY 会重新拉取
        hasResumedFromPosition = false
        viewModel.stopPeriodicReporting()

        currentEpisodeId = ep.id
        currentEpisodeNumber = ep.episode_number

        // 更新 skip 按钮状态
        updateSkipButtons()

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
                } else {
                    p.play()
                }
            }
        }

        binding.progressSeekbar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                if (fromUser) {
                    player?.let { p ->
                        val position = (progress.toFloat() / 1000) * p.duration
                        binding.tvCurrentTime.text = formatTime(position.toLong())
                    }
                }
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {
                isSeeking = true
            }

            override fun onStopTrackingTouch(seekBar: SeekBar?) {
                isSeeking = false
                player?.let { p ->
                    val position = ((seekBar?.progress ?: 0).toFloat() / 1000) * p.duration
                    p.seekTo(position.toLong())
                }
            }
        })

        binding.btnSpeed.setOnClickListener {
            binding.speedMenu.visibility = if (binding.speedMenu.visibility == View.VISIBLE)
                View.GONE else View.VISIBLE
        }

        // 错误浮层重试按钮
        binding.btnRetry.setOnClickListener {
            viewModel.recover()
            refreshVideoUrl()
        }

        // AC-PLAYER-05: Speed selector - id-based binding for all 6 speed options
        binding.speedMenu.findViewById<Button>(R.id.btn_speed_05)?.setOnClickListener {
            viewModel.setSpeed(PlaybackSpeed.SPEED_0_5X)
            binding.speedMenu.visibility = View.GONE
        }
        binding.speedMenu.findViewById<Button>(R.id.btn_speed_075)?.setOnClickListener {
            viewModel.setSpeed(PlaybackSpeed.SPEED_0_75X)
            binding.speedMenu.visibility = View.GONE
        }
        binding.speedMenu.findViewById<Button>(R.id.btn_speed_10)?.setOnClickListener {
            viewModel.setSpeed(PlaybackSpeed.SPEED_1X)
            binding.speedMenu.visibility = View.GONE
        }
        binding.speedMenu.findViewById<Button>(R.id.btn_speed_125)?.setOnClickListener {
            viewModel.setSpeed(PlaybackSpeed.SPEED_1_25X)
            binding.speedMenu.visibility = View.GONE
        }
        binding.speedMenu.findViewById<Button>(R.id.btn_speed_15)?.setOnClickListener {
            viewModel.setSpeed(PlaybackSpeed.SPEED_1_5X)
            binding.speedMenu.visibility = View.GONE
        }
        binding.speedMenu.findViewById<Button>(R.id.btn_speed_20)?.setOnClickListener {
            viewModel.setSpeed(PlaybackSpeed.SPEED_2X)
            binding.speedMenu.visibility = View.GONE
        }

        binding.btnFullscreen.setOnClickListener {
            viewModel.toggleFullscreen()
        }

        binding.btnBack.setOnClickListener { finish() }

        binding.btnSkipPrev.setOnClickListener {
            navigateEpisode(-1)
        }

        binding.btnSkipNext.setOnClickListener {
            navigateEpisode(1)
        }

        // 点击 PlayerView 切换控制条显示
        binding.playerView.setOnClickListener {
            toggleControls()
        }
    }

    private fun toggleControls() {
        controlsVisible = !controlsVisible
        binding.playerControls.visibility = if (controlsVisible) View.VISIBLE else View.GONE
        if (controlsVisible && (viewModel.isFullscreen.value == true)) {
            startAutoHideTimer()
        }
    }

    private fun startAutoHideTimer() {
        autoHideJob?.cancel()
        autoHideJob = lifecycleScope.launch {
            delay(3000)
            controlsVisible = false
            binding.playerControls.visibility = View.GONE
        }
    }

    private fun navigateEpisode(direction: Int) {
        if (dramaId <= 0 || episodeCache.isEmpty()) return
        val currentIndex = episodeCache.indexOfFirst { it.id == currentEpisodeId }
        val targetIndex = currentIndex + direction
        if (targetIndex < 0 || targetIndex >= episodeCache.size) {
            Toast.makeText(this, if (direction < 0) "已是第一集" else "已是最后一集", Toast.LENGTH_SHORT).show()
            return
        }
        playEpisode(episodeCache[targetIndex])
    }

    private fun updateSkipButtons() {
        if (episodeCache.isEmpty() || dramaId <= 0) return
        val currentIndex = episodeCache.indexOfFirst { it.id == currentEpisodeId }
        binding.btnSkipPrev.alpha = if (currentIndex > 0) 1.0f else 0.3f
        binding.btnSkipNext.alpha = if (currentIndex < episodeCache.size - 1) 1.0f else 0.3f
    }

    private fun observeViewModel() {
        viewModel.currentSpeed.observe(this) { speed ->
            player?.setPlaybackSpeed(speed.value)
            binding.btnSpeed.text = "${speed.value}x"
            // 高亮 speed menu 中当前选中档，其它恢复灰色
            val speedButtons = mapOf(
                R.id.btn_speed_05 to PlaybackSpeed.SPEED_0_5X,
                R.id.btn_speed_075 to PlaybackSpeed.SPEED_0_75X,
                R.id.btn_speed_10 to PlaybackSpeed.SPEED_1X,
                R.id.btn_speed_125 to PlaybackSpeed.SPEED_1_25X,
                R.id.btn_speed_15 to PlaybackSpeed.SPEED_1_5X,
                R.id.btn_speed_20 to PlaybackSpeed.SPEED_2X,
            )
            for ((id, buttonSpeed) in speedButtons) {
                binding.speedMenu.findViewById<Button>(id)?.setTextColor(
                    if (buttonSpeed == speed) 0xFFA29BFE.toInt() else 0xFFB0B0B0.toInt()
                )
            }
        }

        viewModel.isFullscreen.observe(this) { fullscreen ->
            if (fullscreen) {
                window.addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN)
                supportActionBar?.hide()
                binding.btnFullscreen.setImageResource(R.drawable.ic_fullscreen_exit)
                // 全屏后自动隐藏控制条
                controlsVisible = true
                startAutoHideTimer()
            } else {
                window.clearFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN)
                supportActionBar?.show()
                binding.btnFullscreen.setImageResource(R.drawable.ic_fullscreen)
                // 退出全屏后保持控制条可见
                autoHideJob?.cancel()
                controlsVisible = true
                binding.playerControls.visibility = View.VISIBLE
            }
        }

        viewModel.playerState.observe(this) { state ->
            // AC-PLAYER-17: ERROR→BUFFERING — reset ExoPlayer to resume playback
            // When recover() sets BUFFERING after an error, ExoPlayer is in STATE_IDLE
            // and needs prepare() to restart playback
            if (state == PlayerState.BUFFERING && player?.playbackState == Player.STATE_IDLE) {
                player?.apply {
                    prepare()
                    playWhenReady = true
                }
            }

            // AC-PLAYER-16/15: Auto-show controls on error or playback end
            if (state == PlayerState.ENDED || state == PlayerState.ERROR) {
                autoHideJob?.cancel()
                controlsVisible = true
                binding.playerControls.visibility = View.VISIBLE
            }

            // 错误浮层：ERROR 时显示，离开 ERROR 时隐藏
            binding.playerErrorOverlay.visibility = if (state == PlayerState.ERROR) View.VISIBLE else View.GONE
        }
    }

    override fun onStop() {
        super.onStop()
        // 退出时即时上报进度
        player?.let { p ->
            if (p.playbackState == Player.STATE_READY || p.isPlaying) {
                viewModel.reportProgress(currentEpisodeId, p.currentPosition, p.duration)
            }
        }
        viewModel.stopPeriodicReporting()
        player?.pause()
    }

    override fun onDestroy() {
        super.onDestroy()
        progressJob?.cancel()
        nextEpisodeJob?.cancel()
        player?.release()
        // AC-PLAYER-18: Reset state to IDLE after player release
        viewModel.setState(PlayerState.IDLE)
        player = null
    }

    override fun onResume() {
        super.onResume()
        binding.speedMenu.visibility = View.GONE
    }
}
