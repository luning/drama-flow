package com.dramaflow.common

import android.app.Activity
import android.webkit.JavascriptInterface
import com.dramaflow.DramaFlowApp
import java.lang.ref.WeakReference

/**
 * Android WebView 与 Vue3 H5 的通信桥接。
 * H5 通过 window.DramaFlowBridge.{method} 调用原生能力。
 *
 * 持有 Activity 的弱引用确保导航栈连续——PlayerActivity 在同一个 Task 中打开，
 * finish() 后自然返回前一页面，而非回到系统桌面。
 */
class JSBridge(activity: Activity) {

    private val activityRef = WeakReference(activity)

    @JavascriptInterface
    fun playVideo(episodeId: Int, videoUrl: String, title: String, dramaId: Int = 0, episodeNumber: Int = 1) {
        val act = activityRef.get() ?: return
        val intent = android.content.Intent(act, Class.forName("com.dramaflow.player.ui.PlayerActivity")).apply {
            putExtra("episode_id", episodeId)
            putExtra("video_url", videoUrl)
            putExtra("title", title)
            putExtra("drama_id", dramaId)
            putExtra("episode_number", episodeNumber)
        }
        act.startActivity(intent)
    }

    @JavascriptInterface
    fun openPlayer(episodeId: Int, dramaId: Int, episodeNumber: Int) {
        val act = activityRef.get() ?: return
        val intent = android.content.Intent(act, Class.forName("com.dramaflow.player.ui.PlayerActivity")).apply {
            putExtra("episode_id", episodeId)
            putExtra("video_url", "")
            putExtra("title", "")
            putExtra("drama_id", dramaId)
            putExtra("episode_number", episodeNumber)
        }
        act.startActivity(intent)
    }

    @JavascriptInterface
    fun getAccessToken(): String {
        val prefs = com.dramaflow.data.local.PreferencesManager(DramaFlowApp.instance)
        return prefs.accessToken ?: ""
    }

    @Suppress("UNUSED_PARAMETER")
    @JavascriptInterface
    fun shareDrama(dramaId: Int, title: String) {
        val act = activityRef.get() ?: return
        val sendIntent = android.content.Intent().apply {
            action = android.content.Intent.ACTION_SEND
            putExtra(android.content.Intent.EXTRA_TEXT, "来 DramaFlow 看《$title》！")
            type = "text/plain"
        }
        act.startActivity(android.content.Intent.createChooser(sendIntent, "分享"))
    }
}
