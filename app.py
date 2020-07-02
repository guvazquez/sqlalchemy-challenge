import sqlalchemy
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt


#Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Collect date variable to be used later
session = Session(engine)
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
last_date_str = str(last_date[0]).split("-")
last_date_dt = dt.date(int(last_date_str[0]),int(last_date_str[1]),int(last_date_str[2]))
session.close()

#Flask

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date <= last_date_dt).\
    filter(Measurement.date >= (last_date_dt-dt.timedelta(days=365))).all()
    session.close()
    precipitate = []
    for date, prcp in results:
        prec_dict = {}
        prec_dict["name"] = date
        prec_dict["prcp"] = prcp
        precipitate.append(prec_dict)    
    return jsonify(precipitate)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation)
    session.close()
    stations = []
    for station, name, latitude, longitude, altitude in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["altitude"] = altitude
        stations.append(station_dict)
        
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Station.station, Station.name, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Station.station == Measurement.station).\
        filter(Measurement.date <= last_date_dt).\
        filter(Measurement.date >= (last_date_dt-dt.timedelta(days=365))).\
        group_by(Station.id).\
        order_by(func.count(Station.station).desc()).limit(1).all()
    session.close()
    tobs = []
    for station, name, min, max, avg in results:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["name"] = name
        tobs_dict["min"] = min
        tobs_dict["max"] = max
        tobs_dict["avg"] = avg
        tobs.append(tobs_dict)    
    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
def tobs_query(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    tobs_q1 = []
    for min, max, avg in results:
        tobsq1_dict = {}
        tobsq1_dict["min"] = min
        tobsq1_dict["max"] = max
        tobsq1_dict["avg"] = avg
        tobs_q1.append(tobsq1_dict)    
    
        if start <= last_date[0]:
           return jsonify(tobs_q1) 

    return jsonify({"error": f"There is no data for {start}. Data is avalailable up to {last_date[0]}"})


@app.route("/api/v1.0/<start>/<end>")
def tobs_query2(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    tobs_q2 = []
    for min, max, avg in results:
        tobsq2_dict = {}
        tobsq2_dict["min"] = min
        tobsq2_dict["max"] = max
        tobsq2_dict["avg"] = avg
        tobs_q2.append(tobsq2_dict)    
    
        if start <= last_date[0]:
           return jsonify(tobs_q2) 

    return jsonify({"error": f"There is no data for {start}. Data is avalailable up to {last_date[0]}"})


if __name__ == "__main__":
    app.run(debug=True)