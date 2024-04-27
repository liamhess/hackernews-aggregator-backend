import api
import asyncio
import schedule
import time

async def start_api():
    import uvicorn
    uvicorn.run("api.api:app", host="0.0.0.0", port=3000, reload=True)
    
def job():
    print("hehehe")
    
async def schedule_something():
    schedule.every(5).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

async def main():
    start_api()
    schedule_something()

if __name__ == "__main__":
    asyncio.run(main())
