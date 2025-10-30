from flask import Flask, render_template, request, redirect, url_for, flash, session, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from models import (
    get_db_connection, 
    init_db, 
    get_comments_by_post_id, 
    add_comment, 
    delete_comment,
    get_post_by_id,
    update_post,
    delete_post
)
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# 设置静态文件缓存
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600

@app.after_request
def add_header(response):
    """添加缓存头"""
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=300'
    return response

# 初始化数据库
init_db()

def row_to_dict(row):
    """将 sqlite3.Row 对象转换为字典"""
    return dict(row) if row else None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # 使用简单查询
        cursor.execute('''
            SELECT p.*, u.username 
            FROM posts p 
            JOIN users u ON p.author_id = u.id 
            ORDER BY p.created_at DESC
            LIMIT 20
        ''')
        posts = cursor.fetchall()
        posts = [row_to_dict(post) for post in posts]
    except Exception as e:
        print(f"查询留言失败: {e}")
        posts = []
    finally:
        conn.close()
    
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def show_post(post_id):  # 重命名避免冲突
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, u.username 
            FROM posts p 
            JOIN users u ON p.author_id = u.id 
            WHERE p.id = ?
        ''', (post_id,))
        post = row_to_dict(cursor.fetchone())
    except Exception as e:
        print(f"查询留言详情失败: {e}")
        post = None
    finally:
        conn.close()
    
    if post is None:
        flash('留言不存在!', 'danger')
        return redirect(url_for('index'))
    
    # 获取评论
    comments = get_comments_by_post_id(post_id)
    
    return render_template('post.html', post=post, comments=comments)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'user_id' not in session:
        flash('请先登录!', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author_id = session['user_id']
        
        if not title or not content:
            flash('标题和内容不能为空!', 'danger')
            return redirect(url_for('create'))
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)',
                (title, content, author_id)
            )
            conn.commit()
            flash('留言创建成功!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            print(f"创建留言失败: {e}")
            flash('创建留言失败!', 'danger')
        finally:
            conn.close()
    
    return render_template('create.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('用户名和密码不能为空!', 'danger')
            return redirect(url_for('register'))
        
        if len(username) < 3:
            flash('用户名至少需要3个字符!', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('密码至少需要6个字符!', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, hashed_password)
            )
            conn.commit()
            flash('注册成功! 请登录。', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('用户名已存在!', 'danger')
        except Exception as e:
            print(f"注册失败: {e}")
            flash('注册失败!', 'danger')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = row_to_dict(cursor.fetchone())
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('登录成功!', 'success')
                return redirect(url_for('index'))
            else:
                flash('用户名或密码错误!', 'danger')
        except Exception as e:
            print(f"登录失败: {e}")
            flash('登录失败!', 'danger')
        finally:
            conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('已退出登录!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        flash('请先登录!', 'danger')
        return redirect(url_for('login'))
    
    # 获取文章信息
    post = get_post_by_id(post_id)
    if not post:
        flash('留言不存在!', 'danger')
        return redirect(url_for('index'))
    
    # 检查权限：只能编辑自己的留言
    if post['author_id'] != session['user_id']:
        flash('你只能编辑自己的留言!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title or not content:
            flash('标题和内容不能为空!', 'danger')
            return redirect(url_for('edit_post', post_id=post_id))
        
        if update_post(post_id, title, content):
            flash('留言更新成功!', 'success')
            return redirect(url_for('show_post', post_id=post_id))
        else:
            flash('更新失败!', 'danger')
    
    return render_template('edit.html', post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post_route(post_id):  # 重命名避免冲突
    if 'user_id' not in session:
        flash('请先登录!', 'danger')
        return redirect(url_for('login'))
    
    # 获取留言信息
    post = get_post_by_id(post_id)
    if not post:
        flash('留言不存在!', 'danger')
        return redirect(url_for('index'))
    
    # 检查权限：只能删除自己的留言
    if post['author_id'] != session['user_id']:
        flash('你只能删除自己的留言!', 'danger')
        return redirect(url_for('index'))
    
    if delete_post(post_id):
        flash('留言删除成功!', 'success')
    else:
        flash('删除失败!', 'danger')
    
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment_route(post_id):
    if 'user_id' not in session:
        flash('请先登录!', 'danger')
        return redirect(url_for('login'))
    
    content = request.form['content']
    if not content:
        flash('评论内容不能为空!', 'danger')
        return redirect(url_for('show_post', post_id=post_id))
    
    if add_comment(content, session['user_id'], post_id):
        flash('评论发布成功!', 'success')
    else:
        flash('评论发布失败!', 'danger')
    
    return redirect(url_for('show_post', post_id=post_id))

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment_route(comment_id):
    if 'user_id' not in session:
        flash('请先登录!', 'danger')
        return redirect(url_for('login'))
    
    if delete_comment(comment_id):
        flash('评论删除成功!', 'success')
    else:
        flash('评论删除失败!', 'danger')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'user_id' not in session:
        return {'error': '请先登录'}, 403
    
    if 'image' not in request.files:
        return {'error': '没有选择文件'}, 400
    
    file = request.files['image']
    if file.filename == '':
        return {'error': '没有选择文件'}, 400
    
    if file and allowed_file(file.filename):
        # 创建上传目录
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 添加时间戳避免重名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 返回图片URL
        image_url = url_for('static', filename=f'uploads/{filename}')
        return {'url': image_url}
    
    return {'error': '不支持的文件格式'}, 400

if __name__ == '__main__':
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=True,  # 暂时开启调试模式
        threaded=True
    )
@app.route('/test-effects')
def test_effects():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>效果测试</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='css/mouse-effects.css') }}">
    </head>
    <body style="margin: 0; padding: 50px; background: #1a1a1a; color: white; font-family: Arial;">
        <h1>效果测试页面</h1>
        <p>移动鼠标查看拖尾效果</p>
        <p>点击页面查看点击效果</p>
        <button onclick="toggleRain()" style="padding: 10px 20px; font-size: 16px; margin: 10px;">切换下雨效果</button>
        <button onclick="location.reload()" style="padding: 10px 20px; font-size: 16px; margin: 10px;">重新加载</button>
        
        <script src="{{ url_for('static', filename='js/mouse-effects.js') }}"></script>
        <script>
            let rain = null;
            
            function toggleRain() {
                if (!rain) {
                    initRainEffect();
                    rain = true;
                    console.log('下雨效果开启');
                } else {
                    stopRainEffect();
                    rain = null;
                    console.log('下雨效果关闭');
                }
            }
            
            // 确保控制台可以访问这些函数
            console.log('测试页面加载完成');
            console.log('可用函数:', { initMouseEffects, initRainEffect, stopRainEffect });
        </script>
    </body>
    </html>
    '''