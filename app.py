import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin


DATABASE = 'flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/", methods=["POST", "GET"])
def index():
    return redirect(url_for('practice'))


@app.route("/practice", methods=["POST", "GET"])
def practice():
    return render_template('practice.html', menu=dbase.getStartMenu(), title='Общая информация')


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        deb = dbase.getUserByEmail(current_user.getEmail())
        type_user = deb[4]
        if type_user == 1:
            return redirect(url_for('user_profile'))
        else:
            return redirect(url_for('admin_profile'))

    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            deb = dbase.getUserByEmail(current_user.getEmail())
            type_user = deb[4]
            if type_user == 1:
                return redirect(url_for('user_profile'))
            else:
                return redirect(url_for('admin_profile'))
        flash("Неверная пара логин/пароль", "error")
    return render_template("login.html", menu=dbase.getStartMenu(), title="Авторизация")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['username']) > 3 and len(request.form['email']) > 3 \
            and len(request.form['psw']) > 3 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['username'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", menu=dbase.getStartMenu(), title="Регистрация")


@app.route("/user_profile")
@login_required
def user_profile():
    return render_template("user_profile.html", menu=dbase.getUserMenu(), title="Профиль пользователя")


@app.route("/admin_profile")
@login_required
def admin_profile():
    return render_template("admin_profile.html", menu=dbase.getAdminMenu(), title="Профиль администратора")


@app.route('/userava2/<user_id>', methods=["POST", "GET"])
@login_required
def userava(user_id):
    user = UserLogin().fromDB(user_id, dbase)
    img = user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route("/add_task", methods=["POST", "GET"])
@login_required
def addTask():
    if request.method == "POST":
        if len(request.form['task']) > 4 and len(request.form['disc']) > 4 and len(request.form['importance']) > 0:
            id_user = current_user.get_id()
            res = dbase.addTask(request.form['task'], request.form['disc'], request.form['importance'], id_user)
            if not res:
                flash('Ошибка добавления задания', category='error')
            else:
                flash('Задание добавлена успешно', category='success')
        else:
            flash('Ошибка добавления задания', category='error')

    return render_template('add_task.html', menu=dbase.getUserMenu(), title="Добавление задания")


@app.route("/delete/<task_id>", methods=["POST", "GET"])
@login_required
def delete_task(task_id):
    dbase.delete_task(task_id)
    return redirect(url_for('user_index'))


@app.route("/change_task/<task_id>", methods=["POST", "GET"])
@login_required
def change_task(task_id):
    task = dbase.getTaskById(task_id)
    desc = dbase.getDescriptionById(task_id)
    return render_template('change_user_task.html', menu=dbase.getUserMenu(), task=task[0], desc=desc[0], title='Редактирование задания:', id=task_id)


@app.route("/sort_tasks_imp")
@login_required
def sort_tasks_imp():
    id_user = current_user.get_id()
    tasks = dbase.getSortedTasksByImp(id_user)
    if not tasks[0]:
        return render_template('sort_tasks_imp.html', menu=dbase.getUserMenu(), tasks=[], title='У вас пока нет ни одного задания')
    return render_template('sort_tasks_imp.html', menu=dbase.getUserMenu(), tasks=tasks, title='Ваши задания')


@app.route("/task_complete/<task_id>", methods=["POST", "GET"])
@login_required
def task_complete(task_id):
    id_user = dbase.getIdUserFromIdTask(task_id)
    dbase.setTaskComplete(task_id)
    user_tasks = dbase.getAllTasksFromID(id_user[0])
    if not user_tasks[0]:
        return render_template('user_index.html', menu=dbase.getUserMenu(), tasks=[], title='У Вас пока нет заданий')
    return render_template('user_index.html', menu=dbase.getUserMenu(), tasks=dbase.getAllTasksFromID(current_user.get_id()), title='Ваши задания')


@app.route("/change_user_task/<task_id>", methods=["POST", "GET"])
@login_required
def change_user_task(task_id):
    if request.method == "POST":
        if len(request.form['task']) > 4 and len(request.form['disc']) > 2 and len(request.form['importance']) > 0:
            res = dbase.change_task(task_id, request.form['task'], request.form['disc'], request.form['importance'])
        else:
            flash('Ошибка изменения задания', category='error')
    return render_template("user_index.html", menu=dbase.getUserMenu(), tasks=dbase.getAllTasksFromID(current_user.get_id()), title='Ваши задания')

@app.route("/delete_users_task/<task_id>", methods=["POST", "GET"])
@login_required
def delete_users_task(task_id):
    id_user = dbase.getIdUserFromIdTask(task_id)
    dbase.delete_task(task_id)
    user_tasks = dbase.getAllTasksFromID(id_user[0])
    if not user_tasks[0]:
        return render_template('user_tasks.html', menu=dbase.getAdminMenu(), tasks=[], title='У пользователя пока нет заданий')
    return render_template('user_tasks.html', menu=dbase.getAdminMenu(), tasks=user_tasks, title='Задания пользователя')


@app.route("/delete_user/<user_id>", methods=["POST", "GET"])
@login_required
def delete_user(user_id):
    dbase.delete_user(user_id)
    return render_template("admin_index.html", menu=dbase.getAdminMenu(), users=dbase.getAllUsersExceptAdmin(), title='Все пользователи')


@app.route("/user_index")
@login_required
def user_index():
    user_id = current_user.get_id()
    tasks = dbase.getSortedTasksByTime(user_id)
    if not tasks[0]:
        return render_template('user_index.html', menu=dbase.getUserMenu(), tasks=[], title='У Вас пока нет ни одного задания')
    return render_template('user_index.html', menu=dbase.getUserMenu(), tasks=tasks, title='Ваши задания')


@app.route("/users_tasks/<id_user>", methods=["POST", "GET"])
@login_required
def show_user_task_from_id(id_user):
    tasks = dbase.getAllTasksFromID(id_user)
    if not tasks[0]:
        return render_template('user_tasks.html', menu=dbase.getAdminMenu(), tasks=[], title="У пользователя пока нет заданий")
    return render_template('user_tasks.html', menu=dbase.getAdminMenu(), tasks=tasks, title="Задания пользователя:")



@app.route("/admin_index")
@login_required
def admin_index():
    return render_template('admin_index.html', menu=dbase.getAdminMenu(), users=dbase.getAllUsersExceptAdmin(), title='Все пользователи')


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")
    if current_user.getName() == 'admin':
        return redirect(url_for('admin_profile'))
    return redirect(url_for('user_profile'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
