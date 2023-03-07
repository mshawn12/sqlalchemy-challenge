# Imports
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine)

# Save reference to the two tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Creating app
app = Flask(__name__)

# Defining routes
# Defining what to do when users hit index
@app.route("/")
def homepage():
    return (
        f"Hawaii Climate App <br/><br/>"
        f"Available routes:</br>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"<li>/api/v1.0/<start></li>"
        f"<li>/api/v1.0/<start>/<end></li>"
        f"<p>'start' and 'end' date shou;d be in the format MMDDYYYY.</p>"
    )

# Defining what to do when users hit /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set.
    year_from_last_date = dt.date(2017,8,23) - dt.timedelta(days=365)

    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_from_last_date).all()
    
    # Close Session
    session.close()
    
    # Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    precip = {date: prcp for date, prcp in precipitation}

    # Return the JSON representation of your dictionary
    return jsonify(precip)

# Defining what to do when users hit /api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    # Design a query for all the stations in the dataset
    query = session.query(Station.station).all()

    # Close Session
    session.close()

    # Convert list of tuples into normal list
    stations = list(np.ravel(query))
    
    # Return a JSON list of stations from the dataset
    return jsonify(stations=stations)

# Defining what to do when users hit /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tobs():
    # Query the last 12 months of temperature observation data for the most active station
    last_12_months_tobs = dt.date(2017,8,23) - dt.timedelta(days=365)

    query = session.query(Measurement.tobs).\
        filter(Measurement.station=='USC00519281').\
        filter(Measurement.date >= last_12_months_tobs).all()
    
    # Close Session
    session.close()
    
    # Convert list of tuples into normal list
    temps = list(np.ravel(query))

    # Return a JSON list of temperature observations for the previous year.
    return jsonify(temps=temps)


# Defining what to do when users hit /api/v1.0/<start> AND /api/v1.0/<start>/<end>
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None,end=None):
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start,"%m%d%Y")
        query = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        # Close Session
        session.close()

        # Convert list of tuples into normal list
        temps = list(np.ravel(query))

        # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start
        return jsonify(temps)
    
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
    start = dt.datetime.strptime(start,"%m%d%Y")
    end = dt.datetime.strptime(end,"%m%d%Y")

    query = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

     # Close Session
    session.close()

    # Convert list of tuples into normal list
    temps = list(np.ravel(query))

    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range.
    return jsonify(temps=temps)



# Defining main behavior
if __name__ == "__main__":
    app.run(debug=True)
