from unittest.mock import patch

import numpy as np
import pytest

from audio_delay_assistant.cli import find_device_id, make_click


def test_make_click_returns_float32_signal():
    click = make_click(sample_rate=48_000)

    assert isinstance(click, np.ndarray)
    assert click.dtype == np.float32
    assert len(click) == 384  # 8 ms at 48 kHz
    assert np.max(np.abs(click)) <= 0.8


def test_make_click_respects_duration():
    click = make_click(sample_rate=48_000, duration_ms=10.0)

    assert len(click) == 480


def test_find_device_id_finds_wasapi_input_by_name():
    devices = [
        {
            "name": "Microphone Array",
            "hostapi": 0,
            "max_input_channels": 2,
            "max_output_channels": 0,
            "default_samplerate": 48_000,
        },
        {
            "name": "Bluetooth Speaker",
            "hostapi": 0,
            "max_input_channels": 0,
            "max_output_channels": 2,
            "default_samplerate": 48_000,
        },
    ]

    with patch("audio_delay_assistant.cli.sd.query_devices", return_value=devices), patch(
        "audio_delay_assistant.cli.sd.query_hostapis",
        return_value={"name": "Windows WASAPI"},
    ):
        device_id = find_device_id(
            name_contains="microphone",
            kind="input",
            api_contains="WASAPI",
        )

    assert device_id == 0


def test_find_device_id_finds_wasapi_output_by_name():
    devices = [
        {
            "name": "Microphone Array",
            "hostapi": 0,
            "max_input_channels": 2,
            "max_output_channels": 0,
            "default_samplerate": 48_000,
        },
        {
            "name": "Bluetooth Speaker",
            "hostapi": 0,
            "max_input_channels": 0,
            "max_output_channels": 2,
            "default_samplerate": 48_000,
        },
    ]

    with patch("audio_delay_assistant.cli.sd.query_devices", return_value=devices), patch(
        "audio_delay_assistant.cli.sd.query_hostapis",
        return_value={"name": "Windows WASAPI"},
    ):
        device_id = find_device_id(
            name_contains="speaker",
            kind="output",
            api_contains="WASAPI",
        )

    assert device_id == 1


def test_find_device_id_ignores_non_matching_api():
    devices = [
        {
            "name": "Microphone Array",
            "hostapi": 0,
            "max_input_channels": 2,
            "max_output_channels": 0,
            "default_samplerate": 48_000,
        }
    ]

    with patch("audio_delay_assistant.cli.sd.query_devices", return_value=devices), patch(
        "audio_delay_assistant.cli.sd.query_hostapis",
        return_value={"name": "MME"},
    ):
        device_id = find_device_id(
            name_contains="microphone",
            kind="input",
            api_contains="WASAPI",
        )

    assert device_id is None


def test_find_device_id_returns_none_for_missing_device():
    devices = [
        {
            "name": "Bluetooth Speaker",
            "hostapi": 0,
            "max_input_channels": 0,
            "max_output_channels": 2,
            "default_samplerate": 48_000,
        }
    ]

    with patch("audio_delay_assistant.cli.sd.query_devices", return_value=devices), patch(
        "audio_delay_assistant.cli.sd.query_hostapis",
        return_value={"name": "Windows WASAPI"},
    ):
        device_id = find_device_id(
            name_contains="microphone",
            kind="input",
            api_contains="WASAPI",
        )

    assert device_id is None


def test_find_device_id_without_name_returns_first_matching_device():
    devices = [
        {
            "name": "First Input",
            "hostapi": 0,
            "max_input_channels": 1,
            "max_output_channels": 0,
            "default_samplerate": 48_000,
        },
        {
            "name": "Second Input",
            "hostapi": 0,
            "max_input_channels": 2,
            "max_output_channels": 0,
            "default_samplerate": 48_000,
        },
    ]

    with patch("audio_delay_assistant.cli.sd.query_devices", return_value=devices), patch(
        "audio_delay_assistant.cli.sd.query_hostapis",
        return_value={"name": "Windows WASAPI"},
    ):
        device_id = find_device_id(kind="input", api_contains="WASAPI")

    assert device_id == 0