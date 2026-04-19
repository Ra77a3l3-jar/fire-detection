# Dronebot 2026 — Script PC

Script Python per il rilevamento del fuoco e il coordinamento del rover durante la gara.
Gira su PC collegato al drone DJI Neo 1 tramite streaming video.

---

## Come funziona

La gara si svolge in due fasi gestite automaticamente dallo script.

### Fase 1 — Rilevamento del fuoco

Il pilota porta il drone sull'area di fuoco. Lo script usa YOLO per rilevare il fuoco in tempo reale.
Quando la rilevazione e' stabile per `FIRE_CONFIR_FRAMES` frame consecutivi l'incendio viene confermato, viene salvata una foto come prova e viene inviato il **Segnale 1** al rover via WiFi UDP.
Il rover riceve il segnale e inizia a prepararsi per il tracciamento.

### Fase 2 — Coordinamento rover

La fase 2 si divide in due sotto-fasi automatiche.

**Fase 2a — Blocco del cerchio di fuoco**

Il pilota torna nell'area del rover. Il rover inizia a seguire il drone. Il pilota riporta lentamente il drone sopra l'area di fuoco e lo mantiene fermo.
Lo script rileva nuovamente il fuoco e, quando la posizione e' stabile per `FIRE_LOCK_FRAMES` frame consecutivi, blocca il centro e il raggio del cerchio di fuoco come riferimento preciso.
Questo riferimento e' piu' accurato di quello della Fase 1 perche' il drone e' esattamente sopra il fuoco alla quota di verifica.

**Fase 2b — Verifica contenimento**

Lo script verifica che tutti e quattro gli angoli del marker ArUco (montato sul rover) siano all'interno del cerchio di fuoco bloccato.
Il centro del cerchio viene aggiornato frame per frame per compensare il leggero drift del drone in hovering.
Quando la condizione e' soddisfatta per `ROVER_CONFIRM_FRAMES` frame consecutivi, il contenimento viene confermato e viene salvata la foto finale come prova.

---

## Prerequisiti

- **Pixi** — gestore di pacchetti: https://pixi.prefix.dev/latest/
- **scrcpy** — streaming schermo Android: `apt install scrcpy` / `pacman -S scrcpy`
- **adb** — Android Debug Bridge (incluso con scrcpy o installabile via package manager)
- **v4l2loopback** — modulo kernel per la webcam virtuale
- **Dispositivo Android** con debug USB abilitato

---

## Installazione

### Installare le dipendenze con supporto GPU

```bash
pixi install
./setup.sh
```

Lo script installa le dipendenze pixi, rimuove PyTorch CPU-only e installa PyTorch con CUDA 12.1.

**Verifica che CUDA funzioni:**

```bash
pixi run python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

### Creare la webcam virtuale

```bash
sudo ./setup_virtual_camera.sh
```

Oppure manualmente:

```bash
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1
```

Il modulo crea il dispositivo `/dev/video10`. Il numero puo' essere cambiato modificando anche `VIDEO_SOURCE` in `src/config.py`.

**Su Fedora / RHEL (v4l2loopback non disponibile di default):**

```bash
sudo dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install v4l2loopback akmod-v4l2loopback
sudo akmods --force
sudo depmod -a
sudo reboot
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1
```

---

> [!NOTE]
> Per i metodi con RTMP o Wireless entrambi i dispositivi devono essere collegati alla stessa rete

## Connessione con RTMP live streaming

L'applicazione DJI FLY supporta il live streaming del video feed via RTMP, questo permette di usare
un qualsiasi dispositivo Ios o Android.

1. Creare un server RTMP sul proprio dispositivo con ffmpeg
```bash
 ffmpeg -fflags nobuffer -flags low_delay -listen 1 -i rtmp://0.0.0.0:1935/live/drone -f v4l2 /dev/video10
```

2. Nell'app DJI FLY premere GO FLY per connettersi al drone
3. Aprire le impostazioni di *trasmissione* > *live streaming platforms* e selezionare *RTMP*
4. Inserire il live streaming address definito nel comando ffmpeg,cambiando l'indirizzo IP con quello del nostro dispositivo

```bash
ip a | grep "inet " | grep -v 127
```
L'output dara una stringa come : inet 172.20.10.5/28 brd 172.20.10.15 scope global dynamic noprefixroute wlp4s0
Il primo indirizzo ip andra` sostituito quando l'indirizzo rtmp verra inserito nell'app DJI

5. Selezionare la risoluzione e bitrate piu adatti
6. Iniziare la live

## Connessione del dispositivo Android

### Connessione via cavo USB (consigliata per la configurazione iniziale)

1. Abilitare il debug USB sul dispositivo Android: Impostazioni > Opzioni sviluppatore > Debug USB
2. Collegare il cavo USB al PC
3. Verificare la connessione:

```bash
adb devices
```

L'output deve mostrare il dispositivo con stato `device`. Se compare `unauthorized`, sbloccare il telefono e accettare il dialogo di autorizzazione.

4. Avviare lo streaming:

```bash
scrcpy --v4l2-sink=/dev/video10 --no-playback
```

### Connessione wireless (necessaria durante la gara)

La connessione wireless e' necessaria perche' durante la gara il drone deve muoversi liberamente senza cavo.

