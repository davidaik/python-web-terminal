#!/usr/bin/env python3

import argparse
import base64
import sys

def get_script_from_args():
    parser = argparse.ArgumentParser(description='Get script')
    parser.add_argument('script', type=str)
    args = parser.parse_args()
    return args.script


if __name__ == '__main__':
    encoded_script_string = get_script_from_args()
    decoded_code_string = base64.b64decode(encoded_script_string)
    try:
        exec(decoded_code_string)
    except Exception as e:
        print(e)
        sys.stdout.flush()
        pass
