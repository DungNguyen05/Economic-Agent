# api/mattermost.py - Mattermost webhook integration handler
import logging
import json
from fastapi import APIRouter, Request, Depends, HTTPException, Form, Response
from typing import Optional, Dict, Any
from pydantic import BaseModel

from api.dependencies import get_chatbot, validate_openai_key

logger = logging.getLogger(__name__)

# Create API router for Mattermost integration
router = APIRouter()

def format_mattermost_response(answer, sources=None, user_name=None):
    """
    Format a response for Mattermost with Markdown support.
    
    Args:
        answer (str): The chatbot's answer
        sources (list): Optional list of source references
        user_name (str): Optional username to personalize the response
    
    Returns:
        str: Formatted response text
    """
    # Start with a personalized greeting if username is provided
    response = f"@{user_name}: " if user_name else ""
    
    # Add the main answer
    response += answer
    
    # Add sources if available
    if sources and len(sources) > 0:
        response += "\n\n**Sources:**\n"
        for i, source in enumerate(sources, 1):
            response += f"{i}. **{source['source']}**\n"
    
    return response


class MattermostWebhookRequest(BaseModel):
    """Model for Mattermost outgoing webhook request"""
    token: str
    team_id: str
    team_domain: str
    channel_id: str
    channel_name: str
    timestamp: int
    user_id: str
    user_name: str
    post_id: str
    text: str
    trigger_word: Optional[str] = None
    file_ids: Optional[str] = None

@router.post("/webhook/mattermost")
async def mattermost_webhook(
    request: Request,
    chatbot=Depends(get_chatbot)
):
    """
    Handle Mattermost outgoing webhook requests.
    
    This endpoint accepts form data from Mattermost outgoing webhooks
    and returns responses in the format Mattermost expects.
    """
    try:
        # Parse form data (Mattermost sends webhook data as form fields)
        form_data = await request.form()
        logger.info(f"Received Mattermost webhook with data: {form_data}")
        
        # Extract necessary information
        text = form_data.get("text", "")
        user_name = form_data.get("user_name", "unknown")
        trigger_word = form_data.get("trigger_word", "")
        
        # Remove trigger word from text (e.g., "@bot")
        if trigger_word and text.startswith(trigger_word):
            actual_question = text[len(trigger_word):].strip()
        else:
            actual_question = text.strip()
        
        logger.info(f"Processing question from {user_name}: {actual_question}")
        
        # Handle empty messages
        if not actual_question:
            return {"text": "I didn't receive a question. How can I help you?"}
        
        # Generate answer using the chatbot
        # Use a specific session_id for each user to maintain context
        session_id = f"mattermost_{form_data.get('user_id', 'default')}"
        answer, sources = chatbot.generate_answer(
            question=actual_question,
            chat_history=None,  # No chat history for now
            session_id=session_id
        )
        
        # Format response for Mattermost
        response_text = format_mattermost_response(
            answer=answer,
            sources=sources,
            user_name=user_name
        )
        
        # Add sources if available
        if sources:
            source_text = "\n\n**Sources**: " + ", ".join([s["source"] for s in sources])
            response_text += source_text
        
        # Return response in the format Mattermost expects
        return {"text": response_text}
    
    except Exception as e:
        logger.error(f"Error processing Mattermost webhook: {e}", exc_info=True)
        # Return a friendly error message
        return {"text": f"I encountered an error while processing your request. Please try again later."}