"""
WebSearch Widget Router
API endpoints for web search functionality with AI summaries
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from core.database import get_db
from models.database_models import WebSearchQuery, DashboardWidget, Summary
from models.schemas.websearch_schemas import (
    CreateWebSearchQueryRequest,
    WebSearchQueryResponse,
    WebSearchWidgetDataResponse,
    GenerateSummaryRequest,
    SummaryResponse
)
from services.web_search_service import WebSearchService
from services.ai_summarization_service import AISummarizationService
from utils.router_utils import RouterUtils

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websearch"])

def get_services(db: Session = Depends(get_db)):
    """Get required services"""
    return {
        'web_search': WebSearchService(),
        'ai_summary': AISummarizationService(),
        'utils': RouterUtils()
    }

@router.post("/search", response_model=WebSearchQueryResponse)
async def create_search_query(
    search_data: CreateWebSearchQueryRequest,
    db: Session = Depends(get_db),
    services = Depends(get_services)
):
    """Create a new web search query for a widget"""
    try:
        # Verify widget exists and is websearch type
        widget = services['utils'].verify_widget_exists(db, search_data.dashboard_widget_id, "websearch")
        
        # Create search query record
        search_query = WebSearchQuery(
            dashboard_widget_id=search_data.dashboard_widget_id,
            search_term=search_data.search_term
        )
        
        db.add(search_query)
        db.commit()
        db.refresh(search_query)
        
        logger.info(f"Created search query: {search_query.search_term} for widget {search_data.dashboard_widget_id}")
        return WebSearchQueryResponse.from_orm(search_query)
        
    except Exception as e:
        services['utils'].handle_database_error("create search query", e)

@router.post("/search/{search_id}/summarize", response_model=SummaryResponse)
async def generate_summary_for_search(
    search_id: str,
    summary_request: GenerateSummaryRequest,
    db: Session = Depends(get_db),
    services = Depends(get_services)
):
    """Generate AI summary for a search query"""
    try:
        # Get the search query
        search_query = db.query(WebSearchQuery).filter(WebSearchQuery.id == search_id).first()
        if not search_query:
            raise HTTPException(status_code=404, detail="Search query not found")
        
        # Perform web search
        logger.info(f"Performing web search for: {summary_request.query}")
        search_results = await services['web_search'].search(summary_request.query)
        
        # Generate AI summary
        context = " ".join([result.snippet for result in search_results[:5]])  # Use top 5 results
        summary_text = await services['ai_summary'].summarize(
            content=context,
            query=summary_request.query
        )
        
        # Save summary to database
        sources = [result.url for result in search_results[:5]]
        summary = Summary(
            dashboard_widget_id=search_query.dashboard_widget_id,
            query=summary_request.query,
            summary_text=summary_text,
            sources_json=sources,
            search_results_json=[{
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet
            } for r in search_results]
        )
        
        db.add(summary)
        db.commit()
        db.refresh(summary)
        
        logger.info(f"Generated summary for search query: {search_id}")
        
        return SummaryResponse(
            id=summary.summary_id,
            query=summary.query,
            summary=summary.summary_text,
            sources=summary.sources_json or [],
            createdAt=summary.created_at.isoformat()
        )
        
    except Exception as e:
        services['utils'].handle_database_error("generate summary", e)

@router.get("/widget/{widget_id}/searches", response_model=List[WebSearchQueryResponse])
async def get_widget_searches(
    widget_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    services = Depends(get_services)
):
    """Get search queries for a widget"""
    try:
        # Verify widget exists
        services['utils'].verify_widget_exists(db, widget_id, "websearch")
        
        # Get search queries
        searches = db.query(WebSearchQuery).filter(
            WebSearchQuery.dashboard_widget_id == widget_id
        ).order_by(WebSearchQuery.created_at.desc()).offset(skip).limit(limit).all()
        
        return [WebSearchQueryResponse.from_orm(search) for search in searches]
        
    except Exception as e:
        services['utils'].handle_database_error("get widget searches", e)

@router.get("/widget/{widget_id}/summaries", response_model=List[SummaryResponse])
async def get_widget_summaries(
    widget_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    services = Depends(get_services)
):
    """Get AI summaries for a widget"""
    try:
        # Verify widget exists
        services['utils'].verify_widget_exists(db, widget_id, "websearch")
        
        # Get summaries
        summaries = db.query(Summary).filter(
            Summary.dashboard_widget_id == widget_id
        ).order_by(Summary.created_at.desc()).offset(skip).limit(limit).all()
        
        return [
            SummaryResponse(
                id=summary.summary_id,
                query=summary.query,
                summary=summary.summary_text,
                sources=summary.sources_json or [],
                createdAt=summary.created_at.isoformat()
            ) for summary in summaries
        ]
        
    except Exception as e:
        services['utils'].handle_database_error("get widget summaries", e)

@router.get("/widget/{widget_id}/data", response_model=WebSearchWidgetDataResponse)
async def get_widget_data(
    widget_id: str,
    db: Session = Depends(get_db),
    services = Depends(get_services)
):
    """Get complete widget data with searches and recent summaries"""
    try:
        # Verify widget exists
        services['utils'].verify_widget_exists(db, widget_id, "websearch")
        
        # Get recent searches
        searches = db.query(WebSearchQuery).filter(
            WebSearchQuery.dashboard_widget_id == widget_id
        ).order_by(WebSearchQuery.created_at.desc()).limit(10).all()
        
        # Get recent summaries
        summaries = db.query(Summary).filter(
            Summary.dashboard_widget_id == widget_id
        ).order_by(Summary.created_at.desc()).limit(5).all()
        
        # Calculate stats
        total_searches = db.query(WebSearchQuery).filter(
            WebSearchQuery.dashboard_widget_id == widget_id
        ).count()
        
        total_summaries = db.query(Summary).filter(
            Summary.dashboard_widget_id == widget_id
        ).count()
        
        return WebSearchWidgetDataResponse(
            widget_id=widget_id,
            queries=[WebSearchQueryResponse.from_orm(s) for s in searches],
            recent_summaries=[{
                "id": s.summary_id,
                "query": s.query,
                "summary": s.summary_text[:200] + "..." if len(s.summary_text) > 200 else s.summary_text,
                "created_at": s.created_at.isoformat()
            } for s in summaries],
            stats={
                "total_searches": total_searches,
                "total_summaries": total_summaries,
                "recent_activity": len(searches)
            }
        )
        
    except Exception as e:
        services['utils'].handle_database_error("get widget data", e)

@router.delete("/search/{search_id}")
async def delete_search_query(
    search_id: str,
    db: Session = Depends(get_db),
    services = Depends(get_services)
):
    """Delete a search query"""
    try:
        search_query = db.query(WebSearchQuery).filter(WebSearchQuery.id == search_id).first()
        if not search_query:
            raise HTTPException(status_code=404, detail="Search query not found")
        
        db.delete(search_query)
        db.commit()
        
        return services['utils'].format_success_response(f"Search query {search_id} deleted")
        
    except Exception as e:
        services['utils'].handle_database_error("delete search query", e)
