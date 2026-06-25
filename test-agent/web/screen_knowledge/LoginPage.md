# LoginPage

## 已知陷阱
- 登录页可能有 CSRF token 或表单验证，直接 type 到 input 有时不触发 Vue 的 v-model 绑定。优先使用 selector fill 或先 click input 再 type。
- 登录按钮可能被虚拟键盘遮挡（移动端视口），确保 viewport 高度足够。

## 预期元素
- 邮箱输入框 (input[type="email"] 或 input[placeholder*="邮箱"])
- 密码输入框 (input[type="password"])
- 登录按钮 (包含文本 "登录" 的 button)

## 交互提示
- 路由路径: /login
- 注册页入口: /register
- 登录成功后跳转到 / 首页
