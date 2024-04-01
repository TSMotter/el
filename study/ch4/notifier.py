#!/usr/bin/env python3

import subprocess
import time
import shlex

def execute_command(command):
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
    if len(sys.argv) > 2:
        command = " ".join(sys.argv[1:])
        execution_time = execute_command(shlex.split(command))
        send_notification(f"Command '{command}' finished.\nExecution time: {execution_time:.2f} seconds.")
    else:
        print("Invalid command. Usage: notifier make <make_command>")
