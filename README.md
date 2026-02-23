<div align="center">
  <h1>Fire Detection 🔥</h1>
  
  Real-time fire detection using YOLO and Android smartphone camera streaming.
</div>

---

## Capture Methods Comparison ⚡

This project supports two methods for capturing frames from your Android device:

### 1. ADB Screencap (`adb_capture.py`)
- **FPS**: 0.2 - 0.4 frames per second
- **Method**: Uses `adb exec-out screencap -p` to capture screenshots
- **Pros**: Simple, no additional setup required
- **Cons**: Very slow, subprocess overhead per frame
- **Use Case**: Testing or when virtual webcam setup is not available

### 2. Virtual Webcam via scrcpy (Recommended) 🚀
- **FPS**: 30-40 frames per second (with GPU acceleration)
- **Method**: Uses scrcpy to stream phone screen to v4l2loopback virtual device
- **Pros**: 25-50x faster than ADB capture, real-time detection with GPU
- **Cons**: Requires v4l2loopback kernel module setup
- **Use Case**: Production use, real-time fire detection

> [!IMPORTANT]
> The virtual webcam method with GPU acceleration provides **2-3x better performance** than with just CPU,
> and **25-50x times faster than with ADB capture** making it the only viable option for real-time fire detection.
> See [GPU Setup](#2-install-dependencies-with-gpu-support) for enabling CUDA acceleration.

---

## Installation

### Prerequisites

- **Pixi** (Package manager) - Download from [here](https://pixi.prefix.dev/latest/)
- **scrcpy** - Install via your package manager (`apt install scrcpy`, `pacman -S scrcpy`, etc.)
- **adb** (Android Debug Bridge) - Usually comes with scrcpy, or install via package manager
- **v4l2loopback kernel module** (for virtual webcam)
- **Android device** with USB debugging enabled

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/Ra77a3l3-jar/fireDetection.git
cd fireDetection
```

#### 2. Install Dependencies with GPU Support

Run the automated setup script:
```bash
./setup.sh
```

This script will:
- Install all pixi dependencies
- Uninstall CPU-only PyTorch
- Install PyTorch with CUDA 12.1 support for GPU acceleration
- Verify CUDA is working and show GPU info

**Manual Installation (if setup script fails):**
```bash
# Install pixi dependencies
pixi install

# Remove CPU-only PyTorch and install CUDA version
pixi run pip uninstall torch torchvision -y
pixi run pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install missing dependencies
pixi run pip install ultralytics-thop
```

> [!NOTE]
> GPU acceleration provides 2-3x faster performance compared to CPU-only mode.
> The setup script ensures PyTorch is installed with CUDA support.

#### 3. Setup Virtual Webcam

> [!NOTE]
> You can create the virtual webcam at any `/dev/videoX` number. Common choices are
> `/dev/video10` (if you have an existing webcam at `/dev/video0`) or `/dev/video0` (if you don't have a physical webcam).

Load the v4l2loopback kernel module:
```bash
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1
```

**Parameters explained:**
- `devices=1` - Creates 1 virtual camera device
- `video_nr=10` - Creates device at `/dev/video10` (can be any number, e.g., 0, 2, 10, 20, etc.)
- `card_label="PhoneCam"` - Friendly name for the device
- `exclusive_caps=1` - Required for compatibility with some applications

 ```

#### 4. Connect Your Android Device

1. Enable USB Debugging on your Android device
2. Connect via USB cable
3. Verify connection: `adb devices`

#### 5. Start the Camera Stream

**If using `/dev/video10`:**
```bash
scrcpy --v4l2-sink=/dev/video10 --no-playback
```

**If using `/dev/video0` (or any other video device):**
```bash
scrcpy --v4l2-sink=/dev/video0 --no-playback
```

**Flags explained:**
- `--v4l2-sink=/dev/videoX` - Outputs to specified video device
- `--no-playback` - Runs without opening a display window (headless mode)

---

## Usage 🚀

### Running the Detector

#### 1. Ensure the virtual webcam is running:
```bash
scrcpy --v4l2-sink=/dev/video10 --no-playback
```

#### 2. Update the video device in `src/main.py:19` if needed:
```python
# If using /dev/video10 (default)
cap = cv2.VideoCapture("/dev/video10")

# OR if using /dev/video0 or any other device
cap = cv2.VideoCapture("/dev/video0")
```

#### 3. Run the fire detector:
```bash
pixi run python src/main.py
```

> [!WARNING]
> Make sure to start scrcpy **before** running the detector,
> otherwise OpenCV will fail to open the video device.

### Output

- **Live Video Feed**: Real-time display of your camera stream
- **Detection Boxes**: Bounding boxes drawn around detected fires
- **FPS Counter**: Current frames per second and total detections
- **Fire Alerts**: "FIRE DETECTED" overlay when fire is confirmed
- **Evidence Capture**: Automatic screenshot saving to `evidence/` directory

### Controls

- **ESC**: Exit the application

---

## Configuration ⚙️

### Adjust Detection Sensitivity

In `src/main.py:22`, modify the `confirm_frames` parameter:
```python
# More sensitive (faster alerts, more false positives)
controller = DetectionController(confirm_frames=1)

# Default (balanced)
controller = DetectionController(confirm_frames=3)

# More conservative (slower alerts, fewer false positives)
controller = DetectionController(confirm_frames=5)
```

> [!TIP]
> Start with `confirm_frames=3` and adjust based on your environment.
> Higher values reduce false positives but may delay alerts.

### Change Video Device

In `src/main.py:19`, update the video device path:
```python
cap = cv2.VideoCapture("/dev/video10")  # or /dev/video0, /dev/video2, etc.
```

### Display Window Size

In `src/main.py:25-26`, adjust the window dimensions:
```python
cv2.namedWindow("Fire Detector", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Fire Detector", 900, 600)  # width, height
```

---

## Troubleshooting 🔧

### GPU / CUDA Issues

**Problem**: UI shows `[CPU]` instead of `[GPU]` or slow performance

The default PyTorch from conda-forge is CPU-only. You need to install the CUDA version:

```bash
# Run the setup script
./setup.sh

# Or manually install CUDA PyTorch
pixi run pip uninstall torch torchvision -y
pixi run pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**Verify CUDA is working:**
```bash
pixi run python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

Expected output:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3060 Laptop GPU
```

### Virtual Webcam Issues

**Problem**: `/dev/video10` not found or virtual camera not created

```bash
# Check existing video devices
ls -l /dev/video*

# Check if v4l2loopback is loaded
lsmod | grep v4l2loopback

# If not loaded, load it
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1

# Verify the device was created
ls -l /dev/video*
```

**Problem**: Virtual camera device already exists but not working

```bash
# Unload and reload the module
sudo rmmod v4l2loopback
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1

# Check if any process is using the device
sudo fuser /dev/video10

# Add your user to the video group (if permission issues)
sudo usermod -aG video $USER
# Log out and log back in for this to take effect
```

**Problem**: v4l2loopback module not available (Fedora/RHEL)

On Fedora 43 and similar distributions, you need RPM Fusion repositories:

```bash
# Install RPM Fusion repository
sudo dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm

# Install v4l2loopback
sudo dnf install v4l2loopback akmod-v4l2loopback

# Build kernel modules
sudo akmods --force

# Update module dependencies
sudo depmod -a

# Log out and log back
sudo reboot

# Load the module
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1
```

**Problem**: Module loads but camera still not working

```bash
# Check kernel logs for errors
dmesg | grep v4l2loopback

# Try different video device number (e.g., video0, video2, video20)
sudo rmmod v4l2loopback
sudo modprobe v4l2loopback devices=1 video_nr=0 card_label="PhoneCam" exclusive_caps=1

# Update main.py to match the new device number
# Edit line 19: cap = cv2.VideoCapture("/dev/video0")
```

**Problem**: scrcpy connection fails
```bash
# Check ADB connection
adb devices

# Restart ADB server
adb kill-server
adb start-server
```

### Performance Issues

**Expected Performance:**
- **CPU-only**: 10-20 FPS
- **GPU (CUDA)**: 30-40 FPS

**Problem**: Low FPS even with GPU

Ensure you're using the virtual webcam method (`scrcpy`), not `adb_capture.py`.

**Problem**: scrcpy lag or low FPS

Try reducing the phone's screen resolution or bitrate:
```bash
scrcpy --v4l2-sink=/dev/video10 --no-playback --max-size=1024 --bit-rate=2M
```

---

## Project Structure 📂

```
fireDetection/
├── src/
│   ├── main.py                      # Entry point and main loop
│   ├── capture/
│   │   └── adb_capture.py          # ADB screencap capture (slow method)
│   ├── detection/
│   │   └── yolo_detector.py        # YOLO fire detection logic
│   ├── logic/
│   │   └── controller.py           # Detection confirmation controller
│   ├── ui/
│   │   └── render.py               # Rendering and visualization
│   └── utils/
│       └── evidence_saver.py       # Screenshot saving utility
├── evidence/                        # Auto-generated fire detection screenshots
├── pixi.toml                        # Pixi dependencies
└── README.md
```

---

## License 📄

MIT License - Copyright (c) 2026 Raffaele Meo

See [LICENSE](LICENSE) for full details.
