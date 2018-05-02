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

class Data(db.Model):
    __table__ = db.Model.metadata.tables['data']

@app.route('/',methods=['POST', 'GET'])
def home():
    instrumentsName = db.session.query(Test.instrument).distinct().all()
    names = db.session.query(Test.name).all()
    test_table = db.session.query(Test).all()
    testrowCount = db.session.query(Test).count()
    data_table = db.session.query(Data).all()
    datarowCount = db.session.query(Data).count()

    
    instruments = []
    for i in instrumentsName:
        instruments.append(i[0])

    
    mzmlNames = []
    for i in names:
        mzmlNames.append(i[0])

    instrument_name={}    
    for index in range(testrowCount):
        key=test_table[index].instrument
        value=test_table[index].name
        if key not in instrument_name:
            instrument_name[key]=[value]
        else:
            instrument_name[key].append(value)

    name_target={}
    nameTarget_data={}    
    for index in range(datarowCount):
        data=data_table[index].data
        data1=str(data['RTs'])
        
        data2=str(data['ints'])
        data = data1+',,'+data2
        
        key=str(data_table[index].name)+str(data_table[index].EIC)
        nameTarget_data[key]=data
        
        if data_table[index].name not in name_target:  
            name_target[data_table[index].name]=[str(data_table[index].EIC)]
        else:
            name_target[data_table[index].name].append(str(data_table[index].EIC))
            
    instrument_name=json.dumps(instrument_name)
    name_target=json.dumps(name_target)     
    nameTarget_data=json.dumps(nameTarget_data)
    return render_template("homePage.html",instruments=instruments,mzmlNames=mzmlNames,data_table=data_table,instrument_name=instrument_name,name_target=name_target,nameTarget_data=nameTarget_data)




@app.route('/graph', methods=['POST', 'GET'])
def show():
    info_instruments = db.session.query(Test.instrument).distinct().all()
    instruments = []
    for i in info_instruments:
        instruments.append(i[0])
    if request.method == 'POST':
        num_instrument = request.form['instrument']
        info_instrument =db.session.query(Test).filter_by(instrument=num_instrument).all()

        data = []
        total_lentgh = 0
        for i in info_instrument:
            st = i.actualstarttime
            et = i.actualendtime
            length = i.length
            total_length += length
            starttime = datetime.strptime(st, "%Y-%m-%d %H:%M:%S.%f")
            endtime = datetime.strptime(et, "%Y-%m-%d %H:%M:%S.%f")
            st = int(time.mktime(starttime.timetuple()) * 1000 + starttime.microsecond/1000)
            et = int(time.mktime(endtime.timetuple()) * 1000 + endtime.microsecond/1000)
                    
            data.append([st,1])
            data.append([et,0])
        ct = datetime.now()
        ct = int(time.mktime(currenttime.timetuple()) * 1000 + currenttime.microsecond/1000)

        ft =db.session.query(Test).first().actualstarttime
        first_time = datetime.strptime(ft, "%Y-%m-%d %H:%M:%S.%f")
        ft = int(time.mktime(first_time.timetuple()) * 1000 + first_time.microsecond/1000)

        total = ct - ft
        return render_template('graph.html', instruments = instruments,data = data)   
    
    return render_template('graph.html', instruments = instruments)


if __name__ == '__main__':
    app.debug = True
    #app.run()
    ct = datetime.now()
    #currenttime = datetime.strptime(ct, "%Y-%m-%d %H:%M:%S.%f")
    ct = int(time.mktime(ct.timetuple()) * 1000 + ct.microsecond/1000)
    
    
    print(ct-ft)
