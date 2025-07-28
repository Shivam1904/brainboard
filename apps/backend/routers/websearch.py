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
    CreateWebSearchWidgetRequest,
    CreateWebSearchWidgetResponse,
    WebSearchQueryResponse,
    WebSearchWidgetDataResponse,
    GenerateSummaryRequest,
    GenerateSummaryResponse,
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

@router.post("/generateSearch", response_model=CreateWebSearchWidgetResponse)
async def create_search_widget(
    widget_data: CreateWebSearchWidgetRequest,
    db: Session = Depends(get_db),
    services = Depends(get_services)
):
    """Create a websearch widget and save search term"""
    try:
        # Create the websearch widget first
        widget = DashboardWidget(
            user_id="default-user",  # TODO: Get from auth when available
            title=widget_data.title,
            widget_type="websearch",
            frequency=widget_data.frequency,
            category=widget_data.category,
            importance=widget_data.importance,
            settings={}
        )
        
        db.add(widget)
        db.flush()  # Get the widget ID without committing
        
        # Create search query record
        search_query = WebSearchQuery(
            dashboard_widget_id=widget.id,
            search_term=widget_data.search_term
        )
        
        db.add(search_query)
        db.commit()
        db.refresh(widget)
        db.refresh(search_query)
        
        logger.info(f"Created websearch widget: {widget.title} with search term: {search_query.search_term}")
        
        return CreateWebSearchWidgetResponse(
            widget_id=widget.id,
            search_query_id=search_query.id,
            title=widget.title,
            search_term=search_query.search_term,
            widget_type=widget.widget_type,
            created_at=widget.created_at
        )
        
    except Exception as e:
        services['utils'].handle_database_error("create search widget", e)

@router.post("/{widget_id}/summarize", response_model=GenerateSummaryResponse)
async def generate_summary_for_widget(
    widget_id: str,
    summary_request: GenerateSummaryRequest,
    db: Session = Depends(get_db),
    services = Depends(get_services)
):
    """Generate AI summary for a widget based on search query"""
    try:
        # Verify widget exists
        services['utils'].verify_widget_exists(db, widget_id, "websearch")
        
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
            dashboard_widget_id=widget_id,
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
        
        logger.info(f"Successfully generated summary for widget: {widget_id}")
        
        return GenerateSummaryResponse(
            success=True,
            message="Summary generated and saved successfully",
            widget_id=widget_id
        )
        
    except Exception as e:
        logger.error(f"Failed to generate summary for widget {widget_id}: {e}")
        return GenerateSummaryResponse(
            success=False,
            message=f"Failed to generate summary: {str(e)}",
            widget_id=widget_id
        )

@router.get("/{widget_id}/summary", response_model=List[SummaryResponse])
async def get_widget_summary(
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

@router.delete("/{widget_id}")
async def delete_widget_data(
    widget_id: str,
    db: Session = Depends(get_db),
    services = Depends(get_services)
):
    """Delete all search queries and summaries for a widget"""
    try:
        # Verify widget exists
        services['utils'].verify_widget_exists(db, widget_id, "websearch")
        
        # Delete all summaries for the widget
        summaries_deleted = db.query(Summary).filter(
            Summary.dashboard_widget_id == widget_id
        ).delete()
        
        # Delete all search queries for the widget
        searches_deleted = db.query(WebSearchQuery).filter(
            WebSearchQuery.dashboard_widget_id == widget_id
        ).delete()
        
        db.commit()
        
        return services['utils'].format_success_response(
            f"Deleted {searches_deleted} search queries and {summaries_deleted} summaries for widget {widget_id}"
        )
        
    except Exception as e:
        services['utils'].handle_database_error("delete widget data", e)
