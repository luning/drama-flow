package com.dramaflow.detail.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.dramaflow.data.remote.ApiClient
import com.dramaflow.data.remote.HomeApi
import com.dramaflow.data.remote.DramaDetail
import com.dramaflow.data.remote.EpisodeItem
import kotlinx.coroutines.launch

class DetailViewModel : ViewModel() {

    private val api = ApiClient.create<HomeApi>()

    private val _detail = MutableLiveData<DramaDetail?>()
    val detail: LiveData<DramaDetail?> = _detail

    private val _episodes = MutableLiveData<List<EpisodeItem>>()
    val episodes: LiveData<List<EpisodeItem>> = _episodes

    fun loadDetail(dramaId: Int) {
        viewModelScope.launch {
            try {
                val resp = api.getDramaDetail(dramaId)
                _detail.value = resp.body()
            } catch (_: Exception) { }
        }
    }

    fun loadEpisodes(dramaId: Int) {
        viewModelScope.launch {
            try {
                val resp = api.listEpisodes(dramaId)
                _episodes.value = resp.body() ?: emptyList()
            } catch (_: Exception) { }
        }
    }
}
