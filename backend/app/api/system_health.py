"""
KAILASH System Health API
Enhanced system monitoring and health checks
Domain: kailash-ai.in
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import asyncio
import time
from datetime import datetime

from ..core.mongodb import MongoD
from ..core.performance import perf_monitor, monitor_performance
from ..core.security_enhancements import security_enhancer
from ..middleware.security import security_middleware

router = APIRouter()

@router.get("/api/system/health/detailed")
@monitor_performance
async def detailed_health_check(request: Request):
    """Comprehensive system health check with performance metrics"""
    
    # Check for suspicious activity
    if security_enhancer.detect_suspicious_activity(request):
        raise HTTPException(
            status_code=403,
            detail="Suspicious activity detected"
        )
    
    start_time = time.time()
    health_data = {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "checks": {},
        "performance": {},
        "security": {}
    }
    
    # Database connectivity check
    try:
        db_start = time.time()
        if MongoD.client:
            await MongoD.client.admin.command('ping', maxTimeMS=2000)
            health_data["checks"]["database"] = {
                "status": "healthy",
                "response_time_ms": round((time.time() - db_start) * 1000, 2),
                "connection_pool": "active"
            }
        else:
            health_data["checks"]["database"] = {
                "status": "disconnected",
                "error": "No database connection"
            }
            health_data["status"] = "degraded"
    except Exception as e:
        health_data["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": round((time.time() - db_start) * 1000, 2)
        }
        health_data["status"] = "degraded"
    
    # Performance metrics
    perf_stats = perf_monitor.get_performance_stats()
    health_data["performance"] = {
        "memory_usage_percent": perf_stats.get("memory_usage", 0),
        "cpu_usage_percent": perf_stats.get("cpu_usage", 0),
        "slow_queries_last_hour": perf_stats.get("slow_queries_count", 0),
        "total_errors": perf_stats.get("total_errors", 0),
        "uptime_seconds": perf_stats.get("uptime", 0),
        "average_response_times": perf_stats.get("response_times", {})
    }
    
    # Security metrics
    security_stats = security_middleware.get_security_stats()
    security_report = security_enhancer.get_security_report()
    health_data["security"] = {
        "active_rate_limits": security_stats.get("active_rate_limits", 0),
        "blocked_ips": security_stats.get("blocked_ips", 0),
        "blocked_devices": security_stats.get("blocked_devices", 0),
        "suspicious_activities_24h": security_report.get("recent_activities_24h", 0),
        "failed_login_attempts": security_stats.get("total_failed_attempts", 0)
    }
    
    # System resource checks
    if health_data["performance"]["memory_usage_percent"] > 90:
        health_data["status"] = "critical"
        health_data["alerts"] = health_data.get("alerts", [])
        health_data["alerts"].append("Critical memory usage")
    elif health_data["performance"]["memory_usage_percent"] > 80:
        health_data["status"] = "warning"
        health_data["alerts"] = health_data.get("alerts", [])
        health_data["alerts"].append("High memory usage")
    
    if health_data["performance"]["cpu_usage_percent"] > 90:
        health_data["status"] = "critical"
        health_data["alerts"] = health_data.get("alerts", [])
        health_data["alerts"].append("Critical CPU usage")
    
    # Overall response time
    health_data["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    # Set appropriate HTTP status code
    status_code = 200
    if health_data["status"] == "critical":
        status_code = 503
    elif health_data["status"] == "degraded":
        status_code = 200  # Still functional
    
    return JSONResponse(content=health_data, status_code=status_code)

@router.get("/api/system/performance/stats")
@monitor_performance
async def performance_statistics():
    """Get detailed performance statistics"""
    stats = perf_monitor.get_performance_stats()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "performance_metrics": stats,
        "recommendations": _generate_performance_recommendations(stats)
    }

@router.get("/api/system/security/report")
@monitor_performance
async def security_report(request: Request):
    """Get security activity report (admin only)"""
    
    # Check if request is from admin IP
    if not security_enhancer._is_admin_ip(request.client.host if request.client else "unknown"):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    report = security_enhancer.get_security_report()
    security_stats = security_middleware.get_security_stats()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "security_report": report,
        "middleware_stats": security_stats,
        "recommendations": _generate_security_recommendations(report, security_stats)
    }

@router.post("/api/system/maintenance/cleanup")
@monitor_performance
async def trigger_maintenance_cleanup(request: Request):
    """Trigger system maintenance cleanup (admin only)"""
    
    # Check if request is from admin IP
    if not security_enhancer._is_admin_ip(request.client.host if request.client else "unknown"):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    cleanup_results = {}
    
    try:
        # Performance data cleanup
        perf_monitor.cleanup_old_data()
        cleanup_results["performance_data"] = "cleaned"
        
        # Security data cleanup (keep last 7 days)
        current_time = datetime.now()
        for ip in list(security_enhancer.suspicious_activities.keys()):
            security_enhancer.suspicious_activities[ip] = [
                activity for activity in security_enhancer.suspicious_activities[ip]
                if (current_time - activity['timestamp']).days < 7
            ]
            if not security_enhancer.suspicious_activities[ip]:
                del security_enhancer.suspicious_activities[ip]
        
        cleanup_results["security_data"] = "cleaned"
        
        # Database connection pool refresh
        if MongoD.client:
            # This will refresh the connection pool
            await MongoD.client.admin.command('ping')
            cleanup_results["database_pool"] = "refreshed"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "cleanup_results": cleanup_results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Maintenance cleanup failed: {str(e)}"
        )

def _generate_performance_recommendations(stats: Dict) -> list:
    """Generate performance optimization recommendations"""
    recommendations = []
    
    if stats.get("memory_usage", 0) > 80:
        recommendations.append({
            "type": "memory",
            "severity": "high",
            "message": "High memory usage detected. Consider scaling up or optimizing memory-intensive operations."
        })
    
    if stats.get("cpu_usage", 0) > 80:
        recommendations.append({
            "type": "cpu",
            "severity": "high", 
            "message": "High CPU usage detected. Consider scaling horizontally or optimizing CPU-intensive operations."
        })
    
    if stats.get("slow_queries_count", 0) > 10:
        recommendations.append({
            "type": "database",
            "severity": "medium",
            "message": "Multiple slow queries detected. Review database indexes and query optimization."
        })
    
    # Check response times
    response_times = stats.get("response_times", {})
    for endpoint, metrics in response_times.items():
        if metrics.get("avg", 0) > 2.0:
            recommendations.append({
                "type": "endpoint",
                "severity": "medium",
                "message": f"Slow endpoint detected: {endpoint} (avg: {metrics['avg']:.2f}s). Consider optimization."
            })
    
    return recommendations

def _generate_security_recommendations(security_report: Dict, security_stats: Dict) -> list:
    """Generate security recommendations"""
    recommendations = []
    
    if security_report.get("recent_activities_24h", 0) > 50:
        recommendations.append({
            "type": "security",
            "severity": "high",
            "message": "High number of suspicious activities detected. Review security logs and consider IP blocking."
        })
    
    if security_stats.get("blocked_ips", 0) > 100:
        recommendations.append({
            "type": "security",
            "severity": "medium",
            "message": "Large number of blocked IPs. Consider reviewing block list and implementing geographic restrictions."
        })
    
    if security_stats.get("total_failed_attempts", 0) > 1000:
        recommendations.append({
            "type": "authentication",
            "severity": "high",
            "message": "High number of failed login attempts. Consider implementing CAPTCHA or additional authentication factors."
        })
    
    return recommendations