# QMaster — 问卷调查系统

> 40+ 题型 | 可视化统计 | MySQL + Django + Vue 3 | Docker 一键部署

## 快速开始

### 前置条件
- Docker & Docker Compose
- 或：Python 3.12 + Node.js 20 + MySQL 8.0 + Redis

### Docker 部署（推荐）

```bash
# 1. 复制环境变量
cp .env.example .env
# 编辑 .env 修改密码和密钥

# 2. 一键启动
docker compose up -d

# 3. 访问
# 前端: http://localhost
# 管理后台: http://localhost/admin
# 默认管理员: python manage.py createsuperuser
```

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env  # 编辑数据库连接
python manage.py migrate
python manage.py createsuperuser
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
| 后端 | Django 5.1 + DRF |
| 前端 | Vue 3 (Composition API) + Vite |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7 |
| 图表 | ECharts 5 |
| 部署 | Docker Compose |

## 功能

### MVP 阶段 (17 种题型)
单选题、多选题、填空题、多行填空题、多项填空题、下拉单选题、评分题、排序题、日期题、时间题、文件上传题、分页、分段、量表题、滑块题、图片单选题、图片多选题

### 高级功能
- 17 项自定义样式（主题色/背景/Logo/进度条）
- 数据统计：柱状图/饼图/圆环图/条形图
- Excel 导出
- 问卷模板库
- 分享链接 + 二维码
- Django Admin 后台管理
- 题库系统（7 大类）
- 14 种表单验证
- 移动端自适应

## 项目结构

```
qmaster/
├── docker-compose.yml
├── .env
├── backend/           # Django 后端
│   ├── apps/
│   │   ├── users/     # 用户系统
│   │   ├── surveys/   # 问卷/题目/选项
│   │   ├── responses/ # 提交/答案/统计
│   │   ├── templates_app/  # 模板库
│   │   └── bank/      # 题库
│   └── config/        # Django 配置
├── frontend/          # Vue 3 前端
│   └── src/
│       ├── views/     # 页面
│       ├── components/# 组件
│       ├── api/       # API 封装
│       ├── stores/    # Pinia 状态
│       └── styles/    # CSS 设计系统
└── nginx/             # Nginx 配置
```

## 部署到内网 Linux 服务器

```bash
# 1. 服务器安装 Docker
curl -fsSL https://get.docker.com | bash

# 2. 上传项目到服务器
scp -r qmaster/ user@server:/opt/qmaster/

# 3. 启动
cd /opt/qmaster
docker compose up -d

# 4. 创建管理员
docker compose exec backend python manage.py createsuperuser
```
