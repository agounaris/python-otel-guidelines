import logging
import random
import time

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import \
    OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from pythonjsonlogger.json import JsonFormatter

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

# Set up the OTLP exporter and metric reader
exporter = OTLPMetricExporter(insecure=True)
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

# Create meter and instruments
meter = metrics.get_meter(__name__)
duration_histogram = meter.create_histogram(
    name="duration",
    unit="ms",
    description="Duration of process"
)
error_counter = meter.create_counter(
    name="error_count",
    unit="1",
    description="Number of errors"
)

class HistrogramTimer:
    def __init__(self, duration_histogram, error_counter,  attributes={}):
        self.duration_histogram = duration_histogram
        self.error_counter = error_counter
        self.attributes = attributes or {}
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        try:
            if random.random() < 0.05:
                raise Exception('simulated error')
        except Exception as e:
            self.error_counter.add(1, self.attributes)
            logging.error('transaction failed')
        duration_histogram.record(duration_ms, self.attributes)
        
if __name__ == "__main__":
    for i in range(50):
        with HistrogramTimer(duration_histogram, error_counter, {'op': 'data-process'}):
            time.sleep(random.uniform(100, 2000) / 1000)
    # Flush any remaining metrics before exit
    provider.shutdown()
