# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route(f"/api/v1.0/precipitation")
def precipitation():
	session = Session(engine)
	latest_date = datetime(2017,8,23)
	year_ago = latest_date - timedelta(days=365)
    
	# grab precipitation data from SQL lite
	last12 = session.query(measurement.date,measurement.prcp).\
	filter((measurement.date<=latest_date) &(measurement.date>year_ago))
	session.close()
    
	#put precipitation data in a dictionary
	all_prcp = []
	for date, prcp in last12:
		prcp_dict = {}
		prcp_dict["date"] = date
		prcp_dict["prcp"] = prcp
		all_prcp.append(prcp_dict)
	return jsonify(all_prcp)


@app.route(f"/api/v1.0/stations")
def stations():
	stations_list=[]
	session = Session(engine)
	station_names = session.query(measurement.station).distinct().all()
	session.close()
	
	for row in station_names:
		stations_list.append(row[0])
	return jsonify(stations_list)

@app.route(f"/api/v1.0/tobs")
def temps():
	activeid = "USC00519281"
	latest_date = datetime(2017,8,23)
	year_ago = latest_date - timedelta(days=365)
	session = Session(engine)
	temp = session.query(measurement.date,measurement.tobs).\
	filter((measurement.date<=latest_date) & (measurement.date>year_ago)).\
	filter(measurement.station==activeid).all()
	temp_list = [{"date": row.date, "tobs": row.tobs} for row in temp]
	session.close()
	return jsonify(temp_list)

@app.route(f"/api/v1.0/<start>")
def temps2(start):
	session = Session(engine)
	temp2 = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
	filter(measurement.date>=start)
	session.close()
	min_temp, max_temp, avg_temp = temp2[0]
	result = {
		"min_temp": min_temp,
		"max_temp": max_temp,
		"avg_temp": avg_temp
    }
	return jsonify(result)

@app.route(f"/api/v1.0/<start>/<end>")
def temps3(start, end):
	session = Session(engine)
	temp3 = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
	filter((measurement.date>=start)& (measurement.date<=end))  
	session.close()
	min_temp, max_temp, avg_temp = temp3[0]
	result = {
		"min_temp": min_temp,
		"max_temp": max_temp,
		"avg_temp": avg_temp
    }
	return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
