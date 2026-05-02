"""
KAILASH Enhanced Security Module
Additional security features for production deployment
Domain: kailash-ai.in
"""
import hashlib
import secrets
import re
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
import ipaddress
from urllib.parse import urlparse

logger = logging.getLogger("kailash.security")

class SecurityEnhancer:
    """Enhanced security features for KAILASH production"""
    
    def __init__(self):
        # IP whitelist for admin functions
        self.admin_ip_whitelist: Set[str] = {
            "127.0.0.1",
            "::1",
            "localhost"
        }
        
        # Suspicious activity tracking
        self.suspicious_activities: Dict[str, List[Dict]] = {}
        self.blocked_user_agents: Set[str] = {
            "sqlmap",
            "nikto",
            "nmap",
            "masscan",
            "gobuster",
            "dirb",
            "dirbuster"
        }
        
        # Content Security Policy
        self.csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.anthropic.com https://api.openai.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        
        # Password policy
        self.password_policy = {
            'min_length': 8,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_special': True,
            'max_age_days': 90,
            'history_count': 5
        }
    
    def validate_password_strength(self, password: str) -> Dict[str, any]:
        """Validate password against security policy"""
        issues = []
        score = 0
        
        if len(password) < self.password_policy['min_length']:
            issues.append(f"Password must be at least {self.password_policy['min_length']} characters")
        else:
            score += 1
        
        if self.password_policy['require_uppercase'] and not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")
        else:
            score += 1
        
        if self.password_policy['require_lowercase'] and not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")
        else:
            score += 1
        
        if self.password_policy['require_numbers'] and not re.search(r'[0-9]', password):
            issues.append("Password must contain at least one number")
        else:
            score += 1
        
        if self.password_policy['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain at least one special character")
        else:
            score += 1
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):  # Repeated characters
            issues.append("Password should not contain repeated characters")
            score -= 1
        
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            issues.append("Password should not contain sequential numbers")
            score -= 1
        
        strength = "Very Weak"
        if score >= 4:
            strength = "Strong"
        elif score >= 3:
            strength = "Medium"
        elif score >= 2:
            strength = "Weak"
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'strength': strength,
            'score': max(0, score)
        }
    
    def detect_suspicious_activity(self, request: Request) -> bool:
        """Detect suspicious request patterns"""
        if not request.client:
            return False
        
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "").lower()
        path = request.url.path.lower()
        
        # Check for blocked user agents
        for blocked_agent in self.blocked_user_agents:
            if blocked_agent in user_agent:
                self._log_suspicious_activity(client_ip, "blocked_user_agent", {
                    "user_agent": user_agent,
                    "path": path
                })
                return True
        
        # Check for SQL injection patterns
        sql_patterns = [
            r"union\s+select",
            r"or\s+1\s*=\s*1",
            r"drop\s+table",
            r"insert\s+into",
            r"delete\s+from",
            r"update\s+.*set",
            r"exec\s*\(",
            r"script\s*>",
            r"javascript:",
            r"vbscript:"
        ]
        
        query_string = str(request.query_params).lower()
        for pattern in sql_patterns:
            if re.search(pattern, query_string) or re.search(pattern, path):
                self._log_suspicious_activity(client_ip, "sql_injection_attempt", {
                    "pattern": pattern,
                    "path": path,
                    "query": query_string
                })
                return True
        
        # Check for directory traversal
        if "../" in path or "..%2f" in path or "..%5c" in path:
            self._log_suspicious_activity(client_ip, "directory_traversal", {
                "path": path
            })
            return True
        
        # Check for admin path access from non-whitelisted IPs
        admin_paths = ["/admin", "/api/admin", "/management", "/config"]
        if any(admin_path in path for admin_path in admin_paths):
            if not self._is_admin_ip(client_ip):
                self._log_suspicious_activity(client_ip, "unauthorized_admin_access", {
                    "path": path
                })
                return True
        
        return False
    
    def _is_admin_ip(self, ip: str) -> bool:
        """Check if IP is in admin whitelist"""
        try:
            # Check direct matches
            if ip in self.admin_ip_whitelist:
                return True
            
            # Check if it's a private IP (for internal admin access)
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private:
                return True
            
            return False
        except ValueError:
            return False
    
    def _log_suspicious_activity(self, ip: str, activity_type: str, details: Dict):
        """Log suspicious activity"""
        if ip not in self.suspicious_activities:
            self.suspicious_activities[ip] = []
        
        activity = {
            'type': activity_type,
            'timestamp': datetime.now(),
            'details': details
        }
        
        self.suspicious_activities[ip].append(activity)
        
        # Keep only last 100 activities per IP
        if len(self.suspicious_activities[ip]) > 100:
            self.suspicious_activities[ip] = self.suspicious_activities[ip][-100:]
        
        logger.warning(f"SUSPICIOUS ACTIVITY: {activity_type} from {ip} - {details}")
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def hash_sensitive_data(self, data: str, salt: Optional[str] = None) -> Dict[str, str]:
        """Hash sensitive data with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for password hashing
        hashed = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
        
        return {
            'hash': hashed.hex(),
            'salt': salt,
            'algorithm': 'pbkdf2_sha256',
            'iterations': 100000
        }
    
    def verify_hashed_data(self, data: str, stored_hash: str, salt: str) -> bool:
        """Verify hashed data"""
        try:
            computed_hash = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
            return secrets.compare_digest(computed_hash.hex(), stored_hash)
        except Exception as e:
            logger.error(f"Hash verification error: {e}")
            return False
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get comprehensive security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Content-Security-Policy": self.csp_policy,
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin"
        }
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\.\.', '', filename)
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename or 'unnamed_file'
    
    def validate_url(self, url: str, allowed_domains: Optional[List[str]] = None) -> bool:
        """Validate URL for security"""
        try:
            parsed = urlparse(url)
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Only allow HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Check allowed domains if specified
            if allowed_domains:
                domain = parsed.netloc.lower()
                if not any(domain.endswith(allowed) for allowed in allowed_domains):
                    return False
            
            # Block private IPs in production
            try:
                ip = ipaddress.ip_address(parsed.hostname)
                if ip.is_private or ip.is_loopback:
                    return False
            except (ValueError, TypeError):
                pass  # Not an IP address, continue
            
            return True
            
        except Exception:
            return False
    
    def get_security_report(self) -> Dict:
        """Get security activity report"""
        current_time = datetime.now()
        recent_activities = []
        
        for ip, activities in self.suspicious_activities.items():
            recent = [
                a for a in activities 
                if current_time - a['timestamp'] < timedelta(hours=24)
            ]
            if recent:
                recent_activities.extend([{
                    'ip': ip,
                    'type': a['type'],
                    'timestamp': a['timestamp'],
                    'details': a['details']
                } for a in recent])
        
        return {
            'total_suspicious_ips': len(self.suspicious_activities),
            'recent_activities_24h': len(recent_activities),
            'activities': sorted(recent_activities, key=lambda x: x['timestamp'], reverse=True)[:50],
            'admin_whitelist_size': len(self.admin_ip_whitelist),
            'blocked_user_agents': list(self.blocked_user_agents)
        }

# Global security enhancer instance
security_enhancer = SecurityEnhancer()