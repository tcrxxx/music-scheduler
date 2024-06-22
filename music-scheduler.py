import json
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
from pydub import AudioSegment
import pytz
import simpleaudio as sa
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
# SysLog
syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
syslog_handler.setFormatter(log_formatter)
logger.addHandler(syslog_handler)
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

playlist = []
play_obj = None
stop_playback = False

def convert_mp3_to_wav(mp3_file):
    # Load MP3 File
    audio = AudioSegment.from_mp3(mp3_file)
    
    # Save temporary WAV file
    wav_file = mp3_file.replace('.mp3', '.wav')
    audio.export(wav_file, format='wav')
    
    return wav_file

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
    global play_obj, stop_playback
    isMP3Converted = False

    if playlist:
        file = playlist.pop(0)
        logger.info(f'Check {file}')
        
        if(file.endswith('.mp3')):
            logger.info(f'Converting {file}')
            wav_file = convert_mp3_to_wav(file)
            isMP3Converted = True
        else:
            wav_file = file
        
        logger.info(f'Playing {file}')
        wave_obj = sa.WaveObject.from_wave_file(wav_file)
        play_obj = wave_obj.play()
        play_obj.wait_done()

        while not stop_playback:
            if not play_obj.is_playing():
                break
            time.sleep(0.1)

        # Remove temporary wav file
        if(isMP3Converted):
            logger.info(f'Removing {file}')
            os.remove(wav_file)

def stop_playlist():
    global stop_playback

    if play_obj:
        stop_playback = True
        play_obj.stop()
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
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
