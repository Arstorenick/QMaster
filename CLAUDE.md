# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 构建与运行

```bash
# Docker（推荐）— 启动全部服务
docker compose up -d                                    # 启动
docker compose up -d --build                            # 重建并启动
docker compose up -d --build backend                    # 仅重建后端
docker compose up -d --build nginx                      # 仅重建前端
docker compose down                                     # 停止全部

# 后端管理命令
docker exec qmaster-backend-1 python manage.py migrate
docker exec qmaster-backend-1 python manage.py createsuperuser
docker exec qmaster-backend-1 python manage.py collectstatic --noinput

# 数据库直查
docker exec qmaster-db-1 mysql -u qmaster -pqmaster123 qmaster -e "SELECT ..."

# 前端本地开发（不依赖 Docker）
cd frontend && npm install && npm run dev               # http://localhost:5173
cd frontend && npm run build                            # 生产构建
```

**访问地址：** 前端 `http://localhost:8088` | 管理后台 `http://localhost:8088/admin/` | API `http://localhost:8000/api/`

## 架构概览

### 后端（Django 5.1 + DRF）

- **`backend/config/`** — Django 配置，URL 路由分发到五个子应用
- **`backend/apps/users/`** — 自定义 User 模型，三级角色：`1=总管理`、`2=管理员`、`3=用户`。关键属性：`is_super_admin`（role=1）、`is_creator`（role∈{1,2}）。User 有 `department` 外键（所属部门）和 `managed_department` 外键（管理员管辖范围）。部门数据用递归树结构，包含 `get_descendant_ids()` 方法和树形/扁平序列化器
- **`backend/apps/surveys/`** — Survey（问卷）、Question（题目，14 种类型）、Option（选项）。Question 的 `config` 是 JSONField，存放题型特定配置（行数、模式、量表等）。Survey 的 `style` 也是 JSONField。关键端点：问卷 CRUD、发布/停止、复制、题目拖拽排序、样式更新
- **`backend/apps/responses/`** — Submission（提交记录）+ Answer（答案）。统计 API 返回聚合数据供图表使用。支持 Excel 导出
- **`backend/apps/templates_app/`** — 模板库
- **`backend/apps/bank/`** — 题库

**特点：** 全部使用 `@api_view` 函数式视图，无类视图。序列化器更新均用 `partial=True`。环境变量通过 `python-decouple` 读取 `.env` 文件。

### 前端（Vue 3 + Vite 6 + Composition API）

- **`src/api/index.js`** — Axios 实例，含 CSRF 拦截器。导出：`surveysAPI`、`questionsAPI`、`optionsAPI`、`responsesAPI`、`departmentsAPI`、`profileAPI`、`bankAPI`、`templatesAPI`
- **`src/stores/auth.js`** — Pinia 状态管理，`auth.isCreator` 判断管理权限
- **`src/styles/variables.css`** — CSS 自定义属性：主色 `#2563EB`，间距体系（4-48px），圆角等级，阴影层级
- **`src/styles/global.css`** — 按钮体系（`.btn` / `.btn-primary` / `.btn-secondary` / `.btn-danger` / `.btn-ghost` / `.btn-sm` / `.btn-lg`），输入框 `.input`，卡片 `.card`，标签 `.tag`，表格 `.table`

### 页面职责

| 页面 | 文件 | 说明 |
|------|------|------|
| 首页 | `IndexView.vue` | 功能卡片展示，自定义 PNG 图标 |
| 问卷管理 | `HomeView.vue` | 核心页面：编辑题目/目标部门/样式设置/数据统计四个 Tab |
| 预览填写 | `DisplayView.vue` | 公开问卷填写端，使用 `--survey-theme` CSS 变量适配品牌色，支持跳转模式 |
| 答题任务 | `TasksView.vue` | 用户任务列表及问卷作答，支持跳转模式 |
| 部门管理 | `DepartmentView.vue` | 组织架构树、成员列表、批量改角色/部门、成员信息编辑、管理部门设置、CSV 导入 |
| 个人中心 | `ProfileView.vue` | 信息编辑、部门选择（管理员禁用）、角色只读 |

