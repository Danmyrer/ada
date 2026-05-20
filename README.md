# Audio Delay Assistant

Small CLI tool to roughly measure Bluetooth speaker audio delay using a microphone.

It plays short clicks through an output device and records them through an input device. The detected delay is printed in milliseconds.

## Install

### Option 1: Install in a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
```

Run it from the virtual environment:

```powershell
.\.venv\Scripts\ada.exe -l
```

Or activate the virtual environment first:

```powershell
.\.venv\Scripts\Activate.ps1
ada -l
```

### Option 2: Install globally

```powershell
python -m pip install .
```

Then run it directly:

```powershell
ada -l
```

## Usage

List WASAPI devices:

```powershell
ada -l
```

List all devices:

```powershell
ada -l -a
```

Measure with explicit devices:

```powershell
ada -i 20 -o 18
```

Change volume:

```powershell
ada -i 20 -o 18 -v 0.7
```

## Notes

This is a rough measurement tool, not a lab-grade latency analyzer.

For Windows, WASAPI devices are shown by default because MME and DirectSound can add extra buffering and distort the result.
