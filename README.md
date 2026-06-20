# QMaster — 企业问卷调查系统

> 14 种题型 | 拖拽排序 | 评分模式 | 可视化统计 | 蓝色主题 | Docker 一键部署

## 快速开始

### Docker 部署（推荐）

```bash
# 1. 复制环境变量
cp .env.example .env
# 编辑 .env 修改密码和密钥

# 2. 一键启动
docker compose up -d

# 3. 创建管理员
docker compose exec backend python manage.py createsuperuser

# 4. 访问
# 前端: http://localhost:8088
# 管理后台: http://localhost:8088/admin
```

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# 前端
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Django 5.1 + Django REST Framework |
| 前端 | Vue 3 (Composition API) + Vite 6 |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7 |
| 图表 | ECharts 5 |
| 拖拽 | vuedraggable |
| 部署 | Docker Compose |

## 功能

### 14 种题型

| 分类 | 题型 |
|------|------|
| 基础 | 单选、多选、填空（多行文本）、下拉 |
| 高级 | 评分、**拖拽排序**、量表、滑块 |
| 其他 | 日期/时间（可切换仅日期/仅时间/日期+时间）、文件上传、图片单选、图片多选 |
| 结构 | 分页、章节标题 |

### 高级功能

- **评分模式** — 每题和选项可设分值，自动计算总分
- **目标部门** — 独立 Tab 配置问卷推送范围，树形勾选部门
- **拖拽排序题** — 答题端直接拖拽排位，直观高效
- **日期/时间合并** — 三个模式切换：日期+时间、仅日期、仅时间
- **样式设置** — 主题色、背景色、Logo、题头图、进度条、题型标签、分数显示
- **数据统计** — 柱状图、饼图、圆环图、条形图；应提交/已提交/未提交名单
- **Excel 导出** — 一键导出统计报表
- **分享链接 + 二维码** — 扫码即可填写
- **Django Admin 后台** — 完整数据管理
- **题库系统** — 7 大类题目模板
- **部门组织架构** — 树形部门管理 + CSV 批量导入
- **移动端自适应** — 手机浏览器自动适配

## 项目结构

```
qmaster/
├── docker-compose.yml          # Docker 编排
├── .env                        # 环境变量
├── backend/                    # Django 后端
│   ├── apps/
│   │   ├── users/              # 用户系统（角色权限）
│   │   ├── surveys/            # 问卷 / 题目 / 选项 CRUD
│   │   ├── responses/          # 提交 / 答案 / 统计 API
│   │   ├── templates_app/      # 问卷模板库
│   │   └── bank/               # 题库
│   └── config/                 # Django 配置（settings / urls / wsgi）
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── views/              # 页面
│       │   ├── IndexView.vue   # 首页（功能卡片）
│       │   ├── HomeView.vue    # 问卷管理（编辑/目标/样式/统计）
│       │   ├── DisplayView.vue # 问卷填写端（公开）
│       │   ├── TasksView.vue   # 答题任务端
│       │   ├── DepartmentView.vue  # 部门管理
│       │   ├── TemplateView.vue    # 模板浏览
│       │   ├── LoginView.vue   # 登录
│       │   ├── RegisterView.vue# 注册
│       │   ├── ProfileView.vue # 个人中心
│       │   └── ThankYouView.vue# 提交完成页
│       ├── components/
│       │   ├── survey/         # SurveyEditor / StylePanel / PublishDeptNode
│       │   ├── statistics/     # StatisticsPanel
│       │   ├── layout/         # AppHeader
│       │   └── common/         # DeptNode / DeptCascadeNode
│       ├── api/                # Axios API 封装
│       ├── stores/             # Pinia 状态管理
│       └── styles/             # CSS 变量 + 全局样式
└── nginx/                      # Nginx 配置
```

## 角色权限

| 角色 | 编号 | 权限 |
|------|:--:|------|
| 总管理 | 1 | 全部权限：创建/编辑/发布/删除问卷、管理用户和部门 |
| 管理员 | 2 | 创建/编辑/发布/删除问卷、管理所辖部门及成员 |
| 用户 | 3 | 仅答题 |
