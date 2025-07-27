import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize DynamoDB resource with error handling for local development
try:
    dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
    # Test the connection
    list(dynamodb.tables.all())
    logger.info("Connected to AWS DynamoDB")
except (NoCredentialsError, ProfileNotFound) as e:
    logger.warning(f"AWS credentials not found: {e}. Running in local mode without DynamoDB.")
    dynamodb = None
except Exception as e:
    logger.error(f"Error connecting to DynamoDB: {e}")
    dynamodb = None

def init_db():
    """Initialize database tables if they don't exist"""
    if dynamodb is None:
        logger.warning("DynamoDB not available. Skipping database initialization.")
        return
    
    try:
        # Check if tables exist, create if they don't
        create_reminders_table()
        create_summaries_table()
        create_users_table()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

def create_reminders_table():
    """Create reminders table"""
    if dynamodb is None:
        logger.warning("DynamoDB not available. Cannot create reminders table.")
        return
        
    try:
        table = dynamodb.create_table(
            TableName=settings.dynamodb_table_reminders,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'reminder_id',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'reminder_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        logger.info(f"Created table: {settings.dynamodb_table_reminders}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logger.info(f"Table {settings.dynamodb_table_reminders} already exists")
        else:
            raise

def create_summaries_table():
    """Create summaries table"""
    try:
        table = dynamodb.create_table(
            TableName=settings.dynamodb_table_summaries,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'summary_id',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'summary_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        logger.info(f"Created table: {settings.dynamodb_table_summaries}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logger.info(f"Table {settings.dynamodb_table_summaries} already exists")
        else:
            raise

def create_users_table():
    """Create users table"""
    try:
        table = dynamodb.create_table(
            TableName=settings.dynamodb_table_users,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        logger.info(f"Created table: {settings.dynamodb_table_users}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logger.info(f"Table {settings.dynamodb_table_users} already exists")
        else:
            raise

def get_dynamodb_table(table_name: str):
    """Get DynamoDB table resource"""
    if dynamodb is None:
        logger.warning(f"DynamoDB not available. Cannot access table: {table_name}")
        return None
    return dynamodb.Table(table_name)
