from tkinter import CENTER
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

@app.route("/")
def home():
    return(
        f"<Center><h2> Welocome to Hawaii Climate Analysis Local API</h2></center>"
        f"<center><h3>Select from available routes below:</h3></center>"
        f"<center>/api/v1.0/precipitation</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start/end</center>"
        )

#/api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
    #return prev years precipitation as a json
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previousYear).all()

    session.close()
    #dict with date as the key and precip as the value
    precipitation ={date: prcp for date, prcp in results}
    #convert to json
    return jsonify(precipitation)

    #/api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    session.close()

    stationList = list(np.ravel(results))
    return jsonify(stationList)

#/api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def temperatures():

    #return prev year temps
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)


    #query to get the temperatures from most active station from past year
    results = session.query(Measurement.tobs).\
    filter(Measurement.station =='USC00519281').\
    filter(Measurement.date >= previousYear).all()  

    session.close()

    tempList = list(np.ravel(results))
    return jsonify(tempList)


#/api/v1.0/start/end, /api/v1.0/start routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):

    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:
        startDate = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*selection).filter(Measurement.date >= startDate).all()

        session.close()

        tempList = list(np.ravel(results))
        return jsonify(tempList)

    else:
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*selection)\
            .filter(Measurement.date >= startDate)\
            .filter(Measurement.date <= endDate).all()

        session.close()

        tempList = list(np.ravel(results))
        return jsonify(tempList)







if __name__=="__main__":
    app.run(debug=True)