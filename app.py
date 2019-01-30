from flask import Flask, redirect, abort, render_template,request, flash
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
app.config['SECRET_KEY'] = '123'
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

@app.context_processor
def inject_user(): #函数名随意
    user = User.query.first()
    return {'user':user}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': # 判断是否是 POST 请求
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


