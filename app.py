from flask import Flask,render_template,session,url_for,request,redirect
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask import jsonify,json
import os
import gspread
import webbrowser

from oauth2client.service_account import ServiceAccountCredentials
import pprint
import datetime
import argparse
import pickle

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'project'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/project'


mongo = PyMongo(app)
bcrypt = Bcrypt(app)


@app.route('/')
def index():
    return render_template("studentlogin.ejs",title="Student Login")

@app.route('/login', methods = ['POST','GET'])
def login():
    if  session.get('usernameS'):
        students = mongo.db.students
        login_user = students.find_one({"ID" : session.get('usernameS')})
        courses = login_user['courses']
        courses1 = mongo.db.courses
        obj = courses1.find_one({"courses" : courses[0]})
        global link
        link=obj['link']
        session['selected_course']=courses[0]
        return render_template('view_attendance.html',courses=courses,iframe1=link,link=link,x="Student",user=login_user['ID'],subject=obj['courses'])
    if request.method== 'POST':
        username = request.form['usernameS']
        pwd = request.form['pwdS']
        students = mongo.db.students
        login_user = students.find_one({"ID" : username})
        if login_user:
            password = login_user['password']
            if password==pwd:
                session['usernameS'] = username

                courses = login_user['courses']
                courses1 = mongo.db.courses
                obj = courses1.find_one({"courses" : courses[0]})
                link=obj['link']
                session['selected_course']=courses[0]
                return render_template('view_attendance.html',courses=courses,iframe1=link,link=link,x="Student",user=login_user['ID'],subject=obj['courses'])
            else:
                return render_template("studentlogin.ejs",title="Student Login",msg="The username or password is incorrect")
    else:
        webbrowser.open_new_tab(link)
        return render_template("studentlogin.ejs",title="Student Login")

@app.route('/facultylogin')
def faculty():
    return render_template("facultylogin.ejs",title="Faculty Login")

@app.route('/facultylogin', methods = ['POST','GET'])
def facultylogin():
        if  session.get('usernameF'):
            professors = mongo.db.professor
            login_user = professors.find_one({"ID" : session.get('usernameF')})
            courses = login_user['courses']
            courses1 = mongo.db.courses
            obj = courses1.find_one({"courses" : courses[0]})
            global link
            link=obj['link']
            session['selected_course']=courses[0]
            return render_template('mark_attendance.html',courses=courses,iframe=link,link=link,x="Faculty",user=login_user['ID'],subject=obj['courses'])

        if request.method== 'POST':
            username = request.form['usernameF']
            pwd = request.form['pwdF']
            professors = mongo.db.professor
            login_user = professors.find_one({"ID" : username})
            if login_user:
                password = login_user['password']
                if password==pwd :
                    session['usernameF'] = username
                    courses = login_user['courses']
                    courses1 = mongo.db.courses
                    obj = courses1.find_one({"courses" : courses[0]})
                    link=obj['link']
                    session['selected_course']=courses[0]
                    return render_template('mark_attendance.html',courses=courses,iframe=link,link=link,x="Faculty",user=login_user['ID'],subject=obj['courses'])
                else:
                    return render_template("facultylogin.ejs",title="Student Login",msg="The username or password is incorrect")			

@app.route('/getlink', methods=['POST','GET'])
def getlink():

    if request.method == 'GET':



        selected_course=request.args["selected_course"]

        session['selected_course']=selected_course
        courses = mongo.db.courses
        obj = courses.find_one({"courses" : selected_course})
        global link
        link=obj['link']
        loadlink()
        obj={
            'courses':selected_course,
            'link':link
        }
        return jsonify(obj)
    return 0
@app.route('/start_attendance',methods=['GET','POST'])
def start_attendance():
    if  session.get('usernameF'):
            professors = mongo.db.professor
            login_user = professors.find_one({"ID" : session.get('usernameF')})
            courses = login_user['courses']
            course1=mongo.db.courses
            selected = request.args.get('course')
            obj = course1.find_one({"courses" : selected})
            link=obj['link']
            import subprocess as s
            s.call("python face-rec-notebook.py --course " +selected,shell=True)
            return render_template('mark_attendance.html',courses=courses,iframe=link,link=link,x="Faculty",user=login_user['ID'],subject=obj['courses'])




@app.route('/stop_attendance',methods=['GET'])
def stop_attendance():
    import cv2
    cv2.destroyAllWindows()
    global link
    return redirect(link)


@app.route('/loadlink')
def loadlink():
    if  session.get('usernameF'):
            professors = mongo.db.professor
            login_user = professors.find_one({"ID" : session.get('usernameF')})
            courses = login_user['courses']
            course1=mongo.db.courses
            select=request.args.get('course')
            obj = course1.find_one({"courses" : select})
            global link
            link=obj['link']
            return render_template('mark_attendance.html',courses=courses,iframe=link,link=link,x="Faculty",user=login_user['ID'],subject=obj['courses'])


@app.route('/loadlink1')
def loadlink1():
    if  session.get('usernameS'):
            students = mongo.db.students
            login_user = students.find_one({"ID" : session.get('usernameS')})
            courses = login_user['courses']
            course1=mongo.db.courses
            select=request.args.get('course')
            obj = course1.find_one({"courses" : select})
            global link
            link=obj['link']
            return render_template('view_attendance.html',courses=courses,iframe1=link,link=link,x="Student",user=login_user['ID'],subject=obj['courses'])
    
@app.route('/edit')
def edit():
    webbrowser.open_new_tab(link)
    session.pop('usernameF', None)
    session.pop('usernameS', None)
    return render_template("studentlogin.ejs",title="Student Login")

@app.route('/logout')
def logout():
   session.pop('usernameF', None)
   session.pop('usernameS', None)
   return redirect(url_for('index',message="true"))


if __name__ == '__main__':
    app.secret_key='secret'
    app.run(host="127.0.0.1",port=5000,debug=True)
