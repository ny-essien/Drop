import logging
import structlog
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from typing import Dict, Any
import json
import time
from prometheus_client import Counter, Histogram, start_http_server
from functools import wraps
from typing import Callable
import boto3
from botocore.exceptions import ClientError
from app.config import settings

# Configure structured logging
def configure_logging():
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Configure standard logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                "logs/app.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )

    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )

class MetricsCollector:
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "api_calls": 0,
            "errors": 0,
            "response_times": [],
            "active_users": 0,
            "memory_usage": 0,
            "cpu_usage": 0
        }

    def increment_api_calls(self):
        self.metrics["api_calls"] += 1

    def increment_errors(self):
        self.metrics["errors"] += 1

    def record_response_time(self, response_time: float):
        self.metrics["response_times"].append(response_time)
        # Keep only last 1000 response times
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]

    def update_active_users(self, count: int):
        self.metrics["active_users"] = count

    def update_system_metrics(self, memory_usage: float, cpu_usage: float):
        self.metrics["memory_usage"] = memory_usage
        self.metrics["cpu_usage"] = cpu_usage

    def get_metrics(self) -> Dict[str, Any]:
        return {
            **self.metrics,
            "average_response_time": sum(self.metrics["response_times"]) / len(self.metrics["response_times"]) if self.metrics["response_times"] else 0,
            "timestamp": datetime.utcnow().isoformat()
        }

    def save_metrics(self):
        """Save metrics to a file for historical analysis"""
        os.makedirs("metrics", exist_ok=True)
        filename = f"metrics/metrics_{datetime.utcnow().strftime('%Y%m%d')}.json"
        
        # Load existing metrics if file exists
        existing_metrics = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                existing_metrics = json.load(f)
        
        # Add new metrics
        existing_metrics.append(self.get_metrics())
        
        # Save updated metrics
        with open(filename, 'w') as f:
            json.dump(existing_metrics, f, indent=2)

# Initialize global metrics collector
metrics_collector = MetricsCollector()

# Initialize logger
logger = structlog.get_logger()

def log_api_call(method: str, path: str, status_code: int, response_time: float):
    """Log API call details"""
    metrics_collector.increment_api_calls()
    metrics_collector.record_response_time(response_time)
    
    logger.info(
        "api_call",
        method=method,
        path=path,
        status_code=status_code,
        response_time=response_time
    )

def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log error details"""
    metrics_collector.increment_errors()
    
    logger.error(
        "error",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {}
    )

def log_system_metrics(memory_usage: float, cpu_usage: float):
    """Log system metrics"""
    metrics_collector.update_system_metrics(memory_usage, cpu_usage)
    
    logger.info(
        "system_metrics",
        memory_usage=memory_usage,
        cpu_usage=cpu_usage
    )

def log_user_activity(user_id: str, action: str, details: Dict[str, Any] = None):
    """Log user activity"""
    logger.info(
        "user_activity",
        user_id=user_id,
        action=action,
        details=details or {}
    )

# Prometheus metrics
REQUEST_COUNT = Counter(
    'request_count',
    'Number of requests received',
    ['endpoint', 'method', 'status']
)

REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)

ML_PREDICTION_COUNT = Counter(
    'ml_prediction_count',
    'Number of ML predictions made',
    ['model_type', 'status']
)

def start_metrics_server():
    """Start Prometheus metrics server"""
    start_http_server(8000)
    logger.info("Metrics server started on port 8000")

def monitor_endpoint(endpoint: str) -> Callable:
    """Decorator to monitor endpoint performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"Error in {endpoint}: {str(e)}")
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_COUNT.labels(
                    endpoint=endpoint,
                    method=func.__name__,
                    status=status
                ).inc()
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
        return wrapper
    return decorator

def monitor_ml_prediction(model_type: str) -> Callable:
    """Decorator to monitor ML predictions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            status = "success"
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                logger.error(f"Error in ML prediction ({model_type}): {str(e)}")
                raise
            finally:
                ML_PREDICTION_COUNT.labels(
                    model_type=model_type,
                    status=status
                ).inc()
        return wrapper
    return decorator

class BackupManager:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.backup_bucket = settings.BACKUP_BUCKET

    async def create_backup(self, collection_name: str, data: list):
        """Create a backup of a collection in S3"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_key = f"backups/{collection_name}/{timestamp}.json"
            
            self.s3_client.put_object(
                Bucket=self.backup_bucket,
                Key=backup_key,
                Body=str(data)
            )
            
            logger.info(f"Backup created for {collection_name}: {backup_key}")
            return True
        except ClientError as e:
            logger.error(f"Error creating backup for {collection_name}: {str(e)}")
            return False

    async def restore_backup(self, collection_name: str, timestamp: str):
        """Restore a backup from S3"""
        try:
            backup_key = f"backups/{collection_name}/{timestamp}.json"
            
            response = self.s3_client.get_object(
                Bucket=self.backup_bucket,
                Key=backup_key
            )
            
            data = response['Body'].read().decode('utf-8')
            logger.info(f"Backup restored for {collection_name}: {backup_key}")
            return eval(data)  # Convert string back to list
        except ClientError as e:
            logger.error(f"Error restoring backup for {collection_name}: {str(e)}")
            return None

    async def list_backups(self, collection_name: str):
        """List available backups for a collection"""
        try:
            prefix = f"backups/{collection_name}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.backup_bucket,
                Prefix=prefix
            )
            
            backups = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    backup_time = obj['Key'].split('/')[-1].replace('.json', '')
                    backups.append({
                        'timestamp': backup_time,
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
            
            return backups
        except ClientError as e:
            logger.error(f"Error listing backups for {collection_name}: {str(e)}")
            return [] 