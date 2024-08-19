import os
import time
from subprocess import Popen, PIPE, TimeoutExpired
from flask import Flask, request, redirect

from server.database import get_arduino_conf, set_arduino_conf, get_graph_data

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
        return get_graph_data(time.time() - request.form.get("lookback"))
    
    return app
