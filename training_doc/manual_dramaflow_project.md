# 讲师手册 — DramaFlow 项目配置与视觉验收体系

本文件包含课程配套项目的完整技术细节，供讲师备课和演示使用。对应大纲环节：产品设计 Step 4、工程化 Step 5–7、Deep Dive Block 2。

---

## 一、项目目录结构（Agent 友好型设计）

```
dramaflow/
├── CLAUDE.md                      # 系统级 Agent 指令（架构/规范/禁止项）
├── SPEC.md                        # 可执行规格文档（随迭代更新）
├── docs/
│   ├── adr/                       # 架构决策记录
│   ├── designs/                   # Figma 导出参考图（Golden 基准来源）
│   └── design_system.md           # 设计系统规范（从 Figma 提取）
├── backend/                       # Python FastAPI 服务
│   ├── README.md
│   ├── app/
│   │   ├── api/                   # 路由层（按领域拆分）
│   │   │   └── README.md
│   │   ├── services/              # 业务逻辑层
│   │   │   └── README.md
│   │   └── models/                # Pydantic 数据模型
│   │       └── README.md
│   └── tests/                     # pytest 后端集成测试
├── lib/                           # Flutter 移动端
│   ├── core/                      # 公共基础（网络/主题/路由）
│   │   └── README.md
│   ├── features/
│   │   ├── auth/                  # 认证（独立限界上下文）
│   │   │   └── README.md
│   │   ├── home/
│   │   │   └── README.md
│   │   ├── player/
│   │   │   └── README.md
│   │   └── profile/
│   │       └── README.md
│   └── shared/                    # 公共组件
├── test/
│   ├── golden/                    # Flutter Golden Tests（Layer 1 视觉验收）
│   │   └── goldens/               # 基准截图（对齐 Figma 后人工确认并生成）
│   └── integration_test/          # Flutter 行为级集成测试
├── .claude/
│   └── commands/                  # 自定义 Skills
│       ├── build-check.md         # flutter build + integration_test
│       ├── golden-check.md        # Golden Tests：生成/更新/对比基准截图
│       ├── api-check.md           # pytest 后端 API 测试 + 接口冒烟
│       ├── seed-data.md           # 导入 SQLite 测试数据
│       ├── spec-validate.md       # 对照 Spec 验收标准检查实现
│       └── cr-refactor.md         # 代码审阅 + 重构建议
└── pubspec.yaml
```

**设计原则**：每个模块目录都有 README.md，明确职责、依赖和约束。这是 Agent 友好型架构的核心——Agent 在处理任务时通过读取 README 快速定位上下文，而不是盲目探索整个代码库。

---

## 二、SPEC.md 格式模板

每个功能模块使用如下固定格式：

```markdown
## [功能名称]

**领域名词**：定义本模块涉及的关键实体（如 Drama、Episode、WatchRecord）
**前置条件**：触发此功能需要满足什么状态
**主流程**：Happy Path 的分步描述
**异常处理**：每种异常情况的预期行为
**验收标准（AC）**：可验证的 Done 条件（行为描述，非实现描述）
**视觉验收 AC**：颜色/字体/间距符合 design_system.md 中对应规范
```

**示例（Auth 登录功能）**：

```markdown
## 用户登录

**领域名词**：User（uid, email, displayName）、AuthToken（JWT）
**前置条件**：用户未登录，已有注册账号
**主流程**：
  1. 用户输入 email + password
  2. 调用 POST /api/auth/login
  3. 后端验证账号密码，签发 JWT token
  4. 返回 JWT，前端存储并跳转首页
**异常处理**：
  - 密码错误：显示"邮箱或密码错误"，不暴露具体原因
  - 网络超时：显示重试提示，保留已输入内容
  - 账号不存在：与密码错误显示相同文案（防枚举）
**验收标准（AC）**：
  - AC1：正确凭证登录后，3s 内跳转首页
  - AC2：错误凭证显示错误提示，不跳转
  - AC3：登出后访问受保护页面重定向到登录页
**视觉验收 AC**：
  - 登录按钮颜色为 primary (#007AFF)，字体 16px
  - 输入框 padding 符合 AppSpacing.s16 (16px)
```

