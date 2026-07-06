import datetime

log_path = r"C:\Automation\logs\signals.log"

with open(log_path, "a") as f:
    f.write(f"Signal check ran at {datetime.datetime.now()}\n")

print("Collector ran successfully")