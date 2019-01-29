from flask import Flask, redirect, abort, render_template
from flask import url_for
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html',
                           name=name,
                           movies=movies)


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
