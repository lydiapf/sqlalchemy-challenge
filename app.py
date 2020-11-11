import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


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
        f"/api/v1.0/tobs"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    results_dic = {date: prcp for date, prcp in results}

    return jsonify(results_dic)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    results = session.query(Station.station).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    # all_station = []
    # for name in results:
    #     station_dict = {}
    #     station_dict["name"] = name
    #     all_station.append(station_dict)

    results_list = list(np.ravel(results))
    return jsonify(results_list)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    last_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_query_date = last_query[0]
    last_date = dt.datetime.strptime(last_query_date, '%Y-%m-%d').date()
    year_ago = last_date - dt.timedelta(days=365)
    year_ago_date = year_ago.strftime('%Y-%m-%d')

    results = session.query(Measurement.tobs).filter(Measurement.station=='USC00519281').filter(Measurement.date>= year_ago_date).all()

    session.close()
    
    results_list = list(np.ravel(results))
    return jsonify(results_list)
    


if __name__ == '__main__':
    app.run(debug=True)
