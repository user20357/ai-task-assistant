"""
Memory Manager - Utility for monitoring and optimizing memory usage
"""

import os
import gc
import logging
import threading
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages application memory usage to prevent crashes"""
    
    def __init__(self):
        self.monitoring_active = False
        self.monitoring_thread = None
        self.memory_usage = {}
        self.gc_threshold = 80  # Memory percentage to trigger garbage collection
        
    def start_monitoring(self):
        """Start memory monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitor_memory, daemon=True)
            self.monitoring_thread.start()
            logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
            self.monitoring_thread = None
        logger.info("Memory monitoring stopped")
    
    def _monitor_memory(self):
        """Monitor memory usage and optimize when needed"""
        while self.monitoring_active:
            try:
                # Get current memory usage
                self.memory_usage = self._get_memory_usage()
                
                # Check if optimization is needed
                if self.memory_usage.get('percent', 0) > self.gc_threshold:
                    self._optimize_memory()
                
                # Sleep for a bit
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(30)
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage"""
        try:
            # Simple memory check without psutil dependency
            memory_info = {'percent': 50}  # Default value
            
            # Try to get actual memory usage if on Windows
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulong = ctypes.c_ulong
                
                class MEMORYSTATUS(ctypes.Structure):
                    _fields_ = [
                        ('dwLength', c_ulong),
                        ('dwMemoryLoad', c_ulong),
                        ('dwTotalPhys', c_ulong),
                        ('dwAvailPhys', c_ulong),
                        ('dwTotalPageFile', c_ulong),
                        ('dwAvailPageFile', c_ulong),
                        ('dwTotalVirtual', c_ulong),
                        ('dwAvailVirtual', c_ulong)
                    ]
                
                memory_status = MEMORYSTATUS()
                memory_status.dwLength = ctypes.sizeof(MEMORYSTATUS)
                kernel32.GlobalMemoryStatus(ctypes.byref(memory_status))
                
                memory_info = {
                    'percent': memory_status.dwMemoryLoad,
                    'total': memory_status.dwTotalPhys,
                    'available': memory_status.dwAvailPhys
                }
            except:
                pass
            
            return memory_info
            
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return {'percent': 0}
    
    def _optimize_memory(self):
        """Optimize memory usage"""
        try:
            logger.info(f"Memory usage high ({self.memory_usage.get('percent')}%) - optimizing...")
            
            # Force garbage collection
            gc.collect()
            
            # Clear any caches
            self._clear_caches()
            
            logger.info("Memory optimization completed")
            
        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")
    
    def _clear_caches(self):
        """Clear application caches"""
        # This would be extended with app-specific cache clearing
        pass
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        return self.memory_usage
    
    def force_optimize(self):
        """Force memory optimization"""
        self._optimize_memory()