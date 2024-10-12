import os
import signal

def restart_gunicorn():
    try:
        with open('/tmp/gunicorn.pid', 'r') as f:
            pid = int(f.read())
            os.kill(pid, signal.SIGHUP)  # Mengirim sinyal HUP untuk merestart
    except Exception as e:
        print(f'Error restarting Gunicorn: {e}')
