"""
JSON utility functions for handling AI responses and other JSON data.
"""

import json
import re
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def clean_json_response(response: str) -> str:
    """
    Clean JSON response to handle common formatting issues.
    
    Args:
        response: Raw response string from AI
        
    Returns:
        Cleaned JSON string
    """
    if not response:
        return "{}"
    
    response = response.strip()
    
    # Remove markdown code blocks
    if response.startswith("```json"):
        response = response[7:]
    elif response.startswith("```"):
        response = response[3:]
    
    if response.endswith("```"):
        response = response[:-3]
    
    # Find JSON object boundaries
    start_idx = response.find("{")
    end_idx = response.rfind("}")
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        response = response[start_idx:end_idx + 1]
    
    # Clean common JSON issues
    response = response.strip()
    
    # Remove trailing commas before closing braces/brackets
    # Remove trailing commas before } or ]
    response = re.sub(r',(\s*[}\]])', r'\1', response)
    
    # Remove trailing commas at the end of lines
    response = re.sub(r',(\s*\n\s*[}\]])', r'\1', response)
    
    # Remove trailing commas in arrays
    response = re.sub(r',(\s*])', r']', response)
    
    # Fix common quote issues
    response = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1 "\2":', response)
    
    # Fix unquoted string values (basic fix)
    response = re.sub(r':\s*([a-zA-Z][a-zA-Z0-9\s]*?)(?=\s*[,}])', r': "\1"', response)
    
    return response.strip()


def safe_json_parse(response: str, fallback: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON response with multiple fallback strategies.
    
    Args:
        response: Raw response string from AI
        fallback: Fallback response if parsing fails
        
    Returns:
        Parsed JSON dict or None if all attempts fail
    """
    if not response:
        return fallback or {}
    
    # Strategy 1: Try direct parsing
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        logger.debug(f"Direct JSON parsing failed: {e}")
    
    # Strategy 2: Try cleaning and parsing
    try:
        cleaned = clean_json_response(response)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.debug(f"Cleaned JSON parsing failed: {e}")
    
    # Strategy 3: Try to extract valid JSON parts
    try:
        # Look for the most complete JSON object
        json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
        if json_objects:
            # Try the longest JSON object found
            longest_json = max(json_objects, key=len)
            cleaned_longest = clean_json_response(longest_json)
            return json.loads(cleaned_longest)
    except (json.JSONDecodeError, ValueError) as e:
        logger.debug(f"Partial JSON extraction failed: {e}")
    
    # Strategy 4: Try to fix common issues and parse
    try:
        # Remove any text before the first {
        start_idx = response.find('{')
        if start_idx != -1:
            response = response[start_idx:]
        
        # Remove any text after the last }
        end_idx = response.rfind('}')
        if end_idx != -1:
            response = response[:end_idx + 1]
        
        # Try to fix common syntax issues
        fixed_response = response.replace('None', 'null')
        fixed_response = fixed_response.replace('True', 'true')
        fixed_response = fixed_response.replace('False', 'false')
        
        return json.loads(fixed_response)
    except json.JSONDecodeError as e:
        logger.debug(f"Fixed JSON parsing failed: {e}")
    
    # All strategies failed
    logger.error(f"All JSON parsing strategies failed for response: {response[:200]}...")
    return fallback


def validate_json_structure(data: Dict[str, Any], required_fields: list = None) -> Dict[str, Any]:
    """
    Validate JSON structure and provide feedback on missing fields.
    
    Args:
        data: Parsed JSON data
        required_fields: List of required field names
        
    Returns:
        Validation result dict
    """
    if not isinstance(data, dict):
        return {
            "valid": False,
            "error": "Data is not a dictionary",
            "missing_fields": required_fields or []
        }
    
    if not required_fields:
        return {"valid": True, "missing_fields": []}
    
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    return {
        "valid": len(missing_fields) == 0,
        "missing_fields": missing_fields,
        "error": f"Missing required fields: {missing_fields}" if missing_fields else None
    } 