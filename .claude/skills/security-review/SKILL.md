---
name: security-review
description: 安全审查——扫描 DramaFlow 代码库中的常见安全漏洞。当用户说"安全检查"、"安全审查"、"security review"、"漏洞扫描"、"审计安全"时触发。
---

# 安全审查（Security Review）

从以下维度扫描指定路径或整个项目中的安全风险。

## 审查清单

### 认证安全
- [ ] JWT Secret 是否使用默认值（`change-this-in-production`）
- [ ] Token 是否存储在 EncryptedSharedPreferences（Android）而非明文
- [ ] 密码是否使用 bcrypt 哈希
- [ ] Token 过期后是否有刷新机制
- [ ] 登出后 Token 是否被作废（黑名单机制）

### API 安全
- [ ] 敏感接口是否有认证中间件保护
- [ ] 错误响应是否暴露内部技术细节
- [ ] 输入参数是否有类型校验和长度限制
- [ ] CORS 配置是否过于宽松（`allow_origins=["*"]`）

### 数据安全
- [ ] SQL 查询是否使用 ORM 参数化查询（防止 SQL 注入）
- [ ] 用户密码/Token 是否出现在日志中
- [ ] 数据库文件是否有访问权限保护

### Android 安全
- [ ] WebView 是否启用了 JavaScript
- [ ] WebView 是否禁用了危险的 API（文件访问等）
- [ ] 是否使用了 EncryptedSharedPreferences

## 输出格式

```json
{
  "summary": {
    "total_checks": 16,
    "passed": 12,
    "warnings": 3,
    "critical": 1
  },
  "critical_issues": [
    {
      "file": "backend/app/config.py",
      "line": 5,
      "finding": "JWT 密钥使用了默认值 'change-this-in-production'",
      "risk": "攻击者可伪造任意 JWT Token",
      "fix": "替换为环境变量读取，如 os.getenv('JWT_SECRET_KEY')"
    }
  ],
  "warnings": [
    {
      "file": "backend/app/main.py",
      "line": 20,
      "finding": "CORS allow_origins=['*']",
      "risk": "任何域名均可跨域请求",
      "fix": "生产环境限制为具体域名列表"
    }
  ]
}
```

## 注意事项

- 不对第三方依赖做漏洞扫描（建议使用 `pip audit` 或 Dependabot）
- 不扫描 H5 前端的 XSS/CSRF（交给专门的 Web 安全工具）
- 生产环境部署前必须修复所有 critical 级别问题
