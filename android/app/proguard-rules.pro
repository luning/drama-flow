# ProGuard / R8 keep rules for DramaFlow

# Retrofit
-keepattributes Signature
-keepattributes *Annotation*
-keep class retrofit2.** { *; }
-keepclasseswithmembers class * {
    @retrofit2.http.* <methods>;
}

# Moshi (reflection adapter)
-keep class com.squareup.moshi.** { *; }
-keep class com.dramaflow.data.remote.** { *; }
-keep class com.dramaflow.data.remote.model.** { *; }

# Glide
-keep class com.bumptech.glide.** { *; }
-keep public class * implements com.bumptech.glide.module.GlideModule

# OkHttp
-keep class okhttp3.** { *; }
-dontwarn okhttp3.**

# Media3 / ExoPlayer
-keep class androidx.media3.** { *; }

# Kotlin Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}

# AndroidX Security
-keep class androidx.security.crypto.** { *; }

# Gson removal safety (if any transitive dependency uses it)
-dontwarn com.google.gson.**
