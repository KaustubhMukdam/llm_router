"""
Redis client initialization and connection management.
Fails fast on connection errors to prevent degraded service startup.
"""

import os
from typing import Optional
import redis
from redis.exceptions import ConnectionError, TimeoutError


class RedisClient:
    """
    Singleton Redis client with environment-based configuration.
    Fails fast on initialization if Redis is unreachable.
    """
    
    _instance: Optional[redis.Redis] = None
    _initialized: bool = False
    
    @classmethod
    def initialize(cls) -> redis.Redis:
        """
        Initialize Redis client from environment variables.
        
        Environment variables:
            REDIS_HOST: Redis server host (default: localhost)
            REDIS_PORT: Redis server port (default: 6379)
            REDIS_PASSWORD: Redis password (optional)
            REDIS_DB: Redis database number (default: 0)
            REDIS_SOCKET_TIMEOUT: Socket timeout in seconds (default: 5)
            REDIS_SOCKET_CONNECT_TIMEOUT: Connection timeout in seconds (default: 5)
        
        Returns:
            redis.Redis: Configured Redis client
            
        Raises:
            ConnectionError: If unable to connect to Redis
            TimeoutError: If connection times out
            ValueError: If configuration is invalid
        """
        if cls._initialized and cls._instance is not None:
            return cls._instance
        
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        password = os.getenv("REDIS_PASSWORD")
        db = int(os.getenv("REDIS_DB", "0"))
        socket_timeout = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
        socket_connect_timeout = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))
        
        try:
            client = redis.Redis(
                host=host,
                port=port,
                password=password if password else None,
                db=db,
                socket_timeout=socket_timeout,
                socket_connect_timeout=socket_connect_timeout,
                decode_responses=True,
                socket_keepalive=True,
                health_check_interval=30
            )
            
            # Fail fast: verify connection immediately
            client.ping()
            
            cls._instance = client
            cls._initialized = True
            
            return client
            
        except (ConnectionError, TimeoutError) as e:
            error_msg = (
                f"Failed to connect to Redis at {host}:{port}. "
                f"Ensure Redis is running and accessible. Error: {str(e)}"
            )
            raise ConnectionError(error_msg) from e
        except ValueError as e:
            error_msg = f"Invalid Redis configuration: {str(e)}"
            raise ValueError(error_msg) from e
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """
        Get initialized Redis client.
        
        Returns:
            redis.Redis: Active Redis client
            
        Raises:
            RuntimeError: If client not initialized
        """
        if not cls._initialized or cls._instance is None:
            raise RuntimeError(
                "Redis client not initialized. Call RedisClient.initialize() first."
            )
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """
        Reset client instance. Used primarily for testing.
        """
        if cls._instance is not None:
            try:
                cls._instance.close()
            except Exception:
                pass
        cls._instance = None
        cls._initialized = False


def get_redis_client() -> redis.Redis:
    """
    Convenience function to get Redis client.
    
    Returns:
        redis.Redis: Active Redis client
        
    Raises:
        RuntimeError: If client not initialized
    """
    return RedisClient.get_client()
