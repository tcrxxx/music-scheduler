#!/usr/bin/python3
import json
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
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

# Logger settings
logger = logging.getLogger('music-scheduler')
logger.setLevel(logging.DEBUG)
logger.propagate = False # Avoid duplicate logs
log_formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')

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
try:
    # frequency=44100, size=-16, channels=2, buffer=4096
    mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
except Exception as e:
    if "ALSA" in str(e) and os.name == 'posix':
        logger.warning("ALSA failure detected. Attempting to auto-fix /home/admin/.asoundrc...")
        try:
            with open('/home/admin/.asoundrc', 'w') as f:
                f.write("pcm.!default {\n    type hw\n    card 2\n}\n\nctl.!default {\n    type hw\n    card 2\n}\n")
            logger.info("Created /home/admin/.asoundrc. Exiting to allow systemd to restart with new configuration...")
            sys.exit(1) # Exit with error to trigger systemd restart
        except Exception as fix_err:
            logger.critical(f"Failed to auto-fix ALSA config: {fix_err}")
            raise e
    else:
        raise e
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
                scheduler.add_job(play_playlist, 'cron', **cron, args=[file], misfire_grace_time=360)
            elif action == 'stop':
                scheduler.add_job(stop_playlist, 'cron', **cron, misfire_grace_time=360)
            else:
                logger.info(f'Invalid cron task configuration: {task}')
        elif date:
            logger.info(f'Configure via date {date} action {action}')
            date_time = datetime(**date)
            # Ensure date_time has timezone info if needed, but here we use the scheduler's default
            if action == 'play' and file:
                scheduler.add_job(play_playlist, 'date',  args=[file], run_date=date_time, misfire_grace_time=360) #timezone datetime(2024,6,19,1,5)
            elif action == 'stop':
                scheduler.add_job(stop_playlist, 'date', run_date=date_time, misfire_grace_time=360) #timezone datetime(2024,6,19,1,5)
            else:
                logger.info(f'Invalid date task configuration: {task}')
        else:
            logger.info(f'Invalid task configuration: {task}')
    
    check_startup_playback(tasks)

def get_last_fire_time(trigger, now):
    if isinstance(trigger, CronTrigger):
        # To find the last fire time, we start from a week ago and find the latest one before 'now'
        last_fire = None
        current_check = now - timedelta(days=8) # 8 days to be safe for weekly cycles
        while True:
            next_fire = trigger.get_next_fire_time(last_fire, current_check if last_fire is None else last_fire)
            if next_fire is None or next_fire > now:
                break
            last_fire = next_fire
        return last_fire
    elif isinstance(trigger, DateTrigger):
        if trigger.run_date <= now:
            return trigger.run_date
    return None

def check_startup_playback(tasks):
    logger.info("Checking if playback should start immediately...")
    now = datetime.now(timezone(default_timezone))
    
    last_play_time = None
    last_play_file = None
    last_stop_time = None
    
    for task in tasks:
        action = task['action']
        cron = task.get('cron')
        date = task.get('date')
        file = task.get('file')
        
        trigger = None
        if cron:
            trigger = CronTrigger(timezone=timezone(default_timezone), **cron)
        elif date:
            trigger = DateTrigger(run_date=datetime(**date), timezone=timezone(default_timezone))
            
        if trigger:
            fire_time = get_last_fire_time(trigger, now)
            if fire_time:
                if action == 'play':
                    if last_play_time is None or fire_time > last_play_time:
                        last_play_time = fire_time
                        last_play_file = file
                elif action == 'stop':
                    if last_stop_time is None or fire_time > last_stop_time:
                        last_stop_time = fire_time
    
    if last_play_time:
        if last_stop_time is None or last_play_time > last_stop_time:
            logger.info(f"Startup check: Last 'play' ({last_play_time}) is more recent than last 'stop' ({last_stop_time}). Starting playback.")
            # Start play_playlist in a background thread or just call it if we are already in the main loop?
            # Actually, play_playlist is a blocking loop. We should run it like the scheduler would.
            # However, the scheduler is ALREADY running. We can just trigger the job now.
            if last_play_file:
                # We add a one-off job to start now
                scheduler.add_job(play_playlist, 'date', args=[last_play_file], run_date=now)
        else:
            logger.info(f"Startup check: Last 'stop' ({last_stop_time}) is more recent than last 'play' ({last_play_time}). Waiting for next scheduled event.")
    else:
        logger.info("Startup check: No previous play events found.")

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
