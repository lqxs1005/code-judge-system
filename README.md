# 智能题目生成与评测系统 - Flask 后端基础框架

## 技术栈
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Marshmallow
- MySQL

## 目录结构
```
app/
  __init__.py         # 应用工厂
  models.py           # 数据库模型
  extensions.py       # 扩展初始化
  config.py           # 配置
  api/
    __init__.py
    users.py          # 用户API蓝图
  utils/              # 工具函数
run.py                # 启动入口
requirements.txt      # 依赖
schema.sql            # 数据库建表SQL
```

## 启动方法
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 配置数据库连接（可修改 `app/config.py` 或设置环境变量 `DATABASE_URL`）。
3. 启动服务：
   ```bash
   python run.py
   ```
4. 访问用户API示例：
   - `GET /api/users/` 获取所有用户

## 说明
- 数据库表已由 schema.sql 创建，模型与表结构严格对应。
- 推荐使用 Flask-Migrate 进行迁移管理。
