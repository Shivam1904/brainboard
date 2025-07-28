from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseDataAccess(ABC, Generic[T]):
    """Abstract base data access with common CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def update(self, id: str, entity: T) -> Optional[T]:
        """Update entity by ID"""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """List all entities with pagination"""
        pass
