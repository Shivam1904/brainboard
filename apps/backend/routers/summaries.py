from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
import uuid

from models.schemas import Summary, SummaryCreate
from core.auth import get_current_user
from core.database import get_dynamodb_table
from core.config import settings
from services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

@router.get("/", response_model=List[Summary])
async def get_summaries(current_user: str = Depends(get_current_user)):
    """Get all summaries for the current user"""
    try:
        table = get_dynamodb_table(settings.dynamodb_table_summaries)
        
        # If DynamoDB is not available (local development), return empty list
        if table is None:
            return []
        
        response = table.query(
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': current_user}
        )
        
        summaries = []
        for item in response.get('Items', []):
            summary = Summary(
                id=item['summary_id'],
                user_id=item['user_id'],
                query=item['query'],
                summary=item['summary'],
                sources=item.get('sources', []),
                created_at=datetime.fromisoformat(item['created_at'])
            )
            summaries.append(summary)
        
        return summaries
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch summaries: {str(e)}"
        )

@router.post("/", response_model=Summary, status_code=status.HTTP_201_CREATED)
async def create_summary(
    summary_data: SummaryCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a new summary by searching and summarizing web content"""
    try:
        # Use AI service to search and summarize
        search_results = await ai_service.search_web(summary_data.query)
        summary_text = await ai_service.summarize_content(summary_data.query, search_results)
        
        # Extract sources from search results
        sources = [result.get('link', '') for result in search_results.get('organic', [])]
        
        # Save to database
        table = get_dynamodb_table(settings.dynamodb_table_summaries)
        
        summary_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        item = {
            'user_id': current_user,
            'summary_id': summary_id,
            'query': summary_data.query,
            'summary': summary_text,
            'sources': sources,
            'created_at': now.isoformat()
        }
        
        table.put_item(Item=item)
        
        summary = Summary(
            id=summary_id,
            user_id=current_user,
            query=summary_data.query,
            summary=summary_text,
            sources=sources,
            created_at=now
        )
        
        return summary
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create summary: {str(e)}"
        )

@router.delete("/{summary_id}")
async def delete_summary(
    summary_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a summary"""
    try:
        table = get_dynamodb_table(settings.dynamodb_table_summaries)
        
        # Check if summary exists and belongs to user
        response = table.get_item(
            Key={'user_id': current_user, 'summary_id': summary_id}
        )
        
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found"
            )
        
        table.delete_item(
            Key={'user_id': current_user, 'summary_id': summary_id}
        )
        
        return {"message": "Summary deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete summary: {str(e)}"
        )
