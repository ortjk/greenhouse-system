import sqlite3 as sql
import time
from datetime import datetime
import numpy as np

queries = {
    # config table queries
    "create_config_table": "CREATE TABLE IF NOT EXISTS ArduinoConfiguration (manual_enable INTEGER NOT NULL, manual_open INTEGER NOT NULL, open_temperature REAL NOT NULL, close_temperature REAL NOT NULL)",
    "add_default_config": "INSERT INTO ArduinoConfiguration VALUES (0, 0, 30.0, 20.0)",
    "get_config": "SELECT * FROM ArduinoConfiguration",
    "check_config_count": "SELECT count(*) FROM ArduinoConfiguration",
    "add_config": "INSERT INTO ArduinoConfiguration VALUES (?, ?, ?, ?)",
    "remove_existing_config": "DELETE FROM ArduinoConfiguration WHERE rowid > 1",

    # graph table queries
    "create_graph_table": "CREATE TABLE IF NOT EXISTS Graph (timestamp INTEGER NOT NULL, temperature REAL NOT NULL, humidity REAL NOT NULL, error INTEGER NOT NULL)",
    "get_graph_data": "SELECT * FROM Graph WHERE timestamp > ?",
    "remove_old_graph_entries": "DELETE FROM Graph WHERE timestamp < ?",
    "add_graph_entry": "INSERT INTO Graph VALUES (?, ?, ?, ?)",
}

strptime_map = [
    "%b %d %-I:%M%p",
    "%b %d %-I%p",
    "%b %d"
]

def push_average(sums: list[int, float, float, int], count: int, averages: list, map_index: int):
    temp = []

    date = datetime.strptime(time.ctime(sums[0] / count),  "%a %b %d %H:%M:%S %Y")
    date = date.strftime(strptime_map[map_index])

    temp.append(date)
    temp.append("{:.2f}".format(sums[1] / count))
    temp.append("{:.2f}".format(sums[2] / count))

    if (sums[3] / count > 0):
        temp.append(True)
    else:
        temp.append(False)
        
    averages.append({'Time': temp[0], 'Temperature': temp[1], 'Humidity': temp[2], 'Error': temp[3]})

def average_entries(data: list[tuple[int, float, float, int]], map_index: int) -> list[dict[str:str, str:float, str:float, str:bool]]:
    arr = []

    group = 1
    if map_index == 1:
        group = 60
    elif map_index == 2:
        group = 60 * 24

    i = 0
    sums = [0, 0, 0, 0]
    c = 0
    current = 0

    while i < len(data):
        if (current == 0):
            current = data[i][0] // (group * 60)
        elif (data[i][0] // (group * 60) != current):
            push_average(sums, c, arr, map_index)

            sums = [0, 0, 0, 0]
            c = 0
            current = 0

        for q in range(4):
            sums[q] += data[i][q]

        c += 1
        i += 1

    # cleanup
    if c > 0:
        push_average(sums, c, arr, map_index)

    return arr

# helper functions

def db() -> tuple[sql.Connection, sql.Cursor]:
    con = sql.connect("./database.db")
    return con, con.cursor()

def init_conf() -> None:
    # adds the config table if it doesn't already exist and adds a default configuration

    con, cur = db()

    cur.execute(queries["create_config_table"])

    if cur.execute(queries["check_config_count"]).fetchone()[0] < 1:
        cur.execute(queries["add_default_config"])

    con.commit()
    return

def init_graph() -> None:
    con, cur = db()

    cur.execute(queries["create_graph_table"])

    con.commit()
    return

def confs_to_dict(confs: list[tuple[int, int, float, float]]) -> dict[str:int, str:float, str:float]:
    if len(confs) > 0:
        c = confs[0]

        if len(confs) > 1:
            c = confs[1]

        enable = c[0]
        open = c[1]

        op = 0
        if enable and open:
            op = 3 # 0b11
        elif enable:
            op = 2 # 0b10
        
        return {
            "manual_open": op,
            "open_temperature": c[2],
            "close_temperature": c[3]
        }

    return

# exported functions

def get_arduino_conf() -> dict[str:bool, str:bool, str:float, str:float]:
    init_conf()

    con, cur = db()

    records = cur.execute(queries["get_config"]).fetchall()

    return confs_to_dict(records)

def set_arduino_conf(man_enabled: bool, man_open: bool, open_temp: float, close_temp: float) -> None:
    init_conf()

    con, cur = db()

    # remove existing custom config if it exists
    cur.execute(queries["remove_existing_config"])
    con.commit()

    # add new config
    cur.execute(queries["add_config"], (int(man_enabled), int(man_open), float(open_temp), float(close_temp)))
    con.commit()
    
    return

def get_graph_data(maxtime: int) -> list[tuple[int, float, float, bool]]: # dict[str:list[int], str:list[float], str:list[float], str:list[bool]]:
    init_graph()

    con, cur = db()

    entries = cur.execute(queries["get_graph_data"], (maxtime,)).fetchall()
    return entries

def add_graph_entry(timestamp: int, temperature: float, humidity: float, has_error: bool) -> None:
    init_graph()

    con, cur = db()

    # TODO set max limit to a changeable value
    # remove old entries
    cur.execute(queries["remove_old_graph_entries"], (60 * 60 * 24 * 30,))
    con.commit()

    cur.execute(queries["add_graph_entry"], (timestamp, temperature, humidity, int(has_error)))
    con.commit()

    return
