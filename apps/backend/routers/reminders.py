from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
import uuid

from models.schemas import Reminder, ReminderCreate, ReminderUpdate
from core.auth import get_current_user
from core.database import get_dynamodb_table
from core.config import settings

router = APIRouter()

@router.get("/", response_model=List[Reminder])
async def get_reminders(current_user: str = Depends(get_current_user)):
    """Get all reminders for the current user"""
    try:
        table = get_dynamodb_table(settings.dynamodb_table_reminders)
        
        # If DynamoDB is not available (local development), return empty list
        if table is None:
            return []
        
        response = table.query(
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': current_user}
        )
        
        reminders = []
        for item in response.get('Items', []):
            reminder = Reminder(
                id=item['reminder_id'],
                user_id=item['user_id'],
                text=item['text'],
                completed=item.get('completed', False),
                due_date=datetime.fromisoformat(item['due_date']) if item.get('due_date') else None,
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at']) if item.get('updated_at') else None
            )
            reminders.append(reminder)
        
        return reminders
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reminders: {str(e)}"
        )

@router.post("/", response_model=Reminder, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a new reminder"""
    try:
        table = get_dynamodb_table(settings.dynamodb_table_reminders)
        
        reminder_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # If DynamoDB is not available (local development), just return mock data
        if table is None:
            return Reminder(
                id=reminder_id,
                user_id=current_user,
                text=reminder_data.text,
                completed=False,
                due_date=reminder_data.due_date,
                created_at=now
            )
        
        item = {
            'user_id': current_user,
            'reminder_id': reminder_id,
            'text': reminder_data.text,
            'completed': False,
            'created_at': now.isoformat()
        }
        
        if reminder_data.due_date:
            item['due_date'] = reminder_data.due_date.isoformat()
        
        table.put_item(Item=item)
        
        reminder = Reminder(
            id=reminder_id,
            user_id=current_user,
            text=reminder_data.text,
            completed=False,
            due_date=reminder_data.due_date,
            created_at=now
        )
        
        return reminder
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reminder: {str(e)}"
        )

@router.put("/{reminder_id}", response_model=Reminder)
async def update_reminder(
    reminder_id: str,
    reminder_data: ReminderUpdate,
    current_user: str = Depends(get_current_user)
):
    """Update a reminder"""
    try:
        table = get_dynamodb_table(settings.dynamodb_table_reminders)
        
        # Check if reminder exists and belongs to user
        response = table.get_item(
            Key={'user_id': current_user, 'reminder_id': reminder_id}
        )
        
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        item = response['Item']
        update_expression = "SET updated_at = :updated_at"
        expression_values = {':updated_at': datetime.utcnow().isoformat()}
        
        if reminder_data.text is not None:
            update_expression += ", #text = :text"
            expression_values[':text'] = reminder_data.text
        
        if reminder_data.completed is not None:
            update_expression += ", completed = :completed"
            expression_values[':completed'] = reminder_data.completed
        
        if reminder_data.due_date is not None:
            update_expression += ", due_date = :due_date"
            expression_values[':due_date'] = reminder_data.due_date.isoformat()
        
        table.update_item(
            Key={'user_id': current_user, 'reminder_id': reminder_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames={'#text': 'text'} if reminder_data.text is not None else None
        )
        
        # Return updated reminder
        updated_response = table.get_item(
            Key={'user_id': current_user, 'reminder_id': reminder_id}
        )
        updated_item = updated_response['Item']
        
        reminder = Reminder(
            id=updated_item['reminder_id'],
            user_id=updated_item['user_id'],
            text=updated_item['text'],
            completed=updated_item.get('completed', False),
            due_date=datetime.fromisoformat(updated_item['due_date']) if updated_item.get('due_date') else None,
            created_at=datetime.fromisoformat(updated_item['created_at']),
            updated_at=datetime.fromisoformat(updated_item['updated_at']) if updated_item.get('updated_at') else None
        )
        
        return reminder
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update reminder: {str(e)}"
        )

@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a reminder"""
    try:
        table = get_dynamodb_table(settings.dynamodb_table_reminders)
        
        # Check if reminder exists and belongs to user
        response = table.get_item(
            Key={'user_id': current_user, 'reminder_id': reminder_id}
        )
        
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        table.delete_item(
            Key={'user_id': current_user, 'reminder_id': reminder_id}
        )
        
        return {"message": "Reminder deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete reminder: {str(e)}"
        )
