import logging
import logging.config
from multiprocessing import Process
import api
import schedule
import os
import time
from datetime import datetime
from cronjob.cronjob import Cronjob

def setup_logging() -> None:
    config_path = "./config/logging.ini"
    
    timestamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")

    logging.config.fileConfig(
        config_path,
        disable_existing_loggers=False,
        defaults={"logfilename": os.path.join("./logs", f"{timestamp}.log")},
    )

def start_api() -> None:
    import uvicorn
    uvicorn.run("api.api:app", host="0.0.0.0", port=3000, reload=False)
    
def run_cronjob():
    c = Cronjob()
    c.hackernews_to_mail_flow()
    
def schedule_something():
    schedule.every().day.at("06:11").do(run_cronjob)
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logging.exception("Couldn't run daily flow")
        time.sleep(1)

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting main.py")
    p1 = Process(target=schedule_something)
    p1.start()
    p2 = Process(target=start_api)
    p2.start()
    p1.join()
    p2.join()

if __name__ == "__main__":
    main()
