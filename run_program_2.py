#!/usr/bin/env python2.7

# Run Python 2 scripts passed as argument

import os
import signal
import sys
import argparse
import base64
import time
import thread

program_start_time = 0
program_running = True

def get_script_from_args():
    parser = argparse.ArgumentParser(description='Get script')
    parser.add_argument('script', type=str)
    args = parser.parse_args()
    return args.script

def start_autostop_loop():
    while True:
        if not program_running:
            break
        check_and_stop_program()
        time.sleep(1)

def check_and_stop_program():
    elapsed_time = time.time() - program_start_time
    if elapsed_time > 300: # Stop process after 5 minutes
        os.kill(os.getpid(), signal.SIGTERM)


if __name__ == '__main__':
    program_start_time = time.time()
    thread = thread.start_new_thread(start_autostop_loop, ())

    encoded_script_string = get_script_from_args()
    decoded_code_string = base64.b64decode(encoded_script_string)
    try:
        exec decoded_code_string
    except Exception as e:
        print e
        sys.stdout.flush()
        pass
    program_running = False
