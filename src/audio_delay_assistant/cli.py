import argparse
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt


def list_devices(show_all=False):
    devices = sd.query_devices()

    inputs = []
    outputs = []

    for i, d in enumerate(devices):
        hostapi = sd.query_hostapis(d["hostapi"])["name"]

        # Default: show only WASAPI devices
        # With --all: show every available audio API
        if not show_all and "WASAPI" not in hostapi:
            continue

        row = {
            "id": i,
            "api": hostapi,
            "name": d["name"],
            "inputs": d["max_input_channels"],
            "outputs": d["max_output_channels"],
            "samplerate": int(d["default_samplerate"]),
        }

        if row["inputs"] > 0:
            inputs.append(row)

        if row["outputs"] > 0:
            outputs.append(row)

    def print_table(title, rows, direction):
        print()
        print(title)
        print("-" * 100)
        print(f"{'ID':>3} | {'API':<22} | {'CH':<7} | {'SR':<7} | NAME")
        print("-" * 100)

        for r in rows:
            ch = f"{r['inputs']} in" if direction == "in" else f"{r['outputs']} out"
            print(
                f"{r['id']:>3} | "
                f"{r['api']:<22} | "
                f"{ch:<7} | "
                f"{r['samplerate']:<7} | "
                f"{r['name']}"
            )

    if show_all:
        print("All audio devices:")
    else:
        print("Audio devices: WASAPI only")
        print("Use --all to also show MME, DirectSound, and WDM-KS devices.")

    print_table("INPUT DEVICES", inputs, "in")
    print_table("OUTPUT DEVICES", outputs, "out")
    print()


def find_device_id(name_contains=None, kind="output", api_contains="WASAPI"):
    devices = sd.query_devices()

    for i, d in enumerate(devices):
        hostapi = sd.query_hostapis(d["hostapi"])["name"]

        if api_contains and api_contains.lower() not in hostapi.lower():
            continue

        if kind == "input" and d["max_input_channels"] <= 0:
            continue

        if kind == "output" and d["max_output_channels"] <= 0:
            continue

        if name_contains and name_contains.lower() not in d["name"].lower():
            continue

        return i

    return None


def make_click(sample_rate: int, duration_ms: float = 8.0, freq: float = 2000.0):
    n = int(sample_rate * duration_ms / 1000)
    t = np.arange(n) / sample_rate

    # Short sine burst with a window, easier to detect than a single impulse
    click = np.sin(2 * np.pi * freq * t)
    click *= np.hanning(n)
    click *= 0.8

    return click.astype(np.float32)


def measure_delay(
    sample_rate=48000,
    channels=1,
    output_device=None,
    input_device=None,
    volume=0.8,
    pre_silence=0.5,
    click_spacing=0.7,
    clicks=5,
    record_extra=1.0,
):
    click = make_click(sample_rate)

    total_duration = pre_silence + click_spacing * clicks + record_extra
    n_total = int(total_duration * sample_rate)

    playback = np.zeros(n_total, dtype=np.float32)
    expected_times = []

    for i in range(clicks):
        t_click = pre_silence + i * click_spacing
        start = int(t_click * sample_rate)

        playback[start:start + len(click)] += click * volume
        expected_times.append(t_click)

    print("Starting measurement...")
    print("The Bluetooth speaker should play the clicks.")
    print("The laptop microphone should record them.")
    print()

    recording = sd.playrec(
        playback,
        samplerate=sample_rate,
        channels=channels,
        dtype="float32",
        device=(input_device, output_device),
        blocking=True,
    )

    recording = recording[:, 0]

    # Normalize recording around zero
    rec = recording - np.mean(recording)
    rec_abs = np.abs(rec)

    detected_times = []
    delays = []

    for expected in expected_times:
        # Search in a reasonable window after the expected click.
        # Bluetooth latency is often roughly between 50 ms and 300 ms,
        # but this allows up to 800 ms.
        search_start = int((expected + 0.02) * sample_rate)
        search_end = int((expected + 0.80) * sample_rate)

        segment = rec_abs[search_start:search_end]

        if len(segment) == 0:
            continue

        peak_index = np.argmax(segment)
        detected_sample = search_start + peak_index
        detected_time = detected_sample / sample_rate

        delay = detected_time - expected

        detected_times.append(detected_time)
        delays.append(delay)

    delays_ms = np.array(delays) * 1000

    print("Individual measurements:")
    for i, delay in enumerate(delays_ms, start=1):
        print(f"  Click {i}: {delay:.1f} ms")

    if len(delays_ms) > 0:
        print()
        print(f"Median delay: {np.median(delays_ms):.1f} ms")
        print(f"Mean delay:   {np.mean(delays_ms):.1f} ms")
        print()
        print("You can use this value as a rough audio offset.")
        print("For video sync, this usually means the audio is late by this amount.")
    else:
        print("No click detected. Increase microphone gain or speaker volume.")

    # Plot
    times = np.arange(len(recording)) / sample_rate

    plt.figure(figsize=(12, 5))
    plt.plot(times, recording, label="Microphone recording")

    for expected in expected_times:
        plt.axvline(
            expected,
            linestyle="--",
            alpha=0.5,
            label="sent click" if expected == expected_times[0] else None,
        )

    for detected in detected_times:
        plt.axvline(
            detected,
            linestyle=":",
            alpha=0.8,
            label="detected click" if detected == detected_times[0] else None,
        )

    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.title("Bluetooth Audio Delay Measurement")
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Measure rough Bluetooth speaker audio delay using a microphone."
    )

    parser.add_argument(
        "-l",
        "--list-devices",
        action="store_true",
        help="List available audio devices.",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Show all audio APIs, not only WASAPI.",
    )
    parser.add_argument(
        "-i",
        "--input-device",
        type=int,
        default=None,
        help="Input device ID, usually your laptop microphone.",
    )
    parser.add_argument(
        "-o",
        "--output-device",
        type=int,
        default=None,
        help="Output device ID, usually your Bluetooth speaker.",
    )
    parser.add_argument(
        "-s",
        "--samplerate",
        type=int,
        default=48000,
        help="Sample rate in Hz.",
    )
    parser.add_argument(
        "-v",
        "--volume",
        type=float,
        default=0.8,
        help="Click playback volume from 0.0 to 1.0.",
    )

    args = parser.parse_args()

    if args.list_devices:
        list_devices(show_all=args.all)
        return

    input_device = args.input_device
    output_device = args.output_device

    if input_device is None:
        input_device = find_device_id(kind="input", api_contains="WASAPI")

    if output_device is None:
        output_device = find_device_id(kind="output", api_contains="WASAPI")

    if input_device is None:
        raise RuntimeError(
            "No WASAPI input device found. Use --list-devices --all and select one manually."
        )

    if output_device is None:
        raise RuntimeError(
            "No WASAPI output device found. Use --list-devices --all and select one manually."
        )

    print(f"Input device:  {input_device} - {sd.query_devices(input_device)['name']}")
    print(f"Output device: {output_device} - {sd.query_devices(output_device)['name']}")
    print()

    measure_delay(
        sample_rate=args.samplerate,
        input_device=input_device,
        output_device=output_device,
        volume=args.volume,
    )


if __name__ == "__main__":
    main()