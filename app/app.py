from flask import Flask, render_template
import pymysql.cursors
from env import env
from flask_caching import Cache
import threading, time
from datetime import datetime

app = Flask(__name__)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

def last():
    out = ""
    connection = pymysql.connect(host='mysql.netsoc.co',
                             user=env.username,
                             password=env.password,
                             db=env.db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM `info`")
            r = cursor.fetchone()
            lastUpdate = datetime.strptime(r["current"], "%Y-%m-%d %H:%M:%S")
            c = datetime.now()
            diff = c - lastUpdate

            diff = int(diff.total_seconds())

            if diff//3600 > 0:
                out = f'{diff//3600} hour'
                out += "s" if diff//3600 != 1 else ""
            elif diff//60 > 0:
                out = f'{diff//60} minute'
                out += "s" if diff//60 != 1 else ""
            else:
                out = f'{diff} second'
                out += "s" if diff !=1 else ""

    finally:
        connection.close()
        return out

class Note:
    def __init__(self, name, url):
        self.name = name
        self.url = url

class Table:
    def __init__(self, name, id, url, prefix, notes):
        self.name = name
        self.id = id
        self.url = url
        self.prefix = prefix
        self.notes = notes

class Course:
    def __init__(self, id, url, name, tables):
        self.id = id
        self.url = url
        self.name = name
        self.tables = tables

@cache.cached(timeout=100, key_prefix="queries")
def queries():
    connection = pymysql.connect(host='mysql.netsoc.co',
                             user=env.username,
                             password=env.password,
                             db=env.db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `courses`"
            cursor.execute(sql)
            coursesQ = cursor.fetchall()
            courses = []
            for i, course in enumerate(coursesQ):
                courses.append(Course(course["id"], course["url"], course["name"], []))
                
                cursor.execute("SELECT name, id, url, prefix FROM `tables` WHERE id = %s", (courses[i].id))

                tables = cursor.fetchall()

                for it, t in enumerate(tables):
                    courses[i].tables.append(Table(t["name"], t["id"], t["url"], t["prefix"], []))

                    cursor.execute("SELECT name, url FROM `notes` WHERE `id` = %s AND `table` = %s", (t["id"], t["name"]))

                    notes = cursor.fetchall()

                    cursor.execute("SELECT * FROM `additions` WHERE `id` = %s AND `table`= %s", (t["id"], t["name"]))

                    addits = cursor.fetchall()
                    for adds in addits:
                        courses[i].tables[it].notes.append(Note(adds["name"], adds["url"]))

                    for n in notes:
                        courses[i].tables[it].notes.append(Note(n["name"], n["url"]))

                    
            return courses


    finally:
        connection.close()

queries()

def recache():
    while 1:
        queries()
        time.sleep(80)
    

th = threading.Thread(target=recache, args=(), kwargs={})
th.start()

@app.route('/')
@cache.cached(30)
def index():
    courses = queries()
    difference = last()

    name = "CK401 2022 NOTES INDEX"

    return render_template("index.html", name=name, courses=courses, dif=difference)
