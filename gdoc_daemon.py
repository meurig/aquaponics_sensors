#!/usr/bin/python

# Depends on the python-daemon library to behave correctly as a daemon
# execute:
#   sudo apt-get install python-daemon

from daemon import runner
from gdoc_sensors import do_main_program

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/var/run/gdoc_daemon.pid'
        self.pidfile_timeout = 5
    def run(self):
	do_main_program()

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
