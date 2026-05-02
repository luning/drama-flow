package com.dramaflow.home.ui

import android.os.Bundle
import android.view.View
import android.webkit.WebViewClient
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.dramaflow.R
import com.dramaflow.databinding.FragmentHomeBinding
import com.dramaflow.home.viewmodel.HomeViewModel

class HomeFragment : Fragment(R.layout.fragment_home) {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    private val viewModel: HomeViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentHomeBinding.bind(view)

        val webView = binding.h5WebView
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.webViewClient = WebViewClient()

        // 先从本地 assets 加载，开发时后端无状态文件则回退到此方案
        webView.loadUrl("http://10.0.2.2:8000/")

        viewModel.loadBanners()
        viewModel.loadDramas()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
