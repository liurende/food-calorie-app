# 食物热量拍照识别 App

通过多角度拍照识别食物，估算重量并计算热量。支持 50+ 种常见中餐及国际食物。

## 技术栈

- **前端：** React + TypeScript + Vite（移动端优先，iOS 风格浅色主题）
- **后端：** FastAPI（Python）
- **数据库：** SQLite
- **AI：** ONNX 本地分类（MobileNetV3）+ Anthropic Vision API 兜底
- **3D 重建：** OpenCV SIFT 特征匹配 + 三角测量 + 凸包体积估算

## 快速开始（Docker）

### 前置条件

- 安装 [Docker](https://www.docker.com/products/docker-desktop/) 并启动
- （可选）准备 ONNX 食物分类模型文件，放入 `backend/models/food_classifier.onnx`。没有模型文件也能运行，会自动使用模拟分类

### 方式一：docker-compose（推荐）

```bash
# 1. 克隆项目
git clone git@github.com:liurende/food-calorie-app.git
cd food-calorie-app

# 2. 构建并启动
docker-compose up -d

# 3. 初始化食物营养数据库（仅首次）
docker exec $(docker ps -qf "name=food-calorie") python seed_data.py

# 4. 打开浏览器访问
# http://localhost:8000
```

### 方式二：docker run

```bash
# 1. 克隆项目
git clone git@github.com:liurende/food-calorie-app.git
cd food-calorie-app

# 2. 构建镜像
docker build -t calorie-app .

# 3. 运行容器
docker run -d -p 8000:8000 \
  --name calorie-app \
  -v ./backend/models:/app/models \
  -v ./backend/uploads:/app/uploads \
  calorie-app

# 4. 初始化食物营养数据库（仅首次）
docker exec calorie-app python seed_data.py

# 5. 打开浏览器访问
# http://localhost:8000
```

### 停止和清理

```bash
# docker-compose 方式
docker-compose down

# docker run 方式
docker stop calorie-app && docker rm calorie-app
```

## 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
python seed_data.py          # 初始化数据库
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 前端（新终端）
cd frontend
npm install
npm run dev                   # http://localhost:5173

# 运行测试
cd backend
python -m pytest tests/ -v
```

## 使用说明

1. 打开应用，在"今天"页面点击"拍照记录餐食"
2. 按引导从 3 个角度（正面 0°、斜角 45°、侧面 90°）拍摄食物照片
3. 系统自动识别食物种类、估算体积和重量，计算热量和营养成分
4. 查看每日热量摄入环状图、历史记录和营养统计
5. 在"我的"页面填写身高体重等信息，自动计算 BMR 和 TDEE

## 项目结构

```
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── database.py          # SQLite 初始化与连接
│   ├── models.py            # Pydantic 数据模型
│   ├── seed_data.py         # 食物密度数据初始化
│   ├── routers/             # API 路由
│   │   ├── upload.py        # 图片上传
│   │   ├── recognize.py     # 识别 + 重量估算
│   │   ├── meals.py         # 餐食记录 CRUD
│   │   ├── stats.py         # 每日/每周统计
│   │   ├── foods.py         # 食物搜索
│   │   └── profile.py       # 用户信息 + BMR/TDEE
│   ├── engine/              # 重量估算引擎
│   │   ├── feature_matching.py  # SIFT 特征提取与匹配
│   │   ├── reconstruction.py    # 3D 重建与体积估算
│   │   └── weight.py           # 密度查询 -> 重量/热量
│   ├── ai/                  # AI 分类
│   │   ├── classifier.py       # ONNX 分类（模拟兜底）
│   │   └── fallback.py         # Vision API 兜底
│   └── tests/               # 后端测试
├── frontend/
│   └── src/
│       ├── pages/           # 页面组件
│       │   ├── TodayPage.tsx    # 今日概览
│       │   ├── CapturePage.tsx  # 多角度拍照
│       │   ├── ResultPage.tsx   # 识别结果
│       │   ├── HistoryPage.tsx  # 历史记录
│       │   └── ProfilePage.tsx  # 个人中心
│       ├── components/      # 通用组件
│       ├── api/client.ts    # API 请求封装
│       └── types.ts         # TypeScript 类型定义
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```
