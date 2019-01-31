from flask import Flask, redirect, abort, render_template,request, flash
from flask import url_for
from werkzeug.exceptions import HTTPException
import os
import sys
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
import click
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin

app = Flask(__name__)

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控
app.config['SECRET_KEY'] = '123'
db = SQLAlchemy(app) # 初始化扩展，传入程序实例 app
login_manager = LoginManager(app) # 实例化扩展类


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password): ## 用来设置密码的方法，接受密码作为参数
        # 将生成的密码保持到对应字段
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password): ## 用于验证密码的方法，接受密码作为参数
        # 返回布尔值
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))



@app.cli.command() #注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.') #设置选择
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database') #输出提示信息

@app.cli.command()
def forge():
    db.create_all()
    name = 'ayuLiao'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Fake Data Generate Done.')


@app.cli.command()
@click.option('--username', prompt=True, help='Admin Username')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin Password')
def admin(username, password):
    # create user
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password) # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password) # 设置密码
        db.session.add(user)
    db.session.commit()
    click.echo('Done.')


@login_manager.user_loader
def load_user(user_id): # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

@app.context_processor
def inject_user(): #函数名随意
    user = User.query.first()
    return {'user':user}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required # 只有登录后，才可以调用该方法
def logout():
    logout_user() #登出用户
    flash("Goodbye")
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET','POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form.get('name','')
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        # current_user 会返回当前登录用户的数据库记录对象
        current_user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html')



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': # 判断是否是 POST 请求
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        # 获取表单数据
        title = request.form.get('title') # 传入表单对应输入字段的 name 值
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item Created.')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item Updated.')
        return redirect(url_for('index'))
    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit() # 提交数据库会话
    flash('Item Deleted')
    return redirect(url_for('index'))


@app.route('/test')
def test_url_for():
    print(url_for('hello')) #输出：/
    print(url_for('user_page', name='ayu')) #输出： /user/ayu
    print(url_for('test_url_for', num=2)) # 输出： /test?num=2
    return 'Test Page'


@app.errorhandler(404)  # 传入要处理的错误代码
def not_found(e): # 接受异常对象作为参数
    # 返回模板和状态码
    return render_template('404.html'), 404


