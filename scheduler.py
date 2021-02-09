# Scheduler for simplecast data colection
# https://schedule.readthedocs.io/en/stable/

import os
# from apscheduler.schedulers.blocking import BlockingScheduler
from simplecast_data_collector import simplecast_data_collector, getSimplecastResponse
import time
import schedule

 # schedule.every().wednesday.at("13:15").do(job)
print('Setting up schedule...')
schedule.every().monday.at("11:30").do(simplecast_data_collector)


print('schedule created!')