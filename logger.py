# logger.py
import logging
from opentelemetry import trace
from pythonjsonlogger import jsonlogger


class TraceIdInjectingFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        span = trace.get_current_span()
        ctx  = span.get_span_context()

        if ctx and ctx.is_valid:
            hex_trace  = format(ctx.trace_id, '032x')
            xray_trace = f"1-{hex_trace[:8]}-{hex_trace[8:]}"

            log_record['traceId'] = xray_trace
            log_record['spanId']  = format(ctx.span_id, '016x')
        else:
            log_record['traceId'] = "no-trace"
            log_record['spanId']  = "no-span"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler   = logging.StreamHandler()
        formatter = TraceIdInjectingFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
