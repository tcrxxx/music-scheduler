
## Run local

0) Em seu sistema operacional Linux execute:

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

1) Rode então o pip install:

```bash
sudo pip install --no-cache-dir -r requirements.txt --break-system-packages
```

* Obs.: Use --break-system-packages para instalar pacotes no sistema operacional Linux como Raspberry pi

2) Rode seu music-scheduler.py (tenha atenção as configurações de cron ou date informada no schedule e a música na pasta /musics)

## Install on linux service

Para instalar e executar um script Python como um serviço no Linux, você pode usar o `systemd`, que é o sistema de inicialização e gerenciamento de serviços padrão na maioria das distribuições Linux modernas. Aqui estão os passos detalhados para criar e instalar o seu script Python como um serviço no Linux.

### Passo a Passo:

1. **Crie um Arquivo de Serviço do `systemd`:**
   Crie um arquivo de serviço para o `systemd` na pasta `/etc/systemd/system/`. 
   
   **Nota:** Substitua `/caminho/para/o/` pelo caminho real onde seu script Python está localizado. Certifique-se de que o caminho para o interpretador Python (`/usr/bin/python3`) está correto. Além disso, substitua `seu_usuario` e `seu_grupo` pelo usuário e grupo apropriados.

2. **Dê permissão de execução ao script:**
   Certifique-se de que o script Python tenha permissão de execução.

   ```bash
   chmod +x music-scheduler.py
   ```

3. **Recarregue o `systemd` e Habilite o Serviço:**

   Abra um terminal e execute os seguintes comandos:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable music-scheduler.service
   sudo systemctl start music-scheduler.service
   ```

4. **Verifique o Status do Serviço:**

   Para garantir que o serviço está rodando corretamente, você pode verificar o status:

   ```bash
   sudo systemctl status music-scheduler.service
   ```

   Isso deve mostrar a saída indicando que o serviço está ativo e rodando.

5. **Logs e Depuração:**

   Se houver problemas, você pode verificar os logs do serviço usando o `journalctl`:

   ```bash
   sudo journalctl -u music-scheduler.service -f
   ```

## Sample schedule.json

- file property is a directory path. samples: "/opt/music-scheduler/musics/" or "c:/Users/Administrador/developer/repos/music-scheduler/musics/"
- cron property is a cron expression. samples: {"day_of_week": "fri", "hour": 0, "minute": 54}
- date property is a date expression. samples: {"year": 2024, "month": 6, "day": 21, "hour": 0, "minute": 48}

```json
 [
    {
        "action": "play",
        "file": "musics/",
        "cron": {
            "day_of_week": "fri",
            "hour": 0,
            "minute": 54
        }
    },
    {
        "action": "stop",
        "cron": {
            "day_of_week": "fri",
            "hour": 0,
            "minute": 59
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

## Falhas possíveis

- pygame.error: ALSA: Couldn't open audio device: Unknown error 524

solução:

```bash
sudo vim /home/admin/.asoundrc
```

```
pcm.!default {
    type hw
    card 2
}

ctl.!default {
    type hw
    card 2
}
```