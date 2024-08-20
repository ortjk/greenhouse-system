import os
import time
from datetime import datetime
from subprocess import Popen, PIPE, TimeoutExpired
from flask import Flask, request, redirect

from server.database import get_arduino_conf, set_arduino_conf, get_graph_data, average_entries, strptime_map

def create_app(test_config=None):
    # start communication with arduino
    arduino_io = Popen(["python3", "server/arduino/arduino_connection.py"])


    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
        
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/set-config", methods=["POST"])
    def set_config():
        form_map = {
            "off": 0,
            "on": 1,
            '': 0,
            None: 0,
        }
        
        # get information from form
        manual_enabled = form_map[request.form.get("enable-switch-value")]
        manual_open = form_map[request.form.get("open-switch-value")]

        open_temp = request.form.get("open-temperature-value")
        close_temp = request.form.get("close-temperature-value")

        # attempt to catch bad values
        open_temp = form_map.get(open_temp, open_temp)
        open_temp = float(open_temp)
        close_temp = form_map.get(close_temp, close_temp)
        close_temp = float(close_temp)

        # save information to database
        set_arduino_conf(manual_enabled, manual_open, open_temp, close_temp)
        return redirect("/", code=302)
    
    @app.route("/get-config", methods=["GET"])
    def get_config():
        conf = get_arduino_conf()
        return {
            "enable_manual": bool(conf["manual_open"] & 2),
            "open_manual": bool(conf["manual_open"] & 1),
            "open_temperature": conf["open_temperature"],
            "close_temperature": conf["close_temperature"]
        }

    @app.route("/graph", methods=["GET"])
    def get_graph():
        try:
            lookback = request.args["lookback"]
        except IndexError:
            return {'error': "Missing 'lookback' parameter"}, 400
        try:
            period = request.args["period"]
        except IndexError:
            return {'error': "Missing 'period' parameter"}, 400
        
        try:
            lookback = int(lookback)
        except TypeError:
            return {'error': "Parameter 'lookback' is not numeric"}, 400
        try:
            period = int(period)
        except TypeError:
            return {'error': "Parameter 'period' is not numeric"}, 400
        
        t = time.time()
        data = get_graph_data(t - lookback)

        if period <= 61:
            data = average_entries(data, 0)
        elif period <= 3601:
            data = average_entries(data, 1)
        else:
            data = average_entries(data, 2)

        return {'data': data}
    
    return app
