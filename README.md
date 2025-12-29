# 情感识别系统

一个基于Django开发的情感识别系统，支持上传图片和摄像头实时识别。

## 项目结构

```
emotion_detection/
├── emotion_app/                  # 主应用目录
│   ├── __pycache__/              # Python编译缓存
│   ├── migrations/               # 数据库迁移文件
│   │   ├── __pycache__/          # 迁移文件编译缓存
│   │   ├── 0001_initial.py       # 初始迁移
│   │   ├── 0002_remove_emotionrecord_image_path.py  # 移除图片路径字段
│   │   ├── 0003_userprofile.py    # 用户配置文件模型
│   │   ├── 0004_auto_20251228_1601.py  # 自动生成的迁移
│   │   ├── 0005_remove_theme_and_language.py  # 移除主题和语言字段
│   │   ├── 0006_add_image_fields.py  # 添加图片字段
│   │   ├── 0007_add_recycle_bin_days.py  # 添加回收站天数设置
│   │   └── __init__.py
│   ├── templates/                # 模板文件
│   │   └── emotion_app/          # 应用模板
│   │       ├── base.html         # 基础模板
│   │       ├── camera_detection.html  # 摄像头识别页面
│   │       ├── change_password.html  # 修改密码页面
│   │       ├── index.html        # 首页（上传识别）
│   │       ├── login.html        # 登录页面
│   │       ├── profile.html      # 个人资料页面
│   │       ├── records.html      # 历史记录页面
│   │       ├── register.html     # 注册页面
│   │       └── welcome.html      # 欢迎页面
│   ├── __init__.py
│   ├── admin.py                  # Django后台管理配置
│   ├── apps.py                   # 应用配置
│   ├── models.py                 # 数据模型
│   ├── tests.py                  # 测试文件
│   ├── urls.py                   # 应用路由
│   └── views.py                  # 视图函数
├── emotion_detection/            # 项目配置目录
│   ├── __pycache__/              # Python编译缓存
│   ├── __init__.py
│   ├── asgi.py                   # ASGI配置
│   ├── settings.py               # 项目设置
│   ├── urls.py                   # 项目路由
│   └── wsgi.py                   # WSGI配置
├── media/                        # 媒体文件目录（图片等）
├── manage.py                     # Django管理脚本
└── README.md                     # 项目说明文档
```

## 主要功能

1. **用户管理**
   - 用户注册、登录、登出
   - 个人资料管理
   - 密码修改
   - 自定义回收站保管时间

2. **情感识别**
   - 上传图片识别
   - 摄像头实时识别
   - 识别记录管理

3. **历史记录**
   - 查看历史识别记录
   - 软删除（放入回收站）
   - 回收站功能
   - 批量操作

4. **管理员功能**
   - Django自带后台管理
   - 用户管理
   - 记录管理

## 技术栈

- **后端**: Django 5.2.9
- **数据库**: MySQL
- **前端**: HTML, CSS, JavaScript
  - **情感识别**: 自定义Python小模型

## 快速开始

### 安装依赖

```bash
# 安装Python依赖（假设已创建虚拟环境）
pip install -r requirements.txt
```

### 配置数据库

1. 修改 `emotion_detection/settings.py` 中的数据库配置
2. 创建数据库 `emotion_detection`

### 运行迁移

```bash
python manage.py migrate
```

### 创建超级用户

```bash
python manage.py createsuperuser
```

### 运行服务器

```bash
python manage.py runserver
```

### 访问应用

- 前台: http://127.0.0.1:8000/
- 后台: http://127.0.0.1:8000/admin/

## 项目特点

1. **图片存储**: 图片数据存储在数据库中，使用BinaryField
2. **软删除机制**: 记录删除后进入回收站，支持恢复
3. **用户自定义**: 支持自定义回收站保管时间
4. **响应式设计**: 适配不同设备
5. **消息提示**: 5秒自动消失的消息提示

## 许可证

MPL
