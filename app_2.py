#Part 2: Design Your Climate App
# 
# 
#  Import the dependencies.

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime as dt
import numpy as np
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})  
# added parameter to avoid threading errors with Flask

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)
print(Station)
@app.route("/")
def homepage():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of precipitation dictionary."""
    # Create our session from Python to the DB
    session = Session(engine)
    
    # Query for the last 12 months of precipitation data
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    recent_date = dt.strptime(most_recent_date, '%Y-%m-%d').date()
    one_year_ago = recent_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
              filter(Measurement.date >= one_year_ago).\
              order_by(Measurement.date).all()
    print(results)
    session.close()

    # Convert to dictionary using date as the key and prcp as the value
    precipitation_data = dict(results)

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Create our session from Python to the DB
    session = Session(engine)
    
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into a list
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data."""
    # Create our session from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and temperature observations for the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
                          group_by(Measurement.station).\
                          order_by(func.count(Measurement.station).desc()).\
                          first()[0]

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    recent_date = dt.strptime(most_recent_date, '%Y-%m-%d').date()
    one_year_ago = recent_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == most_active_station).\
              filter(Measurement.date >= one_year_ago).\
              order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into a list of dictionaries
    temperature_list = []
    for date, tobs in results:
        temp_dict = {"date": date, "temperature": tobs}
        temperature_list.append(temp_dict)

    return jsonify(temperature_list)

# ...

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum
     temperature for a given start date, or a 404 if not."""
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).first()

    session.close()

    # Check if we have data
    if results is None or any(v is None for v in results):
        return jsonify({"error": "No data found for given start date."}), 404
    
    # Convert the results to a dictionary
    temp_data = {
        "Start Date": start,
        "TMIN": results[0],
        "TAVG": results[1],
        "TMAX": results[2]
    }

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum
     temperature for a given start-end range."""
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).\
              filter(Measurement.date <= end).first()
    
    session.close()

    # Check if we have data
    if results is None or any(v is None for v in results):
        return jsonify({"error": "No data found for given date range."}), 404
    
    # Convert the results to a dictionary
    temp_data = {
        "Start Date": start,
        "End Date": end,
        "TMIN": results[0],
        "TAVG": results[1],
        "TMAX": results[2]
    }

    return jsonify(temp_data)

# ...

# Run the application
if __name__ == '__main__':
    app.run(debug=True)