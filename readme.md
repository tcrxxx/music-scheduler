
## Run local

0) Em seu sistema operacional Linux execute:

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

1) Rode então o pip install:

```bash
    pip install --no-cache-dir -r requirements.txt
```

2) Rode seu music-scheduler.py (tenha atenção as configurações de cron ou date informada no schedule e a música na pasta /musics)

## Install on linux service

Para instalar e executar um script Python como um serviço no Linux, você pode usar o `systemd`, que é o sistema de inicialização e gerenciamento de serviços padrão na maioria das distribuições Linux modernas. Aqui estão os passos detalhados para criar e instalar o seu script Python como um serviço no Linux.

### Passo a Passo:

1. **Crie um Arquivo de Serviço do `systemd`:**
   Crie um arquivo de serviço para o `systemd` na pasta `/etc/systemd/system/`. 
   
   **Nota:** Substitua `/caminho/para/o/` pelo caminho real onde seu script Python está localizado. Certifique-se de que o caminho para o interpretador Python (`/usr/bin/python3`) está correto. Além disso, substitua `seu_usuario` e `seu_grupo` pelo usuário e grupo apropriados.

3. **Recarregue o `systemd` e Habilite o Serviço:**

   Abra um terminal e execute os seguintes comandos:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable player_service.service
   sudo systemctl start player_service.service
   ```

4. **Verifique o Status do Serviço:**

   Para garantir que o serviço está rodando corretamente, você pode verificar o status:

   ```bash
   sudo systemctl status player_service.service
   ```

   Isso deve mostrar a saída indicando que o serviço está ativo e rodando.

5. **Logs e Depuração:**

   Se houver problemas, você pode verificar os logs do serviço usando o `journalctl`:

   ```bash
   sudo journalctl -u player_service.service -f
   ```

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