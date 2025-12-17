"""Quick script to verify tracing helper import and init."""
from pkg.observability import init_tracing

if __name__ == "__main__":
    ok = init_tracing(None, service_name="tracing-check")
    print("Tracing enabled:", ok)
