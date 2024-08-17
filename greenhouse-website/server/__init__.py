import os
from subprocess import Popen, PIPE, TimeoutExpired
from flask import Flask, request, render_template
from .encoding_f import encode_input, decode_output

def create_app(test_config=None):
    
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

    @app.route("/communicate", method=["GET", "POST"])
    def communicate():
        # start communication with arduino
        arduino_io = Popen(["python3", "server/arduino_connection.py"], stdin=PIPE, stdout=PIPE)
        instructions = None # empty instructions set
        output = None

        if request.method == "POST":
            # get information from form
            manual_enabled = request.form.get("enableManualCheck")
            force_open = request.form.get("openWindowCheck")
            manual_open = 0 # 0b00
            if manual_enabled and force_open:
                manual_open = 3 # 0b11
            elif manual_enabled:
                manual_open = 2 # 0b10

            open_temperature = request.form.get("openTemperatureValue")
            close_temperature = request.form.get("closeTemperatureValue")
            
            instructions = {
                "manual_open": manual_open,
                "open_temperature": open_temperature,
                "close_temperature": close_temperature
            }

        # communicate with the arduino
        try:
            output, _ = arduino_io.communicate(encode_input(instructions), 0.5)
        except TimeoutExpired:
            print("Communication failed")

        return decode_output(output)
    
    return app
