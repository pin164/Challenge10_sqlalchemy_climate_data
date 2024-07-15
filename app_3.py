# Part 2: Design Your Climate App
# 
# 
#  Import the dependencies.
import sqlalchemy
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from datetime import datetime, timedelta
import numpy as np
#################################################
# Database Setup
#################################################
# Create engine using the "hawaii "databel file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using "automap_base()"
Base = automap_base()
# reflect an existing database into a new model

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# confirm connection
print("database connected")
# Create our session (link) from Python to the DB
session = Session(engine)
#NOTE:
#Best practice is to open and close session in each route.
#Nonetheless I comply with assignment requirement 
# I commented out each route  open and close
#################################################
# Flask Setup
#################################################
# Flask Setup
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define available routes
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
#########  precipitation  ###########################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last year of precipitation data as JSON."""
    # Create a new session link from Python to the database
    # session = Session(engine)
    
    # Calculate the date 1 year ago from  the last date in the database 
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - timedelta(days=365)
    
    # Perform a query to retrieve the dates needed
    results = session.query(Measurement.date, Measurement.prcp).\
              filter(Measurement.date >= one_year_ago).all()
    
    # Convert the precipitation results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in results}
    
    # Close the session
    #session.close()

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)

#########  stations  n###########################################################
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations as JSON."""
    # Create a new session link from Python to the database
    # session = Session(engine)

    # Perform a query to retrieve the stations
    results = session.query(Station.station).all()
   
    # Close the session
    # session.close()
    
    # Convert the station results to a list
    stations_list = list(np.ravel(results))

    # Return the JSON list of stations
    return jsonify(stations_list)
  

#########  tobs  n###########################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return the last year of temperature observations (tobs) for the most-active station."""
    # Create a session link from Python to the database
    ## session = Session(engine)

    # Query to find the station with the most observations
    most_active_station_id = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]

    # Calculate the date 1 year ago from the last data point for the most active station
    last_date = session.query(func.max(Measurement.date))\
        .filter(Measurement.station == most_active_station_id)\
        .scalar()
    one_year_ago = datetime.strptime(last_date, '%Y-%m-%d') - timedelta(days=365)

    # Perform a query to retrieve the temperature observations for the most active station
    results = session.query(Measurement.tobs)\
        .filter(Measurement.station == most_active_station_id)\
        .filter(Measurement.date >= one_year_ago)\
        .all()

    # Convert the results to a list of temperature observations
    tobs_list = [temp.tobs for temp in results]

    # Close the session
    ##session.close()

    # Return the JSON list of temperature observations for the most active station
    return jsonify(tobs_list)

######### start date YYY-MM-DD  n###########################################################
# Start route
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    # Establish a session (best practise )
   # session = Session(engine)
    
    # Convert the start date to a proper datetime object
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        session.close()
        return jsonify({"error": "Date format should be YYYY-MM-DD"}), 400
        
    # Perform the query to get statistics from the start date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start_date).all()
    
    # Close the session to avoid leaks
    #session.close()
    
    # Unpack the result and create a dictionary to store it
    min_temp, avg_temp, max_temp = results[0]
    stats = {
        "Start Date": start,
        "TMIN": min_temp,
        "TAVG": avg_temp,
        "TMAX": max_temp
    }
    
    # Return the JSON representation of the dictionary
    return jsonify(stats)

#########  start & end date YYYY-MM-DD/YYY-MM-DD  n###########################################################
# Start/end route
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    # Establish a session
   # session = Session(engine)
    
    # Convert start and end dates to datetime objects
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        session.close()
        return jsonify({"error": "Date format should be YYYY-MM-DD"}), 400
    
    # Validate that the end date is not before the start date
    if end_date < start_date:
        session.close()
        return jsonify({"error": "End date must not be before start date"}), 400
        
    # Perform the query to get statistics between start and end dates
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    # Close the session to avoid leaks
    #session.close()
    
    # Unpack the result and create a dictionary to store it
    min_temp, avg_temp, max_temp = results[0]
    stats = {
        "Start Date": start,
        "End Date": end,
        "TMIN": min_temp,
        "TAVG": avg_temp,
        "TMAX": max_temp
    }
    
    # Return the JSON representation of the dictionary
    return jsonify(stats)



# Close the session to avoid leaks
    session.close()
# Run the application
if __name__ == '__main__':
    app.run(debug=True)