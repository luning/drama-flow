# LoginFragment

## 陷阱
- **键盘遮挡**：输入密码后按 BACK 收起键盘，再点登录按钮。`find-id "btn_login"` 找不到说明被挡住了。
- **单 Activity**：`tap` 报 "Screen unchanged" 是正常的。登录成功标志是 nav_host_fragment 中出现 WebView 节点。
- **底部导航栏始终可见**：不要因为看到首页/发现/我的就以为已登录。
