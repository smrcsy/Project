from flask import request
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker, Query
from flask import Flask,redirect,url_for  
import json
import time
from datetime import datetime
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:MINCSY417@localhost:3306/projectdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)
class Test(db.Model):
    
    __table__ = db.Model.metadata.tables['test']

class Test1(db.Model):
    __table__ = db.Model.metadata.tables['data']

@app.route('/',methods=['POST', 'GET'])
def home():
    users = Test.query.all()
    data = Test1.query.all()
    if request.method == 'POST':
        return redirect(url_for('/graph'))
        
    return render_template("homePage.html",data = data)




@app.route('/graph', methods=['POST', 'GET'])
def show():
    instruments = db.session.query(Test.instrument).distinct().all()
    
    if request.method == 'POST':
        num_instrument = request.form['instrument']
        a =db.session.query(Test).filter_by(instrument=num_instrument).all()

        aa = []
        for i in a:
            st = i.actualstarttime
            et = i.actualendtime        
            starttime = datetime.strptime(st, "%Y-%m-%d %H:%M:%S.%f")
            endtime = datetime.strptime(et, "%Y-%m-%d %H:%M:%S.%f")
            st = int(time.mktime(starttime.timetuple()) * 1000 + starttime.microsecond/1000)
            et = int(time.mktime(endtime.timetuple()) * 1000 + endtime.microsecond/1000)
                    
            aa.append([st,1])
            aa.append([et,0])

        return render_template('graph.html', instruments = instruments,data=aa)
    
    
    return render_template('graph.html', instruments = instruments)


if __name__ == '__main__':
    app.debug = True
    app.run()
    #here1 = Test1.query.filter_by(name = '50uM.mzML',EIC=100).first()
    #instruments = db.session.query(Test.instrument).distinct().all()
    a =db.session.query(Test).filter_by(instrument=2).all()
    aa = []
    for i in a:
        st = i.actualstarttime
        et = i.actualendtime        
        starttime = datetime.strptime(st, "%Y-%m-%d %H:%M:%S.%f")
        endtime = datetime.strptime(et, "%Y-%m-%d %H:%M:%S.%f")
        st = int(time.mktime(starttime.timetuple()) * 1000 + starttime.microsecond/1000)
        et = int(time.mktime(endtime.timetuple()) * 1000 + endtime.microsecond/1000)
        
        aa.append([st,1])
        aa.append([et,0])
    print(aa)
    #print(instruments)
    dt = '2018-04-24 16:13:56.822434'
    #timeArray = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f")
    #print(timeArray)
    #a = int(time.mktime(timeArray.timetuple()) * 1000 + timeArray.microsecond/1000)
    #print(a)


