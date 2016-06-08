# requires https://pypi.python.org/pypi/websocket-client/

from excepthook import uncaught_exception, install_thread_excepthook
import sys
sys.excepthook = uncaught_exception
install_thread_excepthook()

# !! Important! Be careful when adding code/imports before this point.
# Our except hook is installed here, so any errors before this point
# won't be caught if they're not in a try-except block.
# Hence, please avoid adding code before this comment; if it's necessary,
# test it thoroughly.

import websocket
import getpass
from threading import Thread
import traceback
from bodyfetcher import BodyFetcher
from chatcommunicate import watcher, special_room_watcher
from datetime import datetime
from utcdate import UtcDate
from spamhandling import check_if_spam_json
from globalvars import GlobalVars
from datahandling import load_files, filter_auto_ignored_posts
from metasmoke import Metasmoke
from deletionwatcher import DeletionWatcher
import os
import time
import requests

if "ChatExchangeU" in os.environ:
    username = os.environ["ChatExchangeU"]
else:
    username = raw_input("Username: ")
if "ChatExchangeP" in os.environ:
    password = os.environ["ChatExchangeP"]
else:
    password = getpass.getpass("Password: ")

# We need an instance of bodyfetcher before load_files() is called
GlobalVars.bodyfetcher = BodyFetcher()

load_files()
filter_auto_ignored_posts()

GlobalVars.wrap.login(username, password)
GlobalVars.smokeDetector_user_id[GlobalVars.charcoal_room_id] = str(GlobalVars.wrap.get_me().id)
GlobalVars.s = "[ [Smokey McSmokeface](https://github.com/Undo1/Smokey-McSmokeface) ] " \
               "SmokeDetector started at [rev " +\
               GlobalVars.commit_with_author +\
               "](https://github.com/Undo1/Smokey-McSmokeface/commit/" +\
               GlobalVars.commit +\
               ") (running on " +\
               GlobalVars.location +\
               ")"
GlobalVars.s_reverted = "[ [Smokey McSmokeface](https://github.com/Undo1/Smokey-McSmokeface) ] " \
                        "SmokeDetector started in [reverted mode](https://github.com/Undo1/Smokey-McSmokeface/blob/master/RevertedMode.md) " \
                        "at [rev " + \
                        GlobalVars.commit_with_author + \
                        "](https://github.com/Undo1/Smokey-McSmokeface/commit/" + \
                        GlobalVars.commit + \
                        ") (running on " +\
                        GlobalVars.location +\
                        ")"

GlobalVars.charcoal_hq = GlobalVars.wrap.get_room(GlobalVars.charcoal_room_id)

# If you change these sites, please also update the wiki at
# https://github.com/Charcoal-SE/SmokeDetector/wiki/Chat-Rooms

GlobalVars.specialrooms = []


def restart_automatically(time_in_seconds):
    time.sleep(time_in_seconds)
    os._exit(1)

Thread(target=restart_automatically, args=(21600,)).start()

DeletionWatcher.update_site_id_list()

ws = websocket.create_connection("ws://qa.sockets.stackexchange.com/")
ws.send("155-questions-active")
GlobalVars.charcoal_hq.join()

GlobalVars.charcoal_hq.watch_socket(watcher)
for room in GlobalVars.specialrooms:
    if "watcher" in room:
        room["room"].join()
        room["room"].watch_socket(special_room_watcher)

#if "first_start" in sys.argv and GlobalVars.on_master:
#    GlobalVars.charcoal_hq.send_message(GlobalVars.s)
#elif "first_start" in sys.argv and not GlobalVars.on_master:
#    GlobalVars.charcoal_hq.send_message(GlobalVars.s_reverted)

Metasmoke.send_status_ping()  # This will call itself every minute or so

while True:
    try:
        a = ws.recv()
        if a is not None and a != "":
            is_spam, reason, why = check_if_spam_json(a)
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        now = datetime.utcnow()
        delta = now - UtcDate.startup_utc_date
        seconds = delta.total_seconds()
        tr = traceback.format_exc()
        exception_only = ''.join(traceback.format_exception_only(type(e), e))\
                           .strip()
        n = os.linesep
        logged_msg = str(now) + " UTC" + n + exception_only + n + tr + n + n
        print(logged_msg)
        with open("errorLogs.txt", "a") as f:
            f.write(logged_msg)
        if seconds < 180 and exc_type != websocket.WebSocketConnectionClosedException\
                and exc_type != KeyboardInterrupt and exc_type != SystemExit and exc_type != requests.ConnectionError:
            os._exit(4)
        ws = websocket.create_connection("ws://qa.sockets.stackexchange.com/")
        ws.send("155-questions-active")
        # GlobalVars.charcoal_hq.send_message("Recovered from `" + exception_only + "`")

now = datetime.utcnow()
delta = UtcDate.startup_utc_date - now
seconds = delta.total_seconds()
if seconds < 60:
    os._exit(4)
s = "[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] SmokeDetector aborted"
GlobalVars.charcoal_hq.send_message(s)
