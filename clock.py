import logging
logging.basicConfig()
import os
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone

sched = BlockingScheduler({'apscheduler.timezone': timezone('Asia/Calcutta')})
@sched.scheduled_job('cron', day_of_week='mon-sun', hour=12, minute=45)
def scheduled_job():
    os.system('python PyScriptDailyNotification.py')
sched.start()