### 问卷编辑器（SurveyEditor.vue）

核心组件。三种模式切换：**正常模式** / **分值模式** / **跳转模式**。题型工具栏按钮渲染 `<img>`（自定义 PNG 图标）或 `<span>`（emoji 回退）。跳转模式下仅显示单选、下拉、图片单选。题目列表使用 `vuedraggable` 拖拽排序。每种题型有特定的预览区域。评分模式由 `toggleScoring` 事件控制，跳转模式由 `toggleSkip` 事件控制。选项通过 `updateOption()` 在失焦时保存——**必须包含 `score` 字段**（曾因遗漏导致分值不保存）。

### 跳转模式

- `Survey.skip_enabled` 控制开关，`Question.config.skip_rules` 存储规则（`{ option_id: target_question_id | null | -1 }`，-1=结束问卷）
- 编辑端每选项有跳转下拉，列出后续单选/下拉/图片单选题
- 答题端 `goNext()` 函数根据选中选项的跳转规则计算目标页

### 前端关键组件

- `StylePanel.vue` — 自定义开关样式（toggle-switch），`show_question_score` 控制预览端是否显示每题分值
- `StatisticsPanel.vue` — ECharts 图表（柱状/饼图/圆环/条形），三张统计卡片可点击展开人员名单
- `PublishDeptNode.vue` — 递归部门树组件，自定义复选框 + 展开箭头
- `SurveyQuestion.vue` — 共享题目渲染组件（DisplayView 和 TasksView 通用，但尚未完全接入）

### 设计约定

- **禁止 emoji 作为结构性图标** — 使用内联 SVG 或 `src/assets/` 下的自定义 PNG
- **蓝色主题 `#2563EB`** — 全局主色，问卷预览页的 `--survey-theme` 默认同色
- **工具栏固定** — HomeView 的 Tab 栏 + SurveyEditor 的模式栏/题型栏均固定在顶部，题目列表独立滚动（通过 `max-height: calc()` + `overflow:hidden` 实现）
- **弹窗** — 使用 `<Teleport to="body">` + `.modal-overlay` 遮罩层

### Nginx 路由（frontend/nginx.conf）

```
/assets/  → 前端构建产物
/static/  → Django 静态文件（SimpleUI 管理主题）
/media/   → 用户上传文件
/api/     → 代理至 backend:8000
/admin    → 301 重定向到 /admin/
/admin/   → 代理至 backend:8000
/         → SPA 回退（index.html）
```

### 常见陷阱

- **前端改了不生效？** 运行 `docker compose up -d --build nginx`，查看 Vite 构建输出是否有错
- **后端崩溃？** 查 `docker logs qmaster-backend-1`，通常是 `urls.py` 缺少函数导入或 views 缩进错误
- **`show_question_score` 勾了但预览看不到？** 三步排查：1) 样式是否保存成功 2) 数据库 `opt.score > 0` 3) `updateOption()` 是否发送了 `score` 字段
- **目标部门不可见？** 管理员需在 Django Admin 或部门成员编辑中设置 `managed_department`，否则默认回退到自身 `department` 的子树
- **管理员不能改自己的部门/角色/管理部门？** 前端禁用 + 后端 `AdminUserUpdateSerializer.validate_*` 双重保护
- **Profile 页部门/角色只读？** `auth.isCreator` 为 true 时禁用，普通用户仍可修改
- **跳转模式不生效？** 检查 `Survey.skip_enabled` 是否为 true，`Question.config.skip_rules` 是否有值
- **访问 /admin 跳到前端？** nginx 需要 `location = /admin { return 301 /admin/; }` 精确匹配块
- **SimpleUI 样式丢失？** 运行 `docker exec qmaster-backend-1 python manage.py collectstatic --noinput`
- **从旧版迁移用户角色 4？** `UPDATE users SET role=3 WHERE role=4;`（角色 4 已废弃），同时运行 `makemigrations` + `migrate`
