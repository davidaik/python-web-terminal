import socketio
from flask import Flask, render_template, url_for
import sys
import subprocess

import thread
import time

sio = socketio.Server(async_mode='threading')
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)


@app.route('/')
def get_index():
    return render_template('index.html')




def exec_code(code_string):
    from cStringIO import StringIO
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    exec(code_string)
    sys.stdout = old_stdout
    print(redirected_output.getvalue())






@sio.on('connect')
def connect(sid, environ):
    print('CONNECTED!!!!!!!!!!!!!! ')
    sys.stdout.flush()
    '''
    proc = subprocess.Popen(['python', '-u', 'test.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)
    thread.start_new_thread(prompt_user, (proc, ))
    proc.stdin.write("David")
    print proc.communicate()[0]
    proc.stdin.close()

    while True:
        line = proc.stdout.readline()
        if line != '':
            print(line.rstrip())
            sys.stdout.flush()
        else:
            break
    '''


@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)


@sio.on('run_program')
def run_program(sid, data):
    sio.save_session(sid, {'user_input_line': None})
    proc = subprocess.Popen(['python', '-u', 'run_program.py', data], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)
    thread.start_new_thread(prompt_user, (sid, proc, ))


    # proc.stdin.write("David")
    # print proc.communicate()[0]
    # proc.stdin.close()
    '''while True:
        line = proc.stdout.readline()
        if line != '':
            # print(line.rstrip())
            # sys.stdout.flush()
            sio.emit('stdout', {'data': line})
        else:
            break'''


@sio.on('user_input')
def user_input(sid, data):
    sio.save_session(sid, {'user_input_line': data})


def prompt_user(sid, proc):
    while True:
        if proc.poll() is not None:
            print('HEFRE')
            sys.stdout.flush()
            break
        session = sio.get_session(sid)
        user_input_line = session['user_input_line']

        if user_input_line:
            line = proc.communicate(user_input_line)[0]
        else:
            line = proc.communicate('"hehehe"\n')[0]
        if line:
            sio.emit('stdout', {'data': line})
            time.sleep(3)

    print('THREAD STOPPED')
    sys.stdout.flush()


if __name__ == '__main__':
    app.debug = True
    app.run(port='8000', threaded=True)
