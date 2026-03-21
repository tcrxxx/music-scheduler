#!/usr/bin/python3
import json
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
from pygame import mixer
import pytz
import signal
import sys
from pytz import timezone
import os
from tzlocal import get_localzone
import random
import logging
import logging.handlers

# Logger settings
logger = logging.getLogger('music-scheduler')
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
# SysLog (Unix only)
if os.name == 'posix':
    try:
        syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
        syslog_handler.setFormatter(log_formatter)
        logger.addHandler(syslog_handler)
    except Exception:
        pass
# FileLog
log_file = 'music-scheduler.log'
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)
# ConsoleLog
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)


# Scheduler Settings
tz = get_localzone()
logger.info(f"Timezone local: {0}")
default_timezone = 'America/Sao_Paulo'
scheduler = BackgroundScheduler(timezone=timezone(default_timezone))
scheduler.start()

# Audio Settings
mixer.init()
playlist = []
stop_playback = False
is_exiting = False

def signal_handler(sig, frame):
    global stop_playback, is_exiting
    logger.info(f"Received signal {sig}. Exiting gracefully...")
    stop_playback = True
    is_exiting = True
    mixer.music.stop()
    # Note: the scheduler shutdown will be handled in the main try-except block

# Register signals
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)



def play_playlist(directory):
    global playlist
    load_playlist(directory)
    while not stop_playback:
        if playlist:
            play_next_music()
        else:
            load_playlist(directory)

def load_playlist(directory):
    global playlist
    playlist = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.mp3', '.wav'))]

    # Set playlist to random 
    logger.info("Shuffle playlist order")
    random.shuffle(playlist)

def play_next_music():
    global stop_playback
    
    if playlist:
        file = playlist.pop(0)
        logger.info(f'Playing {file}')
        
        try:
            mixer.music.load(file)
            mixer.music.play()
            
            # Wait for music to finish or stop signal
            while mixer.music.get_busy() and not stop_playback:
                time.sleep(0.1)
                
            if stop_playback:
                mixer.music.stop()
                
        except Exception as e:
            logger.error(f"Error playing {file}: {e}")

def stop_playlist():
    global stop_playback
    stop_playback = True
    mixer.music.stop()
    logger.info('Music stopped!')

def load_schedule():
    with open('schedule.json') as f:
        tasks = json.load(f)
    
    for task in tasks:
        action = task['action']
        cron = task.get('cron')
        date = task.get('date')
        file = task.get('file')
        
        if cron:
            logger.info(f'Configure via cron {cron} action {action}')
            if action == 'play' and file:
                scheduler.add_job(play_playlist, 'cron', **cron, args=[file])
            elif action == 'stop':
                scheduler.add_job(stop_playlist, 'cron', **cron)
            else:
                logger.info(f'Invalid cron task configuration: {task}')
        elif date:
            logger.info(f'Configure via date {date} action {action}')
            date_time = datetime(**date)
            if action == 'play' and file:
                scheduler.add_job(play_playlist, 'date',  args=[file], run_date=date_time) #timezone datetime(2024,6,19,1,5)
            elif action == 'stop':
                scheduler.add_job(stop_playlist, 'date', run_date=date_time) #timezone datetime(2024,6,19,1,5)
            else:
                logger.info(f'Invalid date task configuration: {task}')
        else:
            logger.info(f'Invalid task configuration: {task}')

if __name__ == '__main__':
    load_schedule()
    logger.info('Scheduler started with the following jobs:')
    for job in scheduler.get_jobs():
        logger.info(job)

    try:
        # Keep the script running
        while not is_exiting:
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Exit requested.")
    finally:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown(wait=False)
        mixer.quit()
        logger.info("Application stopped.")
