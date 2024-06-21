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

tz = get_localzone()
print(f"Timezone local: {0}",tz)

# Criar um scheduler de plano de fundo
default_timezone = 'America/Sao_Paulo'
scheduler = BackgroundScheduler(timezone=timezone(default_timezone))
scheduler.start()

playlist = []
play_obj = None
stop_playback = False

def convert_mp3_to_wav(mp3_file):
    # Carregar arquivo MP3
    audio = AudioSegment.from_mp3(mp3_file)
    
    # Salvar como arquivo WAV temporário
    wav_file = mp3_file.replace('.mp3', '.wav')
    audio.export(wav_file, format='wav')
    
    return wav_file

def play_playlist(directory):
    global playlist
    playlist = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.mp3')]
    play_next_music()

def play_next_music():
    global play_obj, stop_playback  

    if playlist:
        file = playlist.pop(0)
        print(f'Playing {file}')
        
        # Converter MP3 para WAV antes de reproduzir com simpleaudio
        wav_file = convert_mp3_to_wav(file)
        
        # Reproduzir WAV usando simpleaudio
        wave_obj = sa.WaveObject.from_wave_file(wav_file)
        play_obj = wave_obj.play()
        play_obj.wait_done()

        while not stop_playback:
            if not play_obj.is_playing():
                break
            time.sleep(0.1)

        # Remover arquivo WAV temporário após reprodução
        os.remove(wav_file)

def stop_playlist():
    global stop_playback

    if play_obj:
        stop_playback = True
        play_obj.stop()
        print('Música parada.')


def load_schedule():
    with open('schedule.json') as f:
        tasks = json.load(f)
    
    for task in tasks:
        action = task['action']
        cron = task.get('cron')
        date = task.get('date')
        file = task.get('file')
        
        if cron:
            print(f'Configure via cron {cron} action {action}')
            if action == 'stop':
                scheduler.add_job(stop_playlist, 'cron', **cron)
            elif action == 'play' and file:
                scheduler.add_job(play_playlist, 'cron', **cron, args=[file])
            else:
                print(f'Invalid cron task configuration: {task}')
        elif date:
            print(f'Configure via date {date} action {action}')
            date_time = datetime(**date)
            if action == 'play' and file:
                scheduler.add_job(play_playlist, 'date',  args=[file], run_date=date_time) #timezone datetime(2024,6,19,1,5)
            elif action == 'stop':
                scheduler.add_job(stop_playlist, 'date', run_date=date_time) #timezone datetime(2024,6,19,1,5)
            else:
                print(f'Invalid date task configuration: {task}')
        else:
            print(f'Invalid task configuration: {task}')

if __name__ == '__main__':
    load_schedule()
    print('Scheduler started with the following jobs:')
    for job in scheduler.get_jobs():
        print(job)

    try:
        # Manter o script rodando
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
