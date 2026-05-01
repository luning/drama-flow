package com.dramaflow

import android.app.Application

class DramaFlowApp : Application() {
    override fun onCreate() {
        super.onCreate()
        instance = this
    }

    companion object {
        lateinit var instance: DramaFlowApp
            private set
    }
}
