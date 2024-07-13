#Part 2: Design Your Climate App
# 
# 
#  Import the dependencies.


from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime as dt
from datetime import timedelta 
import numpy as np
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Define available routes
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;start&gt;<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    with Session(engine) as session:
        """Return the precipitation data for the last year"""
    # Calculate the date one year ago from the last data point in the database
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()e = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.date(most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precip_data = {date: prcp for date, prcp in results}
    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations (tobs) for the previous year of the most-active station."""
    # Choose the station with the highest number of temperature observations.
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year ago from the last data point in the database
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the last year of temperature observation data for this station
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps = temps)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start."""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    temperatures = list(np.ravel(results))
    return jsonify(temperatures)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range."""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temperatures = list(np.ravel(results))
    return jsonify(temperatures)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)