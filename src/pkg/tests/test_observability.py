import os
import pathlib
import sys

# Ensure 'src' is on sys.path so `import pkg` works when running pytest from project root
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))


def test_init_tracing_from_settings_delegates(monkeypatch):
    called = {}

    def fake_init(app, service_name=None, enabled=None, endpoint=None):
        called["args"] = dict(app=app, service_name=service_name, enabled=enabled, endpoint=endpoint)
        return True

    monkeypatch.setattr("pkg.observability.init_tracing", fake_init)

    # Ensure settings default values are used; do not rely on environment
    try:
        from pkg.shared.config import init_tracing_from_settings

        result = init_tracing_from_settings(app=None, service_name="test-svc")
    finally:
        # clean up any env side-effects in case test runner sets OTEL_*
        os.environ.pop("OTEL_ENABLED", None)
        os.environ.pop("OTEL_EXPORTER_OTLP_ENDPOINT", None)

    assert result is True
    assert called["args"]["service_name"] == "test-svc"
    # endpoint should default to settings.otel_exporter_otlp_endpoint
    assert called["args"]["endpoint"] is not None
