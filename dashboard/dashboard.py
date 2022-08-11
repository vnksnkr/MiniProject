from pkg_resources import get_build_platform
from flask import Flask, request, render_template
import telegram_send
import json
import pandas as pd
import json
import plotly
import plotly.express as px
import sqlite3 as sql
import numpy as np


app = Flask(__name__)



acc_x = [0]*128
acc_y = [0]*128
acc_z = [0]*128

lastfallday = "0"
lastfallmon = "0"
lastfallyear = "0"
lastfallhr = "0"
lastfallmin = "0"
hr = "0"
lasttremordate = "0"

def add_data(date, acc_x, acc_y, acc_z):  
  try:
    # Connecting to database
    con = sql.connect('tremors.db')
    # Getting cursor
    c =  con.cursor() 
    # Adding data
    c.execute("INSERT INTO Tremors (date, acc_x, acc_y, acc_z) VALUES (%s, %s, %s, %s)" %(date, acc_x, acc_y, acc_z))
    # Applying changes
    con.commit() 
  except:
    print("An error has occured")



@app.route('/post', methods = ["POST"])
def post():

    global lastfallday
    global lastfallmon
    global lastfallyear
    global lastfallhr
    global lastfallmin
    global hr
    global lasttremordate
    global acc_x
    global acc_y
    global acc_z

    y = json.loads(request.data)
    
    hr = float(y["HR"])
    fallday = y["fallDay"]
    fallmon = y["fallMon"]
    fallyear = y["fallYear"]
    fallhr = y["fallHr"]
    fallmin = y["fallMin"]
    tremordate = f'{y["tremorDay"]}-{y["tremorMon"]}-{y["tremorYear"]} {y["tremorHr"]}:{y["tremorMin"]}'
    
    if int(fallmin) < 10:
        fallmin = '0' + str(fallmin)

    if (hr < 40 or hr > 120) and (hr != 0):
        hralert = f"Alert! Heart rate is {hr}"
        telegram_send.send(messages=[hralert])
    
    if fallday != lastfallday or lastfallmon != fallmon or lastfallyear != fallyear or lastfallhr != fallhr or lastfallmin != fallmin:
        fallalert = f"Alert! Patient fell at {fallhr}:{fallmin}"
        lastfallday  = fallday
        lastfallmon = fallmon
        lastfallyear = fallyear
        lastfallhr = fallhr
        lastfallmin = fallmin
        telegram_send.send(messages=[fallalert])


    if lasttremordate != tremordate:
        lasttremordate = tremordate
        acc_x = y["acc_x"]
        acc_y = y["acc_y"]
        acc_z = y["acc_z"]
        #for i in range(0,128):
            #add_data(lasttremordate, y["acc_x"][i], y["acc_y"][i], y["acc_z"][i])
                        


    return ''

@app.route('/', methods=['GET', 'POST'])
def index():

    global lastfallday
    global lastfallmon
    global lastfallyear
    global lastfallhr
    global lastfallmin
    global hr

    #print(hr)
    return render_template('wearabledashboard.html',heartrate=hr,Day=lastfallday,Month=lastfallmon,Year=lastfallyear,Hour=lastfallhr,Min=lastfallmin)   



@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return gm(request.args.get('data'))
   
@app.route('/tremorplot')
def tremorplot():
    return render_template('tremors.html', date=lasttremordate, graphJSON=gm())


@app.route('/history')
def history():
    return render_template('history.html')

def gm():
    global acc_x
    global acc_y
    global acc_z
    #acc_x_val = 
    namelist = ['TremorX','TremorY','TremorZ']
    t   =   np.linspace(0,10,128)
    df  =   pd.DataFrame([acc_x,acc_y,acc_z],index=namelist,columns=t)
    df.T
    fig =   px.line(df.T)
    fig.show()
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    print(fig.data[1])
    #fig.data[0]['staticPlot']=True
    
    return graphJSON    


app.run(debug=True, host='0.0.0.0', port= 5000)


