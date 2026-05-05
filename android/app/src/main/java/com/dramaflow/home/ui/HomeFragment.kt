package com.dramaflow.home.ui

import android.os.Bundle
import android.view.KeyEvent
import android.view.View
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.dramaflow.R
import com.dramaflow.auth.viewmodel.AuthViewModel
import com.dramaflow.common.JSBridge
import com.dramaflow.databinding.FragmentHomeBinding
import com.dramaflow.home.viewmodel.HomeViewModel

class HomeFragment : Fragment(R.layout.fragment_home) {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    private val viewModel: HomeViewModel by viewModels()
    private val authViewModel: AuthViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentHomeBinding.bind(view)

        val webView = binding.h5WebView
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.allowFileAccess = false
        webView.webViewClient = WebViewClient()

        // 注入 JSBridge，使 H5 可通过 window.DramaFlowBridge 调用原生功能
        webView.addJavascriptInterface(JSBridge(requireActivity()), "DramaFlowBridge")

        // WebView 内后退导航（H5 hash 路由）
        webView.setOnKeyListener { _, keyCode, event ->
            if (keyCode == KeyEvent.KEYCODE_BACK && event.action == KeyEvent.ACTION_DOWN) {
                if (webView.canGoBack()) {
                    webView.goBack()
                    return@setOnKeyListener true
                }
            }
            false
        }

        webView.loadUrl("http://10.0.2.2:8000/")

        // 退出登录 → 清除 Token → 跳转登录页
        binding.btnLogout.setOnClickListener {
            authViewModel.logout()
            findNavController().navigate(R.id.action_global_to_login)
        }

        viewModel.loadBanners()
        viewModel.loadDramas()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