**Metodo 1 — ADB over TCP/IP (Android standard):**

Con il cavo USB ancora collegato, eseguire:

```bash
adb tcpip 5555
```

Trovare l'indirizzo IP del telefono: Impostazioni > WiFi > (nome rete) > Indirizzo IP.

Disconnettere il cavo USB, poi:

```bash
adb connect <IP_TELEFONO>:5555
adb devices
scrcpy --v4l2-sink=/dev/video10 --no-playback
```

Se la connessione si perde, ricollegare con:

```bash
adb connect <IP_TELEFONO>:5555
```

**Metodo 2 — Debug wireless nativo (Android 11+):**

Su Android 11 o superiore e' disponibile il debug wireless nativo.

Abilitare: Impostazioni > Opzioni sviluppatore > Debug wireless.

Abbinamento tramite codice di coppia:

```bash
adb pair <IP_TELEFONO>:<PORTA_ABBINAMENTO>
```

Poi connettersi alla porta di debug wireless mostrata nell'interfaccia:

```bash
adb connect <IP_TELEFONO>:<PORTA_DEBUG>
adb devices
scrcpy --v4l2-sink=/dev/video10 --no-playback
```

**Opzioni scrcpy utili per la connessione wireless:**

```bash
# Ridurre la risoluzione per migliorare la stabilita' su WiFi lento
scrcpy --v4l2-sink=/dev/video10 --no-playback --max-size=1024

# Ridurre il bitrate
scrcpy --v4l2-sink=/dev/video10 --no-playback --video-bit-rate=2M

# Entrambe
scrcpy --v4l2-sink=/dev/video10 --no-playback --max-size=1024 --video-bit-rate=2M
```

---

## Configurazione

Tutti i parametri si trovano in `src/config.py`.

```python
VIDEO_SOURCE = "/dev/video10"       # dispositivo webcam virtuale

# Fase 1
YOLO_CONFIDENCE = 0.70             # soglia di confidenza YOLO (0.0 - 1.0)
FIRE_CONFIR_FRAMES = 7             # frame consecutivi per confermare il fuoco
MIN_FIRE_AREA = 5000               # area minima in pixel del fuoco rilevato
MAX_FIRE_SHIFT = 100               # spostamento massimo centro fuoco tra frame

# Fase 2
FIRE_LOCK_FRAMES = 20              # frame stabili per bloccare il cerchio di fuoco
ROVER_CONFIRM_FRAMES = 5           # frame consecutivi per confermare il contenimento
MAX_ROVER_SHIFT = 15               # tolleranza in pixel aggiunta al raggio del cerchio

```

---

## Utilizzo

### 1. Assicurarsi che la webcam virtuale sia attiva

```bash
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1
```

### 2. Connettere il telefono e avviare lo streaming

```bash
# Via cavo
scrcpy --v4l2-sink=/dev/video10 --no-playback

# Via WiFi (dopo aver configurato adb wireless)
adb connect <IP_TELEFONO>:5555
scrcpy --v4l2-sink=/dev/video10 --no-playback
```

### 3. Avviare lo script

```bash
cd dronebot-2026/pc
pixi run python src/main.py
```

Lo script deve essere avviato **dopo** scrcpy, altrimenti OpenCV non trovera' il dispositivo video.

### Controlli

- `ESC` o `Q` — chiude l'applicazione

### Output

- Feed video in tempo reale con i box di rilevamento
- Pannello informativo in alto con fase corrente, streak e FPS
- Cerchio di fuoco sovrapposto durante la Fase 2
- Box del rover colorato in verde (contenuto) o rosso (non contenuto)
- Foto salvate automaticamente nella cartella `evidence/` alla conferma del fuoco e al completamento della gara

---

## Generazione marker ArUco

Per generare il marker ArUco da stampare e montare sul rover:

```bash
pixi run python src/aruco_generator.py
```

Il marker viene salvato come `aruco_marker.png`. Verificare che il dizionario e l'ID corrispondano a quelli in `config.py` (`ARUCO_DICTIONARY_NAME`, `ARUCO_ID`).

---

## Risoluzione problemi

### CUDA non disponibile (interfaccia mostra CPU)

```bash
pixi run pip uninstall torch torchvision -y
pixi run pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### `/dev/video10` non trovato

```bash
# Verificare i dispositivi video presenti
ls -l /dev/video*

# Verificare se il modulo e' caricato
lsmod | grep v4l2loopback

# Ricaricare il modulo
sudo rmmod v4l2loopback
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1
```

### Il dispositivo esiste ma non funziona

```bash
# Verificare se un processo occupa gia' il dispositivo
sudo fuser /dev/video10

# Aggiungere il proprio utente al gruppo video (se problemi di permessi)
sudo usermod -aG video $USER
# Effettuare logout e login per applicare la modifica
```

### adb non trova il dispositivo

```bash
adb kill-server
adb start-server
adb devices
```

### Connessione wireless instabile

Assicurarsi che PC e telefono siano sulla stessa rete WiFi. Usare `--max-size=1024 --video-bit-rate=2M` con scrcpy per ridurre il carico di rete. Se la connessione si interrompe durante la gara, riconnettersi con `adb connect <IP>:5555` e riavviare scrcpy.

---

## Licenza

MIT License - Copyright (c) 2026 Raffaele Meo
