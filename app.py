from flask import Flask, redirect, abort, render_template
from flask import url_for
from werkzeug.exceptions import HTTPException
import os
import sys
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
import click


app = Flask(__name__)

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控

db = SQLAlchemy(app) # 初始化扩展，传入程序实例 app

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

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



@app.route('/')
def index():
    user = User.query.first() #读取用户数据
    movies = Movie.query.all() # 读取所有电影
    return render_template('index.html', user=user, movies=movies)


@app.route('/user/<name>')
def user_page():
    return 'User Page'

@app.route('/test')
def test_url_for():
    print(url_for('hello')) #输出：/
    print(url_for('user_page', name='ayu')) #输出： /user/ayu
    print(url_for('test_url_for', num=2)) # 输出： /test?num=2
    return 'Test Page'

@app.route('/404')
def not_found():
    abort(404)

# @app.errorhandler(Exception)
# def all_exception_handler(e):
#     # 对于 HTTP 异常，返回自带的错误描述和状态码
#     # 这些异常类在 Werkzeug 中定义，均继承 HTTPException 类
#     if isinstance(e, HTTPException):
#         return e.description, e.code
#     # 一般异常
#     return 'Error', 500
