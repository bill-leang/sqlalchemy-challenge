import sqlalchemy
from flask import Flask, jsonify
from sqlalchemy import create_engine, func, desc, and_
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# generate engine, save references,
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(autoload_with=engine)

Measurement = Base.classes.measurement
Station = Base.classes.station


app = Flask(__name__)

# landing page
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

# return last one year of precipitation with date as key, prcp as value
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

# returns the list of all stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_r = session.query(Station.station).all()
    session.close()

    station_list = []
    for station in station_r:
        station_list.append(station[0])

    return jsonify(station_list)

# returns tobs of the most active station
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # get the most active station (top_station)
    station_count = session.query(Station.station, func.count(Measurement.id).label('measurement_count'))\
        .join(Measurement, Station.station == Measurement.station).group_by(Station.station)\
        .order_by(func.count(Measurement.id).desc()).all()
    top_station_id = station_count[0][0]
    # get the last 1 year date range for this station
    latest_m = session.query(Measurement).filter(Measurement.station== top_station_id).order_by(desc(Measurement.date)).first()
    latest_dt = datetime.strptime(latest_m.date, '%Y-%m-%d')
    after_date = latest_dt - timedelta(days=366)
    # get the tobs of the last one year
    last12m_temp = session.query(Measurement.date, Measurement.tobs).filter(and_( (Measurement.date >= after_date),\
                (Measurement.date <= latest_dt)), (Measurement.station == top_station_id)).order_by(Measurement.date.desc()).all()
    session.close()

    temp_data = [{ meas.date: meas.tobs} for meas in last12m_temp]
    return jsonify(temp_data)

# return min, max, avg temps from the start date
@app.route("/api/v1.0/<start>")
def startdate(start):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs).label('min_temp'), func.max(Measurement.tobs).label('max_temp'),\
                           func.avg(Measurement.tobs).label('avg_temp')).filter(Measurement.date >= start).all()
    session.close()
    try:
        jdata = {'min_temp': result[0][0], 'max_temp': result[0][1], 'avg_temp':round(result[0][2],2)}
    # throws error message if invalid date is given
    except:
        return f"Invalid data found"
    return jsonify(jdata)

# return min, max, avg temps from the start date to end date
@app.route("/api/v1.0/<start>/<end>")
def startenddates(start, end):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs).label('min_temp'), func.max(Measurement.tobs).label('max_temp'),\
                           func.avg(Measurement.tobs).label('avg_temp')).filter(and_((Measurement.date >= start),\
                                                                                      (Measurement.date <= end))).all()
    session.close()
    try:
        jdata = {'min_temp': result[0][0], 'max_temp': result[0][1], 'avg_temp':round(result[0][2],2)}
    # throws error message if invalid date is given
    except:
        return f"Invalid data found"
    return jsonify(jdata)

if __name__== '__main__':
    app.run(debug=True)