"""
KAILASH Error Handler
Centralized error handling with structured logging
Domain: kailash-ai.in
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import traceback
import os
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory
log_dir = Path("/var/log/kailash") if os.name != "nt" else Path("./logs")
log_dir.mkdir(exist_ok=True, parents=True)

# Configure production logging
logging_file = log_dir / "kailash_production.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-s | %(message)s',
    handlers=[
        logging.FileHandler(logging_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("kailash")


class ErrorHandler:
    """Centralized error handling for KAILASH"""
    
    ADMIN_EMAILS = ["Connect@go4garage.in", "cto@go4garage.in"]
    EMERGENCY_CONTACT = "89389"
    SUPPORT_EMAIL = "cto@go4garage.in"
    
    @staticmethod
    async def handle_exception(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler"""
        error_id = f"{int(datetime.now().timestamp())}"
        
        # Log comprehensive error details
        logger.error(f"""
╔═══════════════════════════════════════════════════════════════╗
║  ERROR OCCURRED                                               ║
╚═══════════════════════════════════════════════════════════════╝
Error ID: {error_id}
Path: {request.url.path}
Method: {request.method}
Client IP: {request.client.host if request.client else 'Unknown'}
User Agent: {request.headers.get('user-agent', 'Unknown')[:]}
Error Type: {type(exc).__name__}
Error Message: {str(exc)}
Traceback:
{traceback.format_exc()}
Timestamp: {datetime.now().isoformat()}
Admin: {', '.join(ErrorHandler.ADMIN_EMAILS)}
Emergency: {ErrorHandler.EMERGENCY_CONTACT}
╚═══════════════════════════════════════════════════════════════╝
        """)
        
        # Return safe error to user
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "error_id": error_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # Generic error for unexpected exceptions
        return JSONResponse(
            status_code=500,
            content={
                "error": "An internal error occurred. Our team has been notified.",
                "error_id": error_id,
                "support": ErrorHandler.SUPPORT_EMAIL,
                "emergency": ErrorHandler.EMERGENCY_CONTACT,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def log_request(request: Request, response_time: float, status_code: int):
        """Log API requests with performance metrics"""
        log_entry = (
            f"{request.method} {request.url.path} | "
            f"Status: {status_code} | "
            f"Time: {response_time:.3f}s | "
            f"IP: {request.client.host if request.client else 'Unknown'}"
        )
        
        if response_time > 1.0:
            logger.warning(f"SLOW REQUEST: {log_entry}")
        else:
            logger.info(log_entry)
    
    @staticmethod
    def log_authentication(kailash_code: str, ip: str, success: bool, device_info: str = ""):
        """Log authentication attempts"""
        status = "SUCCESS" if success else "AILED"
        log_level = logging.INFO if success else logging.WARNING
        
        logger.log(
            log_level,
            f"AUTH {status}: {kailash_code} from {ip} | Device: {device_info}"
        )
    
    @staticmethod
    def log_security_event(event_type: str, details: dict, severity: str = "WARNING"):
        """Log security events"""
        log_level = getattr(logging, severity.upper(), logging.WARNING)
        
        message = f"""
╔═══════════════════════════════════════════════════════════════╗
║  SECURITY EVENT: {event_type}                                ║
╚═══════════════════════════════════════════════════════════════╝
{chr(10).join(f'  {k}: {v}' for k, v in details.items())}
Timestamp: {datetime.now().isoformat()}
Admin: {', '.join(ErrorHandler.ADMIN_EMAILS)}
╚═══════════════════════════════════════════════════════════════╝
        """
        logger.log(log_level, message)


error_handler = ErrorHandler()
