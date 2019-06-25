#!/usr/bin/env python3

import socketio
from flask import Flask, render_template, url_for
import os
import signal
import sys
import subprocess

from threading import Thread
import fcntl
import _thread as thread
import time


sio = socketio.Server(async_mode='threading')
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)

execute_python_version = 2

def kill_process(pid):
    try:
        os.kill(pid, signal.SIGTERM) #or signal.SIGKILL
    except:
        pass


def add_process_start_time_to_session(sid, pid):
    session = sio.get_session(sid)
    if session:
        session['process_start_time'] = pid
    else:
        session = {'process_start_time': pid}
    sio.save_session(sid, session)


def add_pid_to_session(sid, pid):
    # Save the pid of the child process spawned
    session = sio.get_session(sid)
    if session:
        session['running_process_id'] = pid
    else:
        session = {'running_process_id': pid}
    sio.save_session(sid, session)
    return session


def add_user_input_to_session(sid, input):
    session = sio.get_session(sid)
    if session:
        session['user_input_line'] = input
    else:
        session = {'user_input_line': input}
    sio.save_session(sid, session)
    return session


def get_running_process_id(sid):
    session = sio.get_session(sid)
    if session and 'running_process_id' in session:
        return session['running_process_id']
    else:
        return None


def get_user_input_line(sid):
    session = sio.get_session(sid)
    if session and 'user_input_line' in session:
        return session['user_input_line']
    else:
        return None


@app.route('/')
def get_index():
    return render_template('index.html')


@sio.on('connect')
def connect(sid, environ):
    # print('User connected!')
    sys.stdout.flush()


@sio.on('disconnect')
def disconnect(sid):
    # print('User disconnected!')
    sys.stdout.flush()


@sio.on('run_program')
def run_program(sid, data):
    proc = None
    if execute_python_version == 3:
        proc = subprocess.Popen(['python3', 'run_program.py', data], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
    else:
        proc = subprocess.Popen(['python2.7', '-u', 'run_program_2.py', data], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)
    
    set_non_block(proc.stdout)

    running_process_id = get_running_process_id(sid)
    if running_process_id:
        print('KILLING PROCESS')
        kill_process(running_process_id)
    
    sio.save_session(sid, {'user_input_line': None, 'running_process_id': proc.pid})
    thread.start_new_thread(start_io_loop, (sid, proc, ))


@sio.on('user_input')
def user_input(sid, data):
    add_user_input_to_session(sid, data)


def start_io_loop(sid, proc):
    while True:        
        user_input_line = get_user_input_line(sid)
        add_user_input_to_session(sid, None)

        if user_input_line:
            proc.stdin.write('{}{}'.format(user_input_line,'\n').encode('utf-8'))
            proc.stdin.flush()
        line = read(proc.stdout)
        if line:
            sio.emit('stdout', {'data': line.decode('utf-8')})
            time.sleep(0.2)

        if proc.poll() is not None:
            sio.emit('stdout', {'data': 'program_finished'})
            add_pid_to_session(sid, None)
            break


'''
Solution by Chase Seibert.
https://chase-seibert.github.io/blog/2012/11/16/python-subprocess-asynchronous-read-stdout.html
'''
def set_non_block(stdout):
    fd = stdout.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)


def read(stdout):
    try:
        return stdout.read()
    except:
        return ''


if __name__ == '__main__':
    app.debug = True
    app.run(port='8000', threaded=True)
