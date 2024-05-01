from multiprocessing import Process
import api
import schedule
import time
from cronjob.cronjob import Cronjob

def start_api():
    import uvicorn
    uvicorn.run("api.api:app", host="0.0.0.0", port=3000, reload=True)
    
def schedule_something():
    schedule.every().day.at("06:00").do(Cronjob().hackernews_to_mail_flow)
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    p1 = Process(target=schedule_something)
    p1.start()
    p2 = Process(target=start_api)
    p2.start()
    p1.join()
    p2.join()

if __name__ == "__main__":
    main()
