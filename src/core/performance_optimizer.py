"""
Performance Optimizer for reducing lag and improving app responsiveness
"""

import logging
import os
import threading
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Optimizes app performance to reduce lag"""
    
    def __init__(self):
        self.optimization_active = False
        self.optimization_thread = None
        self.detection_interval = 4000  # ms
        self.resource_usage = {}
        
    def start_optimization(self):
        """Start performance optimization"""
        if not self.optimization_active:
            self.optimization_active = True
            self.optimization_thread = threading.Thread(target=self._monitor_resources, daemon=True)
            self.optimization_thread.start()
            logger.info("Performance optimization started")
    
    def stop_optimization(self):
        """Stop performance optimization"""
        self.optimization_active = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=1.0)
            self.optimization_thread = None
        logger.info("Performance optimization stopped")
    
    def _monitor_resources(self):
        """Monitor system resources and adjust app behavior"""
        while self.optimization_active:
            try:
                # Get current resource usage
                self.resource_usage = self._get_resource_usage()
                
                # Adjust detection interval based on CPU usage
                self._adjust_detection_interval()
                
                # Sleep for a bit
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                time.sleep(10)
    
    def _get_resource_usage(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        try:
            # Simple resource check without psutil dependency
            cpu_usage = 50  # Default value
            memory_usage = 50  # Default value
            
            # Try to get actual CPU usage if on Linux
            try:
                with open('/proc/stat', 'r') as f:
                    cpu_info = f.readline().split()
                    cpu_usage = 100 - float(cpu_info[4]) * 100 / sum(float(x) for x in cpu_info[1:])
            except:
                pass
            
            return {
                'cpu_percent': cpu_usage,
                'memory_percent': memory_usage,
                'system_cpu': cpu_usage,
                'system_memory': memory_usage
            }
        except Exception as e:
            logger.error(f"Failed to get resource usage: {e}")
            return {}
    
    def _adjust_detection_interval(self):
        """Adjust detection interval based on CPU usage"""
        cpu_usage = self.resource_usage.get('system_cpu', 50)
        
        # Adjust interval based on CPU load - use longer intervals to reduce lag
        if cpu_usage > 70:
            # Heavy load - significantly reduce frequency
            self.detection_interval = 8000  # 8 seconds
            logger.info(f"High CPU load ({cpu_usage}%) - significantly reduced detection frequency")
        elif cpu_usage > 50:
            # Medium load - reduce frequency
            self.detection_interval = 6000  # 6 seconds
            logger.info(f"Medium CPU load ({cpu_usage}%) - reduced detection frequency")
        else:
            # Light load - normal frequency
            self.detection_interval = 4000  # 4 seconds
            
        # Never go below 4 seconds to prevent excessive CPU usage
        if self.detection_interval < 4000:
            self.detection_interval = 4000
    
    def get_optimal_detection_interval(self) -> int:
        """Get the optimal detection interval based on current system load"""
        return self.detection_interval
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage statistics"""
        return self.resource_usage