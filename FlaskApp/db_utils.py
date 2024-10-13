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


def get_class_id_by_teacher_name(name, lastName, middleName):
    conn = get_db_connection()
    cur = conn.cursor()
    if len(middleName) != 0:
        cur.execute(f"SELECT * FROM get_class_id_by_teacher_name('{name}','{lastName}','{middleName}')")
    else:
        cur.execute(f"SELECT * FROM get_class_id_by_teacher_name('{name}','{lastName}')")
    if (cur.rowcount == 0):
        result = 404
    else:
        result = cur.fetchone()
    cur.close()
    conn.close()
    return result


def get_class_list_by_classid(classid):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'''SELECT 
                s.FirstName,
                s.MiddleName,
                s.LastName,
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
    headers = tuple([i[0] for i in cur.description])
    result.insert(0, headers)
    cur.close()
    conn.close()
    return result


def get_subjects_by_teacher(name, lastName, middleName):
    conn = get_db_connection()
    cur = conn.cursor()
    if(len(middleName) != 0):
        cur.execute(f"""SELECT subjectname FROM subject
         WHERE subjectid IN
         (SELECT subjectid FROM teachersubject 
         WHERE  teacherid=(SELECT teacherid FROM teacher 
         WHERE firstname='{name}' and lastname='{lastName}' and middlename='{middleName}'))""")
    else:
        cur.execute(f"""SELECT subjectname FROM subject
         WHERE subjectid IN
         (SELECT subjectid FROM teachersubject 
         WHERE  teacherid=(SELECT teacherid FROM teacher 
         WHERE firstname='{name}' and lastname='{lastName}'))""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def get_grades_by_teacher(name, lastName, middleName):
    conn = get_db_connection()
    cur = conn.cursor()
    if len(middleName) != 0:
        cur.execute(f"""SELECT 
        (SELECT CONCAT_WS(' ', firstname, lastname, middlename) 
        FROM student WHERE studentid = G.studentid) as studentname,
        (SELECT subjectname FROM subject where subjectid=G.subjectid) as subject,
        G.date,
        G.grade 
        FROM grade G 
        WHERE teacherid = (SELECT teacherid FROM teacher 
        WHERE firstname='{name}' and lastname='{lastName}' and middlename='{middleName}')""")
    else:
        cur.execute(f"""SELECT 
               (SELECT CONCAT_WS(' ', firstname, lastname, middlename) 
               FROM student WHERE studentid = G.studentid) as studentname,
               (SELECT subjectname FROM subject where subjectid=G.subjectid) as subject,
               G.date,
               G.grade 
               FROM grade G 
               WHERE teacherid = (SELECT teacherid FROM teacher 
               WHERE firstname='{name}' and lastname='{lastName}')""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result
