from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseService(ABC):
    """Abstract base class for all services"""
    
    @abstractmethod
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data for the service"""
        pass
    
    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Standard error handling for services"""
        logger.error(f"Service error in {self.__class__.__name__}: {str(error)}")
        return {
            "error": True,
            "message": str(error),
            "service": self.__class__.__name__
        }
