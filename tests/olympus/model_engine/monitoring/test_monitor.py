import pytest
from olympus.model_engine.monitoring.monitor import ModelMonitor

def test_model_monitor_init():
    monitor = ModelMonitor()
    assert isinstance(monitor.inference_count, Counter)
    assert isinstance(monitor.inference_latency, Histogram)
    assert isinstance(monitor.error_count, Counter)
    assert isinstance(monitor.memory_usage, Gauge)
    assert isinstance(monitor.cache_hits, Counter)
    assert isinstance(monitor.cache_misses, Counter)

def test_register_model():
    monitor = ModelMonitor()
    mock_model = mocker.Mock(name="mock_model")
    monitor.register_model(mock_model)
    assert "mock_model" in monitor.memory_usage._metrics

def test_track_inference(mocker):
    monitor = ModelMonitor()
    with monitor.track_inference("test_model"):
        pass
    assert monitor.inference_count.labels(model_name="test_model")._value[0] == 1

def test_track_memory():
    monitor = ModelMonitor()
    monitor.track_memory("test_model", 1024)
    assert monitor.memory_usage.labels(model_name="test_model")._value[0] == 1024

def test_track_cache():
    monitor = ModelMonitor()
    monitor.track_cache("test_model", True)
    assert monitor.cache_hits.labels(model_name="test_model")._value[0] == 1
    monitor.track_cache("test_model", False)
    assert monitor.cache_misses.labels(model_name="test_model")._value[0] == 1