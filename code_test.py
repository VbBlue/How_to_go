from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=5)
@sched.scheduled_job('interval', seconds=10)
def timed_job():
    print('This job is run every three minutes.')

@sched.scheduled_job('cron', hour='6', minute='13')
def scheduled_job():
    print('This job is run every weekday at 5pm.')