---

## 三、CLAUDE.md 结构与 SDD 约束

### 3.1 CLAUDE.md 基础结构

```markdown
# DramaFlow Agent 指令

## 技术栈
- 后端：Python 3.10+ + FastAPI + Pydantic + SQLAlchemy（SQLite）
- 前端：Flutter Web (Dart) + 原生 StatefulWidget（setState）
- 数据库：SQLite（嵌入式，文件随代码同步）
- 认证：FastAPI JWT（python-jose）
- 视频 CDN：七牛云（Qiniu）签名 URL

## 架构约束
- 禁止 feature 模块之间直接互相调用，必须通过 shared/ 或 API 层
- 后端所有数据模型必须使用 Pydantic，不允许裸 dict 传递
- Flutter 端所有网络请求通过 lib/core/network/ 统一发起

## 命名规范
- Python：snake_case 函数和变量，PascalCase 类
- Dart：camelCase 函数和变量，PascalCase 类和 Widget
- API 路径：/api/{resource}/{id} 格式

## SDD 开发规范
- 每次接受任务前，必须确认已阅读 SPEC.md 中对应章节
- 生成代码后，使用验收标准自检：每条 AC 是否有对应实现
- 禁止在未更新 SPEC.md 的情况下改变功能行为
- 生成 Flutter UI 时，颜色和间距必须引用 design_system.md 中的 Token，不允许硬编码
```

### 3.2 SDD 约束的价值演示

**演示对比**（讲师现场演示）：

- 不带 CLAUDE.md：Claude Code 生成登录界面时直接硬编码颜色 `Color(0xFF007AFF)`
- 带 CLAUDE.md（含"颜色必须引用 Token"约束）：Claude Code 自动引用 `AppColors.primary`

这一对比说明 CLAUDE.md 的约束规则可以直接影响 AI 生成代码的质量，而不需要每次在 Prompt 中重复说明。

---

## 四、Skills 详细设计

### 4.1 build-check.md

```markdown
# build-check

flutter build web --profile && \
flutter test integration_test/ --no-pub

输出：
- 编译成功/失败
- 集成测试通过率
- 失败测试的详细日志
```

### 4.2 golden-check.md

```markdown
# golden-check

参数：
- update: 是否更新基准（默认 false）

执行：
if update:
    flutter test --update-goldens test/golden/
else:
    flutter test test/golden/
    
输出：
- 通过/失败的组件列表
- 失败时自动生成对比图到 test/golden/failures/
- 输出与 Figma 设计稿的文件名对应关系
```

### 4.3 api-check.md

```markdown
# api-check

cd backend && \
python -m pytest tests/ -v --tb=short

输出：
- 测试通过率
- 失败接口的请求/响应详情
- 覆盖的 API 端点列表
```

### 4.4 seed-data.md

```markdown
# seed-data

python backend/scripts/seed_sqlite.py

导入内容：
- 10 部 Drama（含封面、简介、分类）
- 每部 Drama 含 3-5 个 Episode（视频 URL 使用七牛云测试域名）
- 2 个测试用户账号（test1@demo.com / test2@demo.com）

幂等性：先清空相关表再写入，重复运行安全
```

### 4.5 spec-validate.md

```markdown
# spec-validate

参数：feature（功能名称，如 auth/home/player）

执行：
1. 读取 SPEC.md 中对应功能的验收标准（AC 列表）
2. 搜索代码库中对应功能的实现
3. 逐条检查每个 AC 是否有对应实现

输出格式：
✅ AC1：正确凭证登录后 3s 内跳转首页 → 已实现（lib/features/auth/login_page.dart:42）
❌ AC3：登出后重定向 → 未找到实现
⚠️  视觉 AC2：输入框 padding → 无法自动验证，需人工核查
```

### 4.6 cr-refactor.md

