import socketio
from flask import Flask, render_template, url_for
import os
import sys
import subprocess

from threading import Thread
import fcntl
import _thread as thread
import time

sio = socketio.Server(async_mode='threading')
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)


@app.route('/')
def get_index():
    return render_template('index.html')


@sio.on('connect')
def connect(sid, environ):
    print('User connected!')
    sys.stdout.flush()


@sio.on('disconnect')
def disconnect(sid):
    print('User disconnected!')
    sys.stdout.flush()


@sio.on('run_program')
def run_program(sid, data):
    sio.save_session(sid, {'user_input_line': None})
    proc = subprocess.Popen(['python3', 'run_program.py', data], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
    thread.start_new_thread(prompt_user, (sid, proc, ))


@sio.on('user_input')
def user_input(sid, data):
    sio.save_session(sid, {'user_input_line': data})


def prompt_user(sid, proc):
    while True:
        if proc.poll() is not None:
            print('Process already stopped')
            sio.emit('stdout', {'data': 'Program finished'})
            sys.stdout.flush()
            break
        session = sio.get_session(sid)
        user_input_line = session['user_input_line']
        sio.save_session(sid, {'user_input_line': None})
        if user_input_line:
            proc.stdin.write('{}{}'.format(user_input_line,'\n').encode('utf-8'))
            proc.stdin.flush()
        line = non_block_read(proc.stdout)
        if line:
            sio.emit('stdout', {'data': line.decode('utf-8')})
            time.sleep(1)


'''
Solution by Chase Seibert.
https://chase-seibert.github.io/blog/2012/11/16/python-subprocess-asynchronous-read-stdout.html
'''
def non_block_read(stdout):
    fd = stdout.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return stdout.read()
    except:
        return ''


if __name__ == '__main__':
    app.debug = True
    app.run(port='8000', threaded=True)
