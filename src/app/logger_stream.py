import logging
import asyncio
import json
from asyncio import Queue

# Global queue for log streaming
log_queue = Queue()

class UIStreamHandler(logging.Handler):
    """
    Custom Logging Handler that intercepts logs and pushes them to an async Queue.
    """
    def emit(self, record):
        try:
            # Format the log message
            msg = self.format(record)
            
            # Determine category based on level or keywords
            category = "INFO"
            if record.levelno >= logging.ERROR:
                category = "ERROR"
            elif record.levelno >= logging.WARNING:
                category = "WARNING"
            elif "[SCAN]" in msg:
                category = "SCAN"
            elif "[MATCH]" in msg:
                category = "MATCH"
            elif "[EXTRACT]" in msg:
                category = "EXTRACT"
            
            # Push structured data to the queue
            log_queue.put_nowait({
                "category": category,
                "message": msg
            })
        except Exception:
            self.handleError(record)

def setup_global_logging():
    """Attaches the UI stream handler to the root logger."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Avoid adding duplicate handlers
    for h in root_logger.handlers:
        if isinstance(h, UIStreamHandler):
            return

    ui_handler = UIStreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
    ui_handler.setFormatter(formatter)
    root_logger.addHandler(ui_handler)
