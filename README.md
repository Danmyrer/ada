# Audio Delay Assistant

Small CLI tool to roughly measure Bluetooth speaker audio delay using a microphone.

It plays short clicks through an output device and records them through an input device. The detected delay is printed in milliseconds.

## Install

### Quick install

#### Using `pipx`:

```powershell
pipx install git+https://github.com/Danmyrer/ada.git
```

#### Using `uv`:

```powershell
uv tool install git+https://github.com/Danmyrer/ada.git
```

Then run:

```powershell
ada -l
```

Or run once without installing permanently:

```powershell
uvx --from git+https://github.com/Danmyrer/ada.git ada -l
```

### Development install

Clone the repository:

```powershell
git clone https://github.com/Danmyrer/ada.git
cd audio-delay-assistant
```

Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

Install the package in editable mode:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Run the CLI:

```powershell
.\.venv\Scripts\ada.exe -l
```

Or activate the virtual environment first:

```powershell
.\.venv\Scripts\Activate.ps1
ada -l
```

Run tests:

```powershell
pytest
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
