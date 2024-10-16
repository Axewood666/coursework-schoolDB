from flask import Blueprint, render_template, request, flash, redirect, url_for

from flask_login import login_user, login_required, logout_user, current_user

from .requireds import teacher_required
import FlaskApp.db_package as db

pages = Blueprint('pages', __name__)


@pages.route("/")
def Main():
    return render_template('index.html', context="/")


@pages.route("/templates/menu.html")
def Menu():
    return render_template('menu.html')


@pages.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user_type = request.form['user_type']
        user = db.model.User.get_user(login, password, user_type)
        if user:
            login_user(user)
            return redirect(url_for('pages.Main'))
        flash('Invalid username or password')
    return render_template('login.html')


@pages.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.Main'))


@pages.route("/teacher")
def Teacher():
    return render_template('teacher/teacher.html', context="/teacher")


@pages.route("/profile/teacher")
@login_required
@teacher_required
def Teacher_profile():
    id_ = current_user.id.split('_')[1]
    fio = db.db_utils.get_teacher_fio(id_)
    return render_template("teacher/teacher-profile.html", fio=fio)
