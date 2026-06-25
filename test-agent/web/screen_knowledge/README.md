# Web Screen Knowledge

Each `.md` file documents known traps and interaction tips for a specific page (by route name).

## File Naming

Name files by their page/component name (not URL path):
- `LoginPage.md` — Login.vue (/login)
- `HomePage.md` — Home.vue (/)
- `DetailPage.md` — Detail.vue (/detail/:id)
- `PlayerPage.md` — Player.vue (/drama/:id/episode/:ep)

## Format

```markdown
# PageName

## 已知陷阱
- Description of known issues

## 预期元素
- Expected visible elements

## 交互提示
- How to interact with elements on this page
```
