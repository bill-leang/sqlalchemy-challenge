import sqlalchemy
from flask import Flask, jsonify
from sqlalchemy import create_engine, func, desc, and_
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(autoload_with=engine)

Measurement = Base.classes.measurement
Station = Base.classes.station


app = Flask(__name__)

@app.route("/")
def welcome():
    """List all the available routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    latest_m = session.query(Measurement).order_by(desc(Measurement.date)).first()
    latest_dt = datetime.strptime(latest_m.date, '%Y-%m-%d')
    after_date = latest_dt - timedelta(days=366)

    last12m_m = session.query(Measurement.date, Measurement.prcp).filter(and_( (Measurement.date >= after_date), (Measurement.date <= latest_dt))).\
        order_by(desc(Measurement.date)).all()
    session.close()
    prec_data = [{meas.date: meas.prcp} for meas in last12m_m]
    return jsonify(prec_data)

@app.route("/api/v1.0/stations")
def stations():
    num_station = session.query(func.count(Station.station)).all()
    return ("WIP <br/>")

@app.route("/api/v1.0/tobs")
def tobs():
    return ("WIP <br/>")

@app.route("/api/v1.0/<start>")
def startdate(start):
    return (f"WIP start <br/>")

@app.route("/api/v1.0/<start>/<end>")
def startenddates(start, end):
    return ("WIP start end <br/>")

if __name__== '__main__':
    app.run(debug=True)