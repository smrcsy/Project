from flask import request
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.orm import scoped_session, sessionmaker, Query
#from flask import Flask,redirect,url_for  
import json
import time
from collections import defaultdict
import datetime
#from datetime import datetime
app = Flask(__name__)
#config information to connect to the database, other database could also be accepted
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:MINCSY417@localhost:3306/projectdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)
# read the table
class Info(db.Model):    
    __table__ = db.Model.metadata.tables['spl_info']

class Detail(db.Model):
    __table__ = db.Model.metadata.tables['spl_dtl']

@app.route('/data',methods=['POST', 'GET'])
#data page
def data():
    #get all the distinct instrument names
    instrumentsName = db.session.query(Info.instrument).distinct().all()   
    #save instrument names into a list
    instruments = []
    for i in instrumentsName:
        instruments.append(i[0])
    #deal with form
    if request.method == 'POST':
        #If the flag in the form is 'data'(search button)
        if request.form['form'] == 'data':
            #get the start and end time user input
            sttime1 = request.form['starttime1']
            ettime1 = request.form['endtime1']
            sttime2 = request.form['starttime2']
            ettime2 = request.form['endtime2']
            #if user forgets to input time, use default time to return all the samples
            if sttime1 == '' or ettime1 == '':
                sttime = '1000-00-00'
                ettime = '3000-00-00'
            else:
                sttime = sttime1 + ' ' + sttime2
                ettime = ettime1 + ' ' + ettime2
            #get the instrument user input
            inst = request.form['instrument']
            # use start time, end time, instrument name to filter samples
            info_instrument = db.session.query(Info).filter_by(instrument=inst).filter(Info.actualstarttime > sttime,Info.actualendtime<ettime).all()
        #if the flag in the form is'all' (show all button)
        elif request.form['form'] == 'all':
            info_instrument = db.session.query(Info).all()
        
        samples = {}
        samples1 = {}
        for i in info_instrument:
            #find a particular sample from the second table to get information of plots
            sample = db.session.query(Detail).filter_by(name = i.name).all()
            samples[i.name] = sample
            nameTar={}       
            for j in sample:                
                data=j.data
                #x-axis
                data1=str(data['RTs'])
                #format is easily used in javascript(eg. 0,1,2,3,4)
                data1 = data1[1:len(data1)-1]
                #y-axis
                data2=str(data['ints'])
                #format is easily used in javascript(eg. 3.45,3.46,3.46...)
                data2 = data2[1:len(data2)-1]
                #double comma helps to split x and y without splitting other data
                data = data1+',,'+data2        
                key=str(j.EIC)
                nameTar[key]=data
            samples1[str(i.name)] = nameTar
        #samples1 records plots x-y coordinates. Each sample could have multiple EIC targets.
        samples1 = json.dumps(samples1)
        
        return render_template("data.html",instruments=instruments,info_instrument = info_instrument,samples = samples, samples1 = samples1)       
                
    return render_template("data.html",instruments=instruments)

#instrument uptime page
@app.route('/', methods=['POST', 'GET'])
def summary():
    # get the list of instruments [a,b,c...]
    info_instruments = db.session.query(Info.instrument).distinct().all()
    instruments = []
    #store all instruments names into the list
    for i in info_instruments:
        instruments.append(i[0])
    #could be deleted
   # sorted(instruments)
    smry_instruments = defaultdict(dict)
    if request.method == 'POST':
        #If the flag in the form is 'summary' (Search button)
        if request.form['form'] == 'summary':
            sttime = request.form['starttime']
            ettime = request.form['endtime']
            #multiple instruments could be chose by user
            inst = request.form.getlist('instrument')
            #if user forgets choose instrument return nothing
            if len(inst) == 0:
                return render_template("summary.html",instruments = instruments,smry_instruments = smry_instruments)
            
            else:
                for j in inst:
                    
                    if sttime != '' and ettime != '':
                        info_instrument = db.session.query(Info).filter_by(instrument=j).filter(Info.actualstarttime > sttime,Info.actualendtime<ettime).all()
                        #transfer start time format
                        st = datetime.datetime.strptime(sttime, "%Y-%m-%d").date()
                        #transfer end time format
                        et = datetime.datetime.strptime(ettime, "%Y-%m-%d").date()
                        #tarnsfer time format to a 13 length integer
                        st = int(time.mktime(st.timetuple()) * 1000)
                        et = int(time.mktime(et.timetuple()) * 1000)
                        total = et-st
                    #if user forgets to choose time gap then return all the samples
                    else:
                        info_instrument = db.session.query(Info).filter_by(instrument=j).all()
                        ct = datetime.datetime.now()
                        ct = int(time.mktime(ct.timetuple()) * 1000 + ct.microsecond / 1000)

                        ft = db.session.query(Info).first().actualstarttime
                        ft = int(time.mktime(ft.timetuple()) * 1000 + ft.microsecond / 1000)
                    #the total time is from the very first sample's start time to the current time
                        total = ct - ft                       
                            
                    count_sample = len(info_instrument)

                    data = []
                    total_length = 0
                    for i in info_instrument:
                        st = i.actualstarttime
                        et = i.actualendtime
                        length = i.length
                        #total running time
                        total_length += length
                        st = int(time.mktime(st.timetuple()) * 1000 + st.microsecond / 1000)
                        et = int(time.mktime(et.timetuple()) * 1000 + et.microsecond / 1000)

                        data.append([st, 1])
                        data.append([et, 0])
                    
                    ratio = round(total_length * 1000 / total * 100, 2)
                    rest_ratio = 100 - ratio
                    smry_instruments[j]['count'] = count_sample
                    smry_instruments[j]['hours'] = round(total/3600000,2)
                    smry_instruments[j]['ratio'] = ratio
                    smry_instruments[j]['rest_ratio'] = rest_ratio
                    smry_instruments[j]['data'] = data
                    # smry_insruments = json.dumps(smry_instruments)
 
            return render_template("summary.html", smry_instruments = smry_instruments, instruments = instruments,inst=inst)
    return render_template("summary.html",instruments = instruments,smry_instruments = smry_instruments)



if __name__ == '__main__':
    app.debug = True
    app.run()
    ft = db.session.query(Info).first().actualstarttime
    print(ft)
    ft = int(time.mktime(ft.timetuple()) * 1000 + ft.microsecond / 1000)
    print(ft)
