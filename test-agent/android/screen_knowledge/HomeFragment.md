# HomeFragment (H5 WebView)

## 陷阱
- **系统手势干扰**：滑动起点 y 不要低于 screen_height - 200，否则触发返回桌面。Activity 变成 NexusLauncherActivity 就是滑过头了。
