# Screen Knowledge Base

每个文件对应一个页面（以 Activity 或 Fragment 命名），记录该页面的操作经验和已知陷阱。

## 使用方式

在执行测试流程时，`info` 命令返回当前 Activity/Fragment 后，检查是否有对应的 `.md` 文件：

```
test-agent/assets/screen_knowledge/{当前页面}.md
```

如有则读取，了解已知陷阱后再执行操作。

## 文件清单

| 页面 | 文件 | 说明 |
|------|------|------|
| 登录页 | LoginFragment.md | 邮箱/密码登录 |
| 首页 | HomeFragment.md | WebView H5 首页 |
