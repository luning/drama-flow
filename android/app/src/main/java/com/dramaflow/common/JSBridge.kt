package com.dramaflow.common

import android.webkit.JavascriptInterface
import com.dramaflow.DramaFlowApp

/**
 * Android WebView 与 Vue3 H5 的通信桥接。
 * H5 通过 window.DramaFlowBridge.{method} 调用原生能力。
 */
class JSBridge {

    @JavascriptInterface
    fun playVideo(episodeId: Int, videoUrl: String, title: String) {
        val context = DramaFlowApp.instance
        // 启动 PlayerActivity
        val intent = android.content.Intent(context, Class.forName("com.dramaflow.player.ui.PlayerActivity")).apply {
            putExtra("episode_id", episodeId)
            putExtra("video_url", videoUrl)
            putExtra("title", title)
            flags = android.content.Intent.FLAG_ACTIVITY_NEW_TASK
        }
        context.startActivity(intent)
    }

    @JavascriptInterface
    fun getAccessToken(): String {
        val prefs = com.dramaflow.data.local.PreferencesManager(DramaFlowApp.instance)
        return prefs.accessToken ?: ""
    }

    @JavascriptInterface
    fun shareDrama(dramaId: Int, title: String) {
        val context = DramaFlowApp.instance
        val sendIntent = android.content.Intent().apply {
            action = android.content.Intent.ACTION_SEND
            putExtra(android.content.Intent.EXTRA_TEXT, "来 DramaFlow 看《$title》！")
            type = "text/plain"
        }
        context.startActivity(android.content.Intent.createChooser(sendIntent, "分享"))
    }
}
