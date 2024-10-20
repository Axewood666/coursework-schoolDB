import json

from flask import Blueprint, render_template, request, flash, redirect, url_for

from flask_login import login_user, login_required, logout_user, current_user

import FlaskApp.db_package as db

if __name__ == '__main__':
    from requireds import teacher_required, student_required, employee_required, staff_required
else:
    from .requireds import teacher_required, student_required, employee_required, staff_required

pages = Blueprint('pages', __name__)


@pages.route("/")
def main():
    return render_template('index.html', context="/")


@pages.route("/templates/menu.html", methods=['GET'])
def Menu():
    path = request.args.get('path', '/')
    return render_template('menu.html', context=path)


# login
@pages.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user_type = request.form['user_type']
        user = db.User.get_user(login, password, user_type, db.schoolDB)
        if user:
            login_user(user)
            if current_user.user_type == 'student':
                return redirect(url_for('pages.profile_student'))
            return redirect(url_for('pages.main'))
        flash('Invalid username or password')
    return render_template('login.html')


@pages.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.main'))


# teachers


@pages.route("/teacher")
@staff_required
def teacher():
    return render_template('teacher/teacher.html', context="/teacher")


@pages.route("/profile/teacher")
@teacher_required
def profile_teacher():
    id_ = current_user.id.split('_')[1]
    fio = db.schoolDB.get_teacher_fio(id_)
    return render_template("teacher/teacher-profile.html", fio=fio)


# student


@pages.route("/student")
@employee_required
def student():
    return render_template("student/student.html", context="/student")


@pages.route("/profile/student")
@student_required
def profile_student():
    student_data = db.schoolDB.get_student_info(current_user.id.split('_')[1])
    if student_data:
        fields = ['Имя', 'Отчество', 'Фамилия', 'Дата рождения', 'Пол', 'Адрес', 'Номер телефона', 'Электронная почта', \
                  'Класс', 'Классный руководитель']
        dicts_data = dict(zip(fields, student_data))
        dicts_data['Дата рождения'] = dicts_data['Дата рождения'].isoformat()
        dicts_data['error'] = 0
        json_student = json.dumps(dicts_data)
    else:
        dicts_data = dict()
        dicts_data['error'] = 1
        json_student = json.dumps(dicts_data)
    return render_template("student/student-profile.html", student=json_student)