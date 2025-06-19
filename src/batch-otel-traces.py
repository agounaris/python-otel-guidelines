import logging
import random
import time

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pythonjsonlogger.json import JsonFormatter

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

# Set up the OTLP exporter and span processor
exporter = OTLPSpanExporter(insecure=True)
provider = TracerProvider()
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

class SpanTime:
    def __init__(self, name, attributes={}):
        self.name = name
        self.attributes = attributes or {}
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        with tracer.start_as_current_span(self.name) as span:
            try:
                if random.random() < 0.05:
                    raise Exception('simulated error')
                span.set_attribute('duration', duration_ms)
                span.set_status(trace.Status(trace.StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                logging.error('failed transaction')

if __name__ == "__main__":
    for i in range(50):
        with SpanTime('data-process'):
            time.sleep(random.uniform(100, 2000) / 1000)
    provider.shutdown()
