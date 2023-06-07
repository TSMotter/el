#!/usr/bin/env python3

import subprocess
import time
import shlex

def execute_make_command(command):
    start_time = time.time()
    process = subprocess.Popen(command, shell=True, stdout=sys.stdout, stderr=sys.stderr, universal_newlines=True)
    process.wait()
    end_time = time.time()
    execution_time = end_time - start_time
    return execution_time

def send_notification(message):
    subprocess.call(['notify-send','mmake', message])

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "make":
        make_command = " ".join(sys.argv[1:])
        execution_time = execute_make_command(shlex.split(make_command))
        send_notification(f"Make command '{make_command}' finished.\nExecution time: {execution_time:.2f} seconds.")
    else:
        print("Invalid command. Usage: doitforme make <make_command>")
