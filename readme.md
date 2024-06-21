
## Run local

0) 
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

1) Run pip install
```bash
    pip install --no-cache-dir -r requirements.txt
```

2) Run .py

## Container Run

```bash
# Construir a imagem Docker
docker build -t spotify-controller .

# Rodar o contêiner Docker
docker run -p 5000:5000 -d spotify-controller
```

## Sample scheduler.json

```json
 [
    {
        "action": "play",
        "date": {
            "year": 2024,
            "month": 6,
            "day": 18,
            "hour": 22,
            "minute": 56,
            "timezone": "UTC"
        }
    },
    {
        "action": "play",
        "file": "music/song1.mp3",
        "cron": {
            "day_of_week": "sat",
            "hour": 8,
            "minute": 0,
            "timezone": "UTC"
        }
    },
    {
        "action": "pause",
        "cron": {
            "day_of_week": "sat",
            "hour": 13,
            "minute": 0,
            "timezone": "UTC"
        }
    },
    {
        "action": "play",
        "file": "musics/",
        "date": {
            "year": 2024,
            "month": 6,
            "day": 21,
            "hour": 0,
            "minute": 48
        }
    },
    {
        "action": "stop",
        "date": {
            "year": 2024,
            "month": 6,
            "day": 21,
            "hour": 0,
            "minute": 49
        }
    }
]

```