```markdown
# cr-refactor

参数：path（要审阅的目录或文件）

执行：
读取目标代码 → 对照 CLAUDE.md 约束检查 → 识别代码坏味道

输出：
[HIGH] 重复逻辑：auth_service.py:23 和 user_service.py:45 有相同的 token 验证逻辑
[MEDIUM] 命名混乱：_process_data 函数命名过于泛化，建议重命名
[LOW] 状态泄漏：LoginPage 中的 isLoading 未在 dispose 时重置

每条问题附带重构建议和预期收益
```

---

## 五、视觉设计验收完整方法论

### 5.1 核心前提

Flutter 没有 DOM，所有视觉测试本质上都是"截图驱动"。四层架构的设计逻辑是：

- **严格层（Golden）**：保证不漏，构成精确契约
- **容忍层（截图容差比对）**：过滤渲染噪音，聚焦结构性变化（可扩展至 Applitools/Percy 等商业工具）
- **AI 层（Claude/GPT Vision）**：将视觉差异翻译为 UX 影响，供人决策
- **规则层（自定义脚本）**：机械地校验 Token 合规，可选引入

| 层 | 推荐工具 | 敏感度 | 解决什么问题 | 局限 |
|----|---------|--------|-------------|------|
| **Layer 1: Golden Test** | flutter_test / golden_toolkit | 极高（像素级）| 捕获任何视觉变化 | 误报多（字体/AA 渲染差异）；需管理基准图 |
| **Layer 2: Diff 工具** | 截图容差比对脚本（扩展：Applitools / Percy）| 中（Layout 级）| 过滤噪音，聚焦结构变化 | 商业工具需外部 API 和成本；课程中以脚本替代 |
| **Layer 3: AI 分析** | Claude / GPT Vision | 低（语义级）| 解释偏差的 UX 含义 | 有幻觉风险，不能自动判定 |
| **Layer 4: 规则引擎** | 自定义脚本 | 精确 | spacing / color token 合规 | 需维护规则；无法捕获"感觉" |

### 5.2 一个例子说明完整工作流

**场景**：开发完成 ProductPage，需验收是否符合 Figma 设计稿。

故意埋入的两类问题：
- **结构偏差**：`padding: EdgeInsets.all(12)`（设计稿要求 16）
- **细节偏差**：价格字体 `fontSize: 14`（设计稿要求 16）

**各层检测结果**：

| 问题 | Golden Test | Applitools/Percy (Layout) | AI 分析输出 |
|------|-------------|--------------------------|-------------|
| padding 差 4px（结构）| ❌ FAIL | ❌ FAIL | "内容区域整体向右压缩，购买按钮可能超出可视区，影响转化率" |
| 字体差 2px（细节）| ❌ FAIL | ✅ PASS（噪音过滤）| — |

**关键洞见**：
- Golden 对两种问题都报错——**像素级契约，不会漏，但会误报**
- Applitools/Percy Layout 模式过滤了字体微差异——**视觉语义契约，理解结构**
- AI 输出对结构偏差的 UX 解释有实际参考价值；对细节偏差因已被 Layer 2 过滤，不需要触发

### 5.3 Demo 项目结构

```
flutter_visual_demo/
├── lib/
│   └── ui/
│       ├── product_page.dart        # 含故意埋入错误的示例页面
│       └── design_tokens.dart       # 设计规范 Token 定义
├── test/
│   ├── golden/
│   │   ├── product_page_test.dart   # Golden Test
│   │   └── goldens/                 # 基准截图（首次运行生成）
│   └── visual_diff/
│       └── compare.py               # 截图容差比对脚本（Layer 2，可替换为 Applitools/Percy）
└── pubspec.yaml
```

### 5.4 关键代码

**设计 Token（design_tokens.dart）**：

```dart
import 'package:flutter/material.dart';

class AppSpacing {
  static const double s8 = 8;
  static const double s16 = 16;
}

class AppColors {
  static const primary = Color(0xFF007AFF);
  static const text = Colors.black;
}

class AppText {
  static const price = TextStyle(fontSize: 16, fontWeight: FontWeight.bold);
}
```

**示例 UI（product_page.dart，含故意错误）**：

