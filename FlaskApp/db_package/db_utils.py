from configparser import ConfigParser
import psycopg2

urlconf = 'config/config.ini'
config = ConfigParser()
config.read(urlconf)
user_db = config['login_db']['user_db']
password_db = config['login_db']['password_db']
name_db = config['login_db']['database_name']


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database=name_db,
                            user=user_db,
                            password=password_db)
    return conn


# teacher
def get_class_id_by_teacher_name(fio):
    result = 0
    if len(fio) > 2:
        middlename = f",'{fio[2]}'"
    else:
        middlename = ''
    if len(fio) >= 2:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            name = fio[1]
            lastname = fio[0]
            cur.execute(f"SELECT * FROM get_class_id_by_teacher_name('{name}','{lastname}'{middlename})")
            result = cur.fetchone()
            cur.close()
            conn.close()
        except:
            result = 0
    return result


def get_class_list_by_classid(classid):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f'''SELECT
                    s.firstname,
                    s.middlename,
                    s.lastname,
                    CAST(s.BirthDate AS TEXT),
                    s.Gender,
                    s.Address,
                    s.PhoneNumber,
                    s.Email,
                    c.ClassName
                FROM
                    Student s
                JOIN
                    Class c ON s.ClassID = c.ClassID
                WHERE
                    s.CLASSID={classid}''')
        result = cur.fetchall()
        if (len(result) != 0):
            headers = tuple([i[0] for i in cur.description])
            result.insert(0, headers)
        else:
            result = 0
        cur.close()
        conn.close()
    except:
        result = 0
    return result


def get_subjects_by_teacher(fio):
    result = 0
    if len(fio) > 2:
        middlename = fio[2]
        query = f"and middlename='{middlename}'"
    else:
        query = ""
    if len(fio) >= 2:
        name = fio[1]
        lastname = fio[0]
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(f"""SELECT subjectname FROM subject
                     WHERE subjectid IN
                     (SELECT subjectid FROM teachersubject
                     WHERE  teacherid=(SELECT teacherid FROM teacher
                     WHERE firstname='{name}' and lastname='{lastname}' {query}))""")
            result = cur.fetchall()
            cur.close()
            conn.close()
        except:
            result = 0
    return result


def get_grades_by_teacher(fio):
    result = 0
    if len(fio) > 2:
        middlename = fio[2]
        query = f"and middlename='{middlename}'"
    if len(fio) >= 2:
        name = fio[1]
        lastname = fio[0]
        query = ""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(f"""SELECT
                   (SELECT CONCAT_WS(' ', firstname, lastname, middlename)
                   FROM student WHERE studentid = G.studentid) as studentname,
                   (SELECT classname FROM class
                   WHERE classid=(SELECT classid FROM student WHERE studentid=G.studentid)) as classname,
                   (SELECT subjectname FROM subject where subjectid=G.subjectid) as subject,
                   G.grade,
                   G.date
                   FROM grade G
                   WHERE teacherid = (SELECT teacherid FROM teacher
                   WHERE firstname='{name}' and lastname='{lastname}' {query})""")
            result = cur.fetchall()
            cur.close()
            conn.close()
        except:
            result = 0
    return result


def get_teacher_fio(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""SELECT lastname, firstname, middlename FROM teacher WHERE teacherid={id}""")
    fio = cur.fetchone()
    cur.close()
    conn.close()
    return fio


def Add_grade(json_data, teacherid, teacher_fio):
    fio = json_data['fio'].split()
    error = 0
    if len(fio) > 2:
        middlename = f"and middlename='{fio[2]}'"
    else:
        middlename = ""
    if len(fio) >= 2:
        subjects = [row[0] for row in get_subjects_by_teacher(teacher_fio)]
        if json_data['subject'] in subjects:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(f"""INSERT INTO grade (studentid, subjectid, date, grade, teacherid)
                VALUES (
                (SELECT studentid FROM student
                WHERE firstname='{fio[1]}' {middlename} and lastname='{fio[0]}'
                 and classid=(SELECT classid FROM class WHERE classname='{json_data['classname']}' LIMIT 1) LIMIT 1),
                (SELECT subjectid FROM subject
                WHERE subjectname='{json_data['subject']}' LIMIT 1),
                CURRENT_DATE,
                {json_data['grade']}, {teacherid})""")
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                error = e
            return error
        else:
            error = f"Вы не преподаёте {json_data['subject']}"
    else:
        error = f"Ученик {json_data['fio']} не найден"
    return error


# student
def get_student_info(student_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""SELECT S.firstname, S.middlename, S.lastname, S.birthdate, 
            S.gender, S.address, S.phonenumber, S.email, 
            (SELECT classname FROM class WHERE classid=S.classid),
                (SELECT CONCAT_WS(' ', firstname, lastname, middlename)
                FROM teacher
                WHERE teacherid=(SELECT teacherid FROM class WHERE classid=S.classid))
        FROM student S WHERE studentid={student_id}""")
        result = cur.fetchone()
        cur.close()
        conn.close()
    except:
        result = 0
    return result


def get_student_classmates(student_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""SELECT firstname, middlename, lastname, phonenumber, email
         FROM student WHERE classid=(SELECT classid FROM student WHERE studentid={student_id})""")
        result = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(e)
        result = 0
    return result


def get_student_grades(student_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""SELECT
           G.grade,
           (SELECT subjectname FROM subject where subjectid=G.subjectid) as subject,
           (SELECT CONCAT_WS(' ', firstname, lastname, middlename)
           FROM teacher WHERE teacherid = G.teacherid) as teachername,
           G.date
           FROM grade G
           WHERE studentid={student_id}""")
        result = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(e)
        result = 0
    return result


def get_class_by_class_name(class_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""SELECT firstname, middlename, lastname, phonenumber, email 
            FROM student 
            WHERE classid=(SELECT classid FROM class WHERE classname='{class_name}')""")
        class_tuple = cur.fetchall()
        cur.close()
        conn.close()
    except:
        class_tuple = 0
    return class_tuple


def get_student_grades_by_fio(fio):
    grades_tuple = 0
    if len(fio) > 2:
        middlename = fio['middlename']
        query = f"and middlename='{middlename}'"
    else:
        query = ""
    if len(fio) >= 2:
        try:
            name = fio['firstname']
            lastname = fio['lastname']
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(f"""SELECT studentid FROM student WHERE firstname='{name}'
             and lastname='{lastname}' {query}""")
            student_id = cur.fetchone()
            grades_tuple = get_student_grades(student_id[0])
            cur.close()
            conn.close()
        except:
            grades_tuple = 0
    return grades_tuple
