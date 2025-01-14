

from datetime import datetime


def write_log(msg):
    logfile = f"log_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(f".\\log\\{logfile}", mode="a") as lf:
        lf.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} {msg}\n")
