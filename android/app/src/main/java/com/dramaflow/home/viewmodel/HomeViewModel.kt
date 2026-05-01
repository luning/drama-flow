package com.dramaflow.home.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.dramaflow.data.remote.ApiClient
import com.dramaflow.data.remote.HomeApi
import com.dramaflow.data.remote.DramaItem
import com.dramaflow.data.remote.BannerItem
import kotlinx.coroutines.launch

class HomeViewModel : ViewModel() {

    private val api = ApiClient.create<HomeApi>()

    private val _dramas = MutableLiveData<List<DramaItem>>()
    val dramas: LiveData<List<DramaItem>> = _dramas

    private val _banners = MutableLiveData<List<BannerItem>>()
    val banners: LiveData<List<BannerItem>> = _banners

    private val _loading = MutableLiveData(false)
    val loading: LiveData<Boolean> = _loading

    fun loadDramas(category: String? = null) {
        _loading.value = true
        viewModelScope.launch {
            try {
                val resp = api.listDramas(category)
                _dramas.value = resp.body()?.items ?: emptyList()
            } catch (_: Exception) {
                _dramas.value = emptyList()
            } finally {
                _loading.value = false
            }
        }
    }

    fun loadBanners() {
        viewModelScope.launch {
            try {
                val resp = api.getBanners()
                _banners.value = resp.body() ?: emptyList()
            } catch (_: Exception) { }
        }
    }
}