```dart
class ProductPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: Padding(
          padding: EdgeInsets.all(12),    // ❌ 故意错误：应为 AppSpacing.s16
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Image.network('https://via.placeholder.com/300'),
              SizedBox(height: AppSpacing.s16),
              Text("iPhone 15"),
              SizedBox(height: AppSpacing.s8),
              Text(
                "￥5999",
                style: TextStyle(fontSize: 14),  // ❌ 故意错误：应为 AppText.price
              ),
              SizedBox(height: AppSpacing.s16),
              ElevatedButton(onPressed: () {}, child: Text("加入购物车")),
            ],
          ),
        ),
      ),
    );
  }
}
```

**Golden Test（product_page_test.dart）**：

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:golden_toolkit/golden_toolkit.dart';
import '../../lib/ui/product_page.dart';

void main() {
  testGoldens('Product Page Golden Test', (tester) async {
    await loadAppFonts();
    await tester.binding.setSurfaceSize(Size(375, 812)); // 固定屏幕尺寸
    await tester.pumpWidgetBuilder(ProductPage());
    await tester.pumpAndSettle();                        // 等动画完成
    await screenMatchesGolden(tester, 'product_page');
  });
}
```

**Layer 2 截图容差比对脚本（compare.py）**：

```python
# 课程使用轻量 Python 脚本实现 Layout 级容差比对
# 商业替代：Applitools / Percy（需外部账号，作为进阶扩展介绍）
from PIL import Image, ImageChops
import numpy as np, sys

def compare(baseline: str, current: str, threshold: float = 0.02):
    base = np.array(Image.open(baseline).convert("RGB"), dtype=float)
    curr = np.array(Image.open(current).convert("RGB"), dtype=float)
    diff = np.abs(base - curr).mean() / 255
    status = "PASS" if diff < threshold else "FAIL"
    print(f"[{status}] diff={diff:.4f} threshold={threshold}")
    return status == "PASS"

