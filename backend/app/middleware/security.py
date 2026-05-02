"""
KAILASH Security Middleware
Production-grade security for Kailash
Domain: kailash-ai.in
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import logging
import hashlib
import re

logger = logging.getLogger("kailash.security")


class SecurityMiddleware:
    """
    Production security middleware for KAILASH
    - Rate limiting:  req/min per IP
    - ailed login tracking:  attempts =  min lockout
    - Device fingerprinting
    - Input sanitization
    - Security headers
    """
    
    def __init__(self):
        # Rate limiting storage with TTL cleanup
        self.rate_limit_storage: Dict[str, List[float]] = defaultdict(list)
        self.max_requests_per_minute = 60  # 60 requests per minute
        self.max_requests_per_hour = 1000  # 1000 requests per hour
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # Cleanup every 5 minutes
        
        # Failed login tracking
        self.failed_logins: Dict[str, List[Dict]] = defaultdict(list)
        self.max_failed_attempts = 5  # 5 failed attempts before lockout
        self.lockout_duration = timedelta(minutes=30)
        
        # locked IPs and devices
        self.blocked_ips: Dict[str, datetime] = {}
        self.blocked_devices: Dict[str, datetime] = {}
        
        # Admin contacts
        self.admin_emails = ["Connect@go4garage.in", "cto@go4garage.in"]
        self.emergency_contact = "89389"
        
        # Dangerous patterns for input sanitization
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe',
            r'eval\(',
            r'document\.cookie',
            r'\$\(.*\)',
            r'DROP\s+TABLE',
            r'SELECT.*FROM',
            r'INSERT\s+INTO',
            r'DELETE.*FROM',
            r'UPDATE.*SET',
        ]
    
    def get_device_fingerprint(self, request: Request) -> str:
        """Create device fingerprint from request headers"""
        fingerprint_data = [
            request.client.host if request.client else "unknown",
            request.headers.get("user-agent", ""),
            request.headers.get("accept-language", ""),
            request.headers.get("accept-encoding", ""),
        ]
        fingerprint_string = "|".join(fingerprint_data)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:16]
    
    def _cleanup_old_data(self, current_time: float):
        """Periodic cleanup of old rate limit data to prevent memory leaks"""
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        # Clean rate limit storage
        for ip in list(self.rate_limit_storage.keys()):
            self.rate_limit_storage[ip] = [
                req_time for req_time in self.rate_limit_storage[ip]
                if current_time - req_time < 3600
            ]
            if not self.rate_limit_storage[ip]:
                del self.rate_limit_storage[ip]
        
        # Clean expired blocks
        current_dt = datetime.now()
        self.blocked_ips = {ip: exp for ip, exp in self.blocked_ips.items() if exp > current_dt}
        self.blocked_devices = {dev: exp for dev, exp in self.blocked_devices.items() if exp > current_dt}
        
        self.last_cleanup = current_time
        logger.debug(f"Cleaned up security middleware data. Active IPs: {len(self.rate_limit_storage)}")
    
    async def rate_limit_check(self, request: Request):
        """Rate limiting: 60 requests/minute per IP with memory optimization"""
        if not request.client:
            return
        
        client_ip = request.client.host
        current_time = time.time()
        
        # Periodic cleanup to prevent memory leaks
        self._cleanup_old_data(current_time)
        
        # Clean old requests for this IP only (> 1 hour)
        self.rate_limit_storage[client_ip] = [
            req_time for req_time in self.rate_limit_storage[client_ip]
            if current_time - req_time < 3600
        ]
        
        # Check last minute
        recent_requests = [
            req_time for req_time in self.rate_limit_storage[client_ip]
            if current_time - req_time < 60
        ]
        
        if len(recent_requests) >= self.max_requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.max_requests_per_minute} requests per minute."
            )
        
        # Check hourly limit
        if len(self.rate_limit_storage[client_ip]) >= self.max_requests_per_hour:
            logger.warning(f"Hourly rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Hourly rate limit exceeded. Maximum {self.max_requests_per_hour} requests per hour."
            )
        
        # Record this request
        self.rate_limit_storage[client_ip].append(current_time)
    
    async def check_device_lockout(self, kailash_code: str, request: Request) -> bool:
        """Check if device/IP is locked after failed login attempts"""
        if not request.client:
            return True
        
        client_ip = request.client.host
        device_fingerprint = self.get_device_fingerprint(request)
        lockout_key = f"{kailash_code}:{device_fingerprint}"
        current_time = datetime.now()
        
        # Check IP block
        if client_ip in self.blocked_ips:
            if current_time < self.blocked_ips[client_ip]:
                remaining = (self.blocked_ips[client_ip] - current_time).total_seconds() / 60
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"IP blocked for {remaining:.0f} more minutes. Emergency: {self.emergency_contact}"
                )
            else:
                del self.blocked_ips[client_ip]
        
        # Check device block
        if lockout_key in self.blocked_devices:
            if current_time < self.blocked_devices[lockout_key]:
                remaining = (self.blocked_devices[lockout_key] - current_time).total_seconds() / 60
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Device blocked for {remaining:.0f} minutes after {self.max_failed_attempts} failed attempts. Emergency: {self.emergency_contact}"
                )
            else:
                del self.blocked_devices[lockout_key]
        
        # Clean old failed attempts
        self.failed_logins[lockout_key] = [
            attempt for attempt in self.failed_logins[lockout_key]
            if current_time - attempt['time'] < self.lockout_duration
        ]
        
        # Check if should lock
        if len(self.failed_logins[lockout_key]) >= self.max_failed_attempts:
            lockout_until = current_time + self.lockout_duration
            self.blocked_ips[client_ip] = lockout_until
            self.blocked_devices[lockout_key] = lockout_until
            
            logger.critical(
                f"Account locked: {kailash_code} from {client_ip} after {self.max_failed_attempts} failed attempts"
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account locked for  minutes after {self.max_failed_attempts} failed attempts. Emergency: {self.emergency_contact}"
            )
        
        return True
    
    def record_failed_login(self, kailash_code: str, request: Request):
        """Record failed login attempt"""
        if not request.client:
            return
        
        device_fingerprint = self.get_device_fingerprint(request)
        lockout_key = f"{kailash_code}:{device_fingerprint}"
        
        self.failed_logins[lockout_key].append({
            'time': datetime.now(),
            'ip': request.client.host,
            'user_agent': request.headers.get("user-agent", "Unknown"),
            'device': device_fingerprint
        })
        
        attempts = len(self.failed_logins[lockout_key])
        logger.warning(
            f"ailed login {attempts}/{self.max_failed_attempts} for {kailash_code} from {request.client.host}"
        )
    
    def clear_failed_logins(self, kailash_code: str, request: Request):
        """Clear failed attempts after successful login"""
        if not request.client:
            return
        
        device_fingerprint = self.get_device_fingerprint(request)
        lockout_key = f"{kailash_code}:{device_fingerprint}"
        
        if lockout_key in self.failed_logins:
            del self.failed_logins[lockout_key]
            logger.info(f"Cleared failed login attempts for {kailash_code}")
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent XSS and injection"""
        if not text:
            return text
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    async def add_security_headers(self, request: Request, call_next):
        """Add comprehensive security headers"""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
    
    def get_security_stats(self) -> Dict:
        """Get current security statistics"""
        return {
            "active_rate_limits": len(self.rate_limit_storage),
            "blocked_ips": len(self.blocked_ips),
            "blocked_devices": len(self.blocked_devices),
            "accounts_with_failed_attempts": len(self.failed_logins),
            "total_failed_attempts": sum(len(attempts) for attempts in self.failed_logins.values())
        }


# Global instance
security_middleware = SecurityMiddleware()
