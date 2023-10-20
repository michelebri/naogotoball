import threading
import subprocess

def run_script(script_path):
    subprocess.Popen(["python2", script_path])

def run_script3(script_path):
    subprocess.Popen(["python", script_path])

if __name__ == "__main__":
    script1_path = "detect.py"
    script2_path = "acquis.py"

    thread1 = threading.Thread(target=run_script3, args=(script1_path,))
    thread2 = threading.Thread(target=run_script, args=(script2_path,))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