if __name__ == "__main__":
    ok = compare(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
```

> **商业工具扩展**：如需更完善的 Layout 级语义比对，可替换为 Applitools（`@applitools/eyes-playwright`）或 Percy（`npx percy snapshot`），原理相同，效果更精准，但需要外部账号。

### 5.5 演示脚本（三步对比）

**第一步：生成基准**
```bash
flutter test --update-goldens test/golden/
# → 生成 goldens/product_page.png（此时代码正确，对齐 Figma）
```

**第二步：引入错误，运行 Golden**
```bash
# 修改 product_page.dart：padding 改 12，字体改 14
flutter test test/golden/
# → FAIL：两类问题均被捕获
```

**第三步：运行 Layer 2 容差比对**
```bash
python test/visual_diff/compare.py \
  test/golden/goldens/product_page.png \
  test/golden/failures/product_page.png
# → padding FAIL（像素差超阈值），字体 PASS（2px 差异在容差范围内）
```

> **扩展演示**：如需展示商业工具效果，可同步介绍 Applitools Layout 模式的语义比对能力（需提前配置账号）。

**讲师话术**：
> "Golden Test 是像素级契约——有任何变化就报错，不会漏，但会误报字体渲染的细微差异。Layer 2 的容差比对是视觉语义契约——通过设置阈值自动过滤不影响布局的噪音。两者组合使用，才能在'不漏报'和'不误报'之间取得平衡。Applitools/Percy 等商业工具把这个能力做得更精准，感兴趣的同学课后可以探索。"

### 5.6 整体局限性（必须对学员讲清楚）

1. **视觉验收只能捕获"是否变了"，无法判断"变了是否更好"** — 定稿权永远在人手里（HITL）
2. **Golden 对 CI 环境敏感** — macOS 和 Linux 的字体渲染不同，必须在固定环境（Docker）运行，否则会随机误报
3. **Layer 2 商业工具有成本** — Applitools/Percy 功能更强但需外部账号；课程使用轻量 Python 脚本替代；企业评估时可考虑 Chromatic 或自建 diff 服务
4. **AI 分析（Layer 3）存在幻觉风险** — 输出仅作参考，不能作为自动化通过/拒绝的依据
5. **Layer 4 规则引擎何时值得引入** — 设计系统已成熟、Token 被 AI 频繁误用时才值得建设

### 5.7 稳定性检查清单（避免随机失败）

| 检查项 | 正确做法 |
|--------|---------|
| 字体加载 | `await loadAppFonts()` |
| 屏幕尺寸 | `setSurfaceSize(Size(375, 812))` 固定设备尺寸 |
| 动画完成 | `pumpAndSettle()` 代替 `pump()` |
| 网络图片 | 测试中替换为本地 Asset，不依赖网络 |
| CI 环境 | 统一使用 Docker 镜像运行，固定渲染环境 |

---

## 六、与 CI 集成（进阶）

将 `golden-check` Skill 集成到 GitHub Actions：

```yaml
- name: Run Golden Tests (Layer 1)
  run: flutter test test/golden/

- name: Run Visual Diff (Layer 2)
  run: python test/visual_diff/compare.py baseline.png current.png

# 可选：接入商业工具（需配置账号）
# - name: Upload to Applitools/Percy on PR
#   run: node test/applitools/upload.js
#   env:
#     APPLITOOLS_API_KEY: ${{ secrets.APPLITOOLS_KEY }}
```

**效果**：每次 PR 自动触发视觉回归检查，设计师和 PM 可直接在 PR 页面审阅视觉 diff，不再需要手工截图对比。

---

## 七、每日产出物

### Day 1 产出

| 产出物 | 说明 |
|--------|------|
| PRD.md | AI 生成 + 人工精化的产品需求文档 |
| SPEC.md | 迭代 1+2 的可执行规格，含功能验收标准 + 视觉验收 AC |
| design_system.md | 从 Figma 设计稿 AI 提取的设计系统规范（颜色/字体/间距）|
| docs/designs/ | Figma 参考图归档（Golden 基准参照）|
| CLAUDE.md | 含 SDD 约束的项目级 Agent 指令文件 |
| 6 个 Skills | build-check / golden-check / api-check / seed-data / spec-validate / cr-refactor |
| 可运行的迭代 1 代码 | Flutter 首页 + Python 后端 API，含 Golden 基准图和 CR 后的重构版本 |

### Day 2 产出

| 产出物 | 说明 |
|--------|------|
| 迭代 2 代码 | 剧集详情 + video_player 播放器，含 ADR + Golden 视觉验收回归记录 |
| 迭代 3 代码 | 首页改版 + 播放器增强 + Auth 增强，含变更 Spec 和完整回归测试 |
| AI 编程最佳实践清单 | 从实战提炼，可直接带回团队分享 |
| SDD 工作流模板 | SPEC.md 格式 + CLAUDE.md 规范模板，可复用 |
| 视觉验收 Demo 代码 | Flutter + Golden + 截图容差比对四层体系完整代码，含演示脚本（可扩展至 Applitools/Percy）|

---

## 九、AI 编程核心经验详解（对应大纲 1.2）

> 大纲中仅列标题，此处为讲师演示的完整内容与话术要点。

1. **把需求写成结构化 Prompt，而不是口头描述**
   明确 I/O、边界条件、约束（性能要求、禁用库、适配环境）、异常处理。Vibe Coding 的质量 = 约束清晰度——描述越模糊，生成质量越随机。
   > 演示对比：`"做个登录功能"` vs `"POST /api/auth/login，输入 email+password，返回 JWT；密码错误返回 401 且不暴露具体原因；网络超时保留输入内容"`

2. **设计先行，架构不能外包**
   先确定模块划分和数据流，再让 AI 填充实现。AI 生成速度 × 烂架构 = 更快制造垃圾。
   > 演示对比：有无 SPEC.md + 模块 README 时，AI 生成的首页代码在结构和命名上的差异

3. **小步拆解，每步可验证**
   太大的任务，人驾驭不了，模型也驾驭不了——上下文膨胀、方向漂移、结果失控。主动将大任务分解为每步有明确输出的子任务，或强制触发 Agent 规划（让模型先输出实施方案再执行），是 SDD 落地的核心手法。
   > 示例拆解：交易系统 → Step1 数据结构 → Step2 核心函数 → Step3 接口层 → Step4 异常处理

4. **用好 Git，随时掌握节奏**
   每完成一个可运行的小步骤就 commit。面对大量修改但结果不满意时，能干净回退是最后的底气。养成"小步快跑 + 频繁提交"的习惯，而不是跑很远才发现方向错了。
   > 现场演示：`git log --oneline` 对比"一次性大提交"vs"小步提交"的回退成本差异

5. **必须看代码，Debug 要给足上下文**
   AI 的"信心"和代码质量无关，Vibe Coding 不看代码迟早翻车。Debug 时不要只贴报错，要提供：代码片段 + 输入数据 + 期望输出 + 实际输出 + 已尝试方案，减少 AI 的不确定性空间。
   > 演示：只贴报错 vs 给完整上下文，AI 给出答案的准确度对比

6. **代码量增长后及时重构**
   随着迭代积累，AI 倾向于在已有复杂度上叠加，引入 tricky 的实现。要主动留意设计是否在退化，在"还能看懂"的时候就重构为下一轮迭代清场——等到混乱到难以读懂再重构，成本会急剧上升。
   > 时机判断：每轮迭代结束后运行 `cr-refactor` Skill，把重构纳入交付流程而非事后补救

7. **用 CLAUDE.md 固化约束，而不是每次在 Prompt 里重复**
   将命名规范、架构约束、代码风格写入 CLAUDE.md，让 AI 每次任务都自动遵循。
   > 演示对比：有无 CLAUDE.md 时生成代码的差异——颜色是否引用 Token、是否发生跨模块直接调用

8. **管理好 Session 和上下文窗口**
   上下文窗口是有限资源，长 Session 积累的无关信息会稀释模型注意力。学会在合适时机开启新 Session、使用 `/clear` 或 `/compact` 压缩上下文、必要时主动唤起 Sub-Agent 处理子任务，把核心上下文留给最重要的事。
   > 实操原则：一个 Session 聚焦一个功能模块；跨模块任务拆成多个 Session 或用 Sub-Agent

9. **分清执行类和架构类任务，善用对比提问**
   写代码/改 bug 是执行类，设计模块/分层是架构类，不要在同一个 Prompt 里混用。需要决策时用"方案 A vs 方案 B + trade-off 分析"，AI 最擅长比较，而不是拍脑袋给最优解。
   > 示例提问："SQLite 直接查询 vs 引入 Repository 层，在这个项目规模下各自的 trade-off 是什么？"

10. **保持人类最终裁决权（HITL）**
    架构决策、安全逻辑（Token 处理、权限设计）、验收标准永远不能外包给 AI。AI 输出是草稿，人工确认是终态；边界条件、隐性 bug、安全漏洞——最终责任在人。
    > HITL 三条红线：架构决策必须人审、安全代码必须人审、Golden 基准必须人确认

---

## 十、知识点覆盖索引（对照 AI-Native.md）

| AI-Native 知识体系 | 课程对应环节 |
|-------------------|------------|
| 1.1 大模型能力演进 | 模块 1 理论 |
| 1.2 工程师角色重塑 / SDD | 模块 1 + Step 2 + Step 7（SDD 工作流）|
| 2.1 S-P-A 架构 | 模块 1 |
| 2.2 Skills & Tools | Step 7 + 全程使用 + Deep Dive Block 2 |
| 3.1 Discovery & Spec | Step 1–4 |
| 3.2 UI Prototype / Figma | Step 4（Figma 导入 + 视觉验收体系）|
| 3.3 Repo as Agent's OS | Step 5–6 + Step 8–14 + Step 16–17 |
| 3.4 测试与自愈 | Step 11 / 14 / 18（[测试自愈]）|
| 3.5 AIOps / RCA | Step 18 + Deep Dive Block 1 |
| 4.1 架构层模块化 | Step 5 |
| 4.2 文档层 Standardized MD | Step 6 + CLAUDE.md 贯穿全程 |
| 4.3 Architecture as Code | Step 14 CR + Deep Dive Block 3 |
| 4.4 经验层知识注入 | Step 16–17 + Deep Dive Block 3 |
| 4.5 约束层 SDD 固化 | Step 7（SDD 工作流）+ Step 15 |
| 5.x 工具全景图 | 模块 1 工具链定位 |
