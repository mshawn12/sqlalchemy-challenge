import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)


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

@app.route("/api/v1.0/precipitation")
def precipitation():
    year_from_last_date = dt.date(2017,8,23) - dt.timedelta(days=365)

    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_from_last_date).all()
    
    session.close()
    precip = {date: prcp for date, prcp in precipitation}

    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    query = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(query))
    
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def tobs():
    last_12_months_tobs = dt.date(2017,8,23) - dt.timedelta(days=365)

    query = session.query(Measurement.tobs).\
        filter(Measurement.station=='USC00519281').\
        filter(Measurement.date >= last_12_months_tobs).all()
    
    session.close()
    
    temps = list(np.ravel(query))

    return jsonify(temps=temps)



@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None,end=None):
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start,"%m%d%Y")
        query = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        session.close()

        temps = list(np.ravel(query))

        return jsonify(temps)
    
    start = dt.datetime.strptime(start,"%m%d%Y")
    end = dt.datetime.strptime(end,"%m%d%Y")

    query = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    
    session.close()

    temps = list(np.ravel(query))

    return jsonify(temps=temps)


if __name__ == "__main__":
    app.run(debug=True)
