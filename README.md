# Audio Delay Assistant

Small CLI tool to roughly measure Bluetooth speaker audio delay using a microphone.

It plays short clicks through an output device and records them through an input device. The detected delay is printed in milliseconds.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
```

## Usage

List WASAPI devices:

```powershell
audio-delay -l
```

List all devices:

```powershell
audio-delay -l -a
```

Measure with explicit devices:

```powershell
audio-delay -i 20 -o 18
```

Change volume:

```powershell
audio-delay -i 20 -o 18 -v 0.7
```

## Notes

This is a rough measurement tool, not a lab-grade latency analyzer.

For Windows, WASAPI devices are shown by default because MME and DirectSound can add extra buffering and distort the result.