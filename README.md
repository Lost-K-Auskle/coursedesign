# 情感识别系统

这是一个基于Django框架开发的情感识别Web应用，能够通过图像识别用户的情感状态，并提供用户管理、记录管理等功能。

## 功能特性

- **用户管理**：注册、登录、个人资料管理
- **情感识别**：上传图像或使用摄像头进行实时情感识别
- **识别记录**：查看历史识别记录，支持软删除功能
- **个人中心**：修改密码、设置回收站保管天数等

## 技术栈

- **后端**：Python 3.10+, Django 5.2.9
- **数据库**：MySQL 5.7+
- **图像处理**：Pillow
- **数据处理**：NumPy, Pandas
- **前端**：HTML5, CSS3, JavaScript

## 项目结构

```
coursedesign/
├── emotion_detection/        # Django项目主目录
│   ├── emotion_app/          # 情感识别应用
│   │   ├── migrations/       # 数据库迁移文件
│   │   ├── templates/        # HTML模板
│   │   ├── __init__.py
│   │   ├── admin.py          # 后台管理配置
│   │   ├── apps.py           # 应用配置
│   │   ├── models.py         # 数据模型
│   │   ├── tests.py          # 测试文件
│   │   ├── urls.py           # 路由配置
│   │   └── views.py          # 视图函数
│   ├── emotion_detection/    # 项目配置
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py       # 项目配置
│   │   ├── urls.py           # 根路由
│   │   └── wsgi.py
│   ├── manage.py             # Django管理脚本
│   └── requirements.txt      # 依赖列表
├── params/                   # 模型参数文件
├── valid_python_many.py      # 批量验证脚本
└── valid_python_single.py    # 单文件验证脚本
```

## 安装步骤

### 1. 环境准备

确保已安装以下软件：
- Python 3.10+
- MySQL 5.7+

### 2. 克隆项目

```bash
git clone https://github.com/Lost-K-Auskle/coursedesign.git
cd coursedesign
```

### 3. 安装依赖

```bash
cd emotion_detection
pip install -r requirements.txt
```

### 4. 数据库配置

1. 创建MySQL数据库：
```sql
CREATE DATABASE emotion_detection CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 修改`emotion_detection/settings.py`中的数据库配置（如果需要）：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'emotion_detection',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
    }
}
```

### 5. 数据库迁移

```bash
python manage.py migrate
```

### 6. 创建超级用户

```bash
python manage.py createsuperuser
```

## 运行项目

```bash
python manage.py runserver
```

### 访问应用

- 前台: http://127.0.0.1:8000/
- 后台: http://127.0.0.1:8000/admin/

## 使用说明

### 1. 注册与登录
- 首次使用需要注册账号
- 登录后进入个人主页

### 2. 情感识别
- 点击"实时识别"使用摄像头进行情感识别
- 或点击"上传图片"上传本地图片进行识别

### 3. 查看记录
- 点击"识别记录"查看历史识别结果
- 支持查看、删除记录

### 4. 个人中心
- 点击"个人资料"修改个人信息
- 点击"修改密码"更改登录密码
- 设置回收站保管天数（1-7天）

## 数据模型

### UserProfile（用户个人资料）
- 扩展Django默认User模型
- 包含个人简介、性别、头像等信息
- 支持自定义回收站保管天数

### EmotionRecord（情感识别记录）
- 记录用户的情感识别结果
- 包含情感类型、置信度、图片数据等信息
- 支持软删除功能

## 注意事项

1. 确保MySQL服务已启动
2. 首次运行需进行数据库迁移
3. 模型参数文件需放置在params目录下
4. 生产环境中需修改SECRET_KEY并关闭DEBUG模式

## License

MPL License
