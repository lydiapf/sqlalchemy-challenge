import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# I did a majority of this assignment with the aid of a Bootcamp tutor

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement

Station = Base.classes.station

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
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start=YYYY-MM-DD <br/>"
        f"/api/v1.0/start=YYYY-MM-DD/end=YYYY-MM-DD <br/>"
        f"Date range must be between 2010-01-01 and 2017-08-23.")

#Precipitation route

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation info"""
    # Query precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    #Create dictionary from the row info and precipitation info
    results_dic = {date: prcp for date, prcp in results}

    return jsonify(results_dic)

# Station route

@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return a list of station data"""
    # Query all station info
    results = session.query(Station.station).all()

    session.close()

    #Create list for results to return to

    results_list = list(np.ravel(results))
    return jsonify(results_list)

# TOBs Route

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session (link) from Python
    session = Session(engine)

    # Copied directly from work done in Jupyter notebook to get proper date notation
    
    #Last data point
    last_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_query_date = last_query[0]
    last_date = dt.datetime.strptime(last_query_date, '%Y-%m-%d').date()
   
   # Year ago info from previous data point
    year_ago = last_date - dt.timedelta(days=365)
    year_ago_date = year_ago.strftime('%Y-%m-%d')


    # Query all measurement info for specific station
    results = session.query(Measurement.tobs).filter(Measurement.station=='USC00519281').filter(Measurement.date>= year_ago_date).all()

    session.close()
    
    # Create list for results to return to
    results_list = list(np.ravel(results))
    return jsonify(results_list)

 # Start Date route
    
@app.route("/api/v1.0/start=<start>")
def start_date(start):
    # Link session from Python
    session = Session(engine)

   #Query data related to the most active station in the past year
    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs))\
                    .filter(Measurement.date >= start).all()

    first_date = session.query(Measurement.date).order_by(Measurement.date).first()

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    session.close()

    # Create a date list of dataset so dates can be used
    date_list = pd.date_range(start=first_date[0], end=last_date[0])

    # Create a dictionary from the row data and append to list
    start_data = []
    for tmin, tmax, tavg in results:
        start_data_dict = {
            'Start Date': start,
            'End Date': last_date[0]
        }
        start_data_dict['T-MIN'] = tmin
        start_data_dict['T-MAX'] = tmax
        start_data_dict['T-AVG'] = tavg
        start_data.append(start_data_dict)

        #Create an if statement for date input and inform user of proper input
        if start in date_list:
            return jsonify(start_data)
        else:
            return jsonify({
                "error": f"Date: {start} not found. Date must be between {first_date[0]} and {last_date[0]}. Please adjust URL for date in range."
            }), 404

# Start and End Date route
@app.route("/api/v1.0/start=<start>/end=<end>")
def period(start, end):
    # Create session (link) from Python
    session = Session(engine)

    # Query data related to the most active station in the past year
    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end).all()

    first_date = session.query(Measurement.date).order_by(Measurement.date).first()

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    session.close()

    # Create a dictionary from the row data and append to list
    date_list = pd.date_range(start=first_date[0], end=last_date[0])

    period_data = []

    for tmin, tmax, tavg in results:
        period_data_dict = {
            'Start Date': start,
            'End Date': end
        }
        period_data_dict['T-MIN'] = tmin
        period_data_dict['T-MAX'] = tmax
        period_data_dict['T-AVG'] = tavg
        period_data.append(period_data_dict)

        # If statement for date input and inform user of proper date input
        if start and end in date_list:
            if start <= end:
                return jsonify(period_data)
            elif start > end:
                return jsonify({
                    "error": f'{start} is greater than {end}'
                })
        else:
            return jsonify({
                "error": f"Date: {start} to {end} not found. Dates must be between {first_date[0]} and {last_date[0]}. Please adjust URL for dates in range."
            }), 404


if __name__ == '__main__':
    app.run(debug=True)