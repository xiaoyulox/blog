import sqlite3
import os
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    # 优化SQLite性能
    conn.execute('PRAGMA journal_mode = WAL')
    conn.execute('PRAGMA synchronous = NORMAL')
    conn.execute('PRAGMA cache_size = -64000')
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建留言表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # 创建评论表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id)')
        
        conn.commit()
        print("✅ 数据库初始化成功！")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
    finally:
        conn.close()

# 文章相关函数
def get_post_by_id(post_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        post = cursor.fetchone()
        return dict(post) if post else None
    except Exception as e:
        print(f"查询文章失败: {e}")
        return None
    finally:
        conn.close()

def update_post(post_id, title, content):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE posts SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (title, content, post_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"更新文章失败: {e}")
        return False
    finally:
        conn.close()

def delete_post(post_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"删除文章失败: {e}")
        return False
    finally:
        conn.close()

# 评论相关函数
def get_comments_by_post_id(post_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, u.username 
            FROM comments c 
            JOIN users u ON c.author_id = u.id 
            WHERE c.post_id = ? 
            ORDER BY c.created_at ASC
        ''', (post_id,))
        comments = cursor.fetchall()
        return [dict(comment) for comment in comments]
    except Exception as e:
        print(f"获取评论失败: {e}")
        return []
    finally:
        conn.close()

def add_comment(content, author_id, post_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO comments (content, author_id, post_id) VALUES (?, ?, ?)',
            (content, author_id, post_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"添加评论失败: {e}")
        return False
    finally:
        conn.close()

def delete_comment(comment_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"删除评论失败: {e}")
        return False
    finally:
        conn.close()