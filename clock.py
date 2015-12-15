from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=17)
def scheduled_job():
    PyScriptDailyNotification.py
sched.start()