"""
KAILASH Performance Monitoring and Optimization
Production-grade performance utilities
Domain: kailash-ai.in
"""
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict, deque
import psutil
import gc

logger = logging.getLogger("kailash.performance")

class PerformanceMonitor:
    """Production performance monitoring for KAILASH"""
    
    def __init__(self):
        self.request_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.slow_queries: List[Dict] = []
        self.memory_usage: deque = deque(maxlen=100)
        self.cpu_usage: deque = deque(maxlen=100)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.last_cleanup = time.time()
        
    def track_request(self, endpoint: str, duration: float, status_code: int):
        """Track API request performance"""
        self.request_times[endpoint].append({
            'duration': duration,
            'timestamp': time.time(),
            'status': status_code
        })
        
        # Log slow requests
        if duration > 2.0:  # 2 second threshold
            logger.warning(f"SLOW REQUEST: {endpoint} took {duration:.3f}s")
            self.slow_queries.append({
                'endpoint': endpoint,
                'duration': duration,
                'timestamp': datetime.now(),
                'status': status_code
            })
    
    def track_system_metrics(self):
        """Track system resource usage"""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage.append({
                'percent': memory.percent,
                'available': memory.available,
                'timestamp': time.time()
            })
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_usage.append({
                'percent': cpu_percent,
                'timestamp': time.time()
            })
            
            # Trigger garbage collection if memory usage is high
            if memory.percent > 85:
                logger.warning(f"High memory usage: {memory.percent}% - triggering GC")
                gc.collect()
                
        except Exception as e:
            logger.error(f"System metrics tracking error: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        current_time = time.time()
        
        # Calculate average response times
        avg_times = {}
        for endpoint, times in self.request_times.items():
            if times:
                recent_times = [t['duration'] for t in times if current_time - t['timestamp'] < 300]  # Last 5 minutes
                if recent_times:
                    avg_times[endpoint] = {
                        'avg': sum(recent_times) / len(recent_times),
                        'max': max(recent_times),
                        'count': len(recent_times)
                    }
        
        # System metrics
        current_memory = self.memory_usage[-1] if self.memory_usage else {'percent': 0}
        current_cpu = self.cpu_usage[-1] if self.cpu_usage else {'percent': 0}
        
        return {
            'response_times': avg_times,
            'slow_queries_count': len([q for q in self.slow_queries if current_time - q['timestamp'].timestamp() < 3600]),
            'memory_usage': current_memory['percent'],
            'cpu_usage': current_cpu['percent'],
            'total_errors': sum(self.error_counts.values()),
            'uptime': current_time - self.last_cleanup
        }
    
    def cleanup_old_data(self):
        """Clean up old performance data"""
        current_time = time.time()
        
        # Clean slow queries older than 24 hours
        self.slow_queries = [
            q for q in self.slow_queries 
            if current_time - q['timestamp'].timestamp() < 86400
        ]
        
        # Clean request times older than 1 hour
        for endpoint in list(self.request_times.keys()):
            self.request_times[endpoint] = deque([
                t for t in self.request_times[endpoint]
                if current_time - t['timestamp'] < 3600
            ], maxlen=1000)
            
            if not self.request_times[endpoint]:
                del self.request_times[endpoint]
        
        self.last_cleanup = current_time
        logger.debug("Performance data cleanup completed")

# Global performance monitor instance
perf_monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            if duration > 1.0:  # Log slow functions
                logger.warning(f"SLOW FUNCTION: {func.__name__} took {duration:.3f}s")
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            perf_monitor.error_counts[func.__name__] += 1
            logger.error(f"FUNCTION ERROR: {func.__name__} failed after {duration:.3f}s: {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if duration > 1.0:  # Log slow functions
                logger.warning(f"SLOW FUNCTION: {func.__name__} took {duration:.3f}s")
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            perf_monitor.error_counts[func.__name__] += 1
            logger.error(f"FUNCTION ERROR: {func.__name__} failed after {duration:.3f}s: {e}")
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

class DatabaseOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def create_compound_index_suggestions(collection_name: str, query_patterns: List[Dict]) -> List[Dict]:
        """Suggest compound indexes based on query patterns"""
        suggestions = []
        
        for pattern in query_patterns:
            fields = list(pattern.keys())
            if len(fields) > 1:
                suggestions.append({
                    'collection': collection_name,
                    'index': {field: 1 for field in fields},
                    'reason': f"Compound index for frequent query pattern: {fields}"
                })
        
        return suggestions
    
    @staticmethod
    async def analyze_slow_queries(db, collection_name: str, threshold_ms: int = 100):
        """Analyze slow queries and suggest optimizations"""
        try:
            # Enable profiling for slow operations
            await db.command("profile", 2, slowms=threshold_ms)
            
            # Get profiling data
            profiling_data = await db.system.profile.find().sort("ts", -1).limit(100).to_list(100)
            
            slow_queries = []
            for op in profiling_data:
                if op.get('millis', 0) > threshold_ms:
                    slow_queries.append({
                        'collection': op.get('ns', '').split('.')[-1],
                        'operation': op.get('op'),
                        'duration_ms': op.get('millis'),
                        'command': op.get('command', {}),
                        'timestamp': op.get('ts')
                    })
            
            return slow_queries
            
        except Exception as e:
            logger.error(f"Slow query analysis failed: {e}")
            return []

# Background task to monitor system performance
async def performance_monitoring_task():
    """Background task for continuous performance monitoring"""
    while True:
        try:
            perf_monitor.track_system_metrics()
            perf_monitor.cleanup_old_data()
            
            # Log performance summary every 5 minutes
            stats = perf_monitor.get_performance_stats()
            if stats['memory_usage'] > 80 or stats['cpu_usage'] > 80:
                logger.warning(f"High resource usage - Memory: {stats['memory_usage']:.1f}%, CPU: {stats['cpu_usage']:.1f}%")
            
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Performance monitoring error: {e}")
            await asyncio.sleep(60)