#dependencies
#___________________________________________________________________

from matplotlib import style
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
from pandas.plotting import table
import math

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#database setup
#___________________________________________________________________

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


# Flask Setup
#___________________________________________________________________

app = Flask(__name__)

#flask routes
@app.route("/")
def home():
    return (
        f"Welcome to Home page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

#precipitation
#___________________________________________________________________

@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date = session.query(Measurement).order_by(Measurement.date.desc()).first()
    datetime_recent_date = datetime.strptime(recent_date.date, '%Y-%m-%d').date()
    last_year = datetime_recent_date - dt.timedelta(days=365)
    one_year = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= last_year)
    precipitation = {}
    for date, prcp in one_year:
        precipitation[date] = prcp
    
    return jsonify(precipitation)

#stations
#___________________________________________________________________

@app.route("/api/v1.0/stations")
def stations():
    all_stations = session.query(Station.station).all()
    list_stations=list(np.ravel(all_stations))
    
    return jsonify(list_stations)

#tobs
#___________________________________________________________________

@app.route("/api/v1.0/tobs")
def tobs():
    recent_date = session.query(Measurement).order_by(Measurement.date.desc()).first()
    datetime_recent_date = datetime.strptime(recent_date.date, '%Y-%m-%d').date()
    last_year = datetime_recent_date - dt.timedelta(days=365)
      
    most_active_station = session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    
    most_active_temp = session.query(Measurement.tobs).filter(Measurement.station == most_active_station[0]).\
    filter(Measurement.date >= last_year).all()
    
    list_most_active_temps = list(np.ravel(most_active_temp))
    
    return jsonify(list_most_active_temps)

#start end
#___________________________________________________________________

@app.route("/api/v1.0/temp/<start>")
def from_start(start):
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    start = dt.datetime.strptime(start, "%m%d%Y")
    stat_start = session.query(*sel).filter(Measurement.date >= start).all()
    temp_start = list(np.ravel(stat_start))
    
    return jsonify(temp_start)
 

@app.route("/api/v1.0/temp/<start>/<end>")
def from_start_to_end(start,end):
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    stat_start_end = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp_start_end = list(np.ravel(stat_start_end))
    
    return jsonify(temp_start_end)




if __name__ == "__main__":
    app.run(debug=True)