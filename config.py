import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    # 使用 SQLite 数据库
    DATABASE_PATH = os.path.join(basedir, 'blog.db')
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 最大文件大小
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}