# api/openai_compat.py - OpenAI API compatibility layer for Mattermost integration
import logging
import time
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel, Field

from api.dependencies import get_chatbot, validate_openai_key
from core.utils import count_tokens

logger = logging.getLogger(__name__)

# Create API router WITHOUT a prefix - this is critical
# The Mattermost plugin expects the routes to be at the root level
router = APIRouter()

# Models for OpenAI compatible API
class ChatMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.3
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    user: Optional[str] = None

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage

class ModelObject(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "economic-chatbot"

class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[ModelObject]

@router.get("/v1/models")
async def list_models():
    """OpenAI-compatible models endpoint"""
    # Return hardcoded model information for compatibility
    current_time = int(time.time())
    
    return {
        "object": "list",
        "data": [
            {
                "id": "economic-chatbot",
                "object": "model",
                "created": current_time,
                "owned_by": "economic-chatbot"
            }
        ]
    }

@router.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    chatbot=Depends(get_chatbot),
    api_key: str = Depends(validate_openai_key)
):
    """OpenAI-compatible chat completions endpoint"""
    try:
        logger.info(f"Received chat completion request with {len(request.messages)} messages")
        
        # Extract the last user message (typically what Mattermost sends)
        last_user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                last_user_message = msg.content
                break
        
        if not last_user_message:
            logger.warning("No user message found in request")
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Format chat history for our chatbot
        chat_history = []
        for msg in request.messages:
            if msg.role in ["user", "assistant"]:
                chat_history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Remove the last user message from history (we'll send it as the question)
        # This avoids duplication as our API expects the current question separately
        if chat_history and chat_history[-1]["role"] == "user":
            chat_history = chat_history[:-1]
        
        # Generate answer using our existing chatbot
        logger.info(f"Generating answer for: {last_user_message[:50]}...")
        
        answer, sources = chatbot.generate_answer(
            question=last_user_message,
            chat_history=chat_history,
            session_id=request.user or "default"
        )
        
        # Format sources as a string if present
        if sources:
            source_text = "\n\nSources: " + ", ".join([s["source"] for s in sources])
            answer += source_text
        
        # Create OpenAI-compatible response
        current_time = int(time.time())
        
        # Estimate token counts for usage stats
        prompt_tokens = count_tokens(" ".join([msg.content for msg in request.messages]))
        completion_tokens = count_tokens(answer)
        
        # Strictly follow OpenAI response structure for maximum compatibility
        response = {
            "id": f"chatcmpl-{str(uuid.uuid4())[:8]}",
            "object": "chat.completion",
            "created": current_time,
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": answer
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        }
        
        logger.info("Successfully generated response")
        logger.debug(f"Response JSON: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error in OpenAI compatibility endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Add a root level health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "economic-chatbot"}

# Add both direct chat/completions endpoints to handle Mattermost's requests
@router.post("/chat/completions")
async def direct_chat_completions(
    request: Request,
    chatbot=Depends(get_chatbot),
    api_key: str = Depends(validate_openai_key)
):
    """Direct chat/completions endpoint for Mattermost"""
    try:
        logger.info("Received request to /chat/completions endpoint")
        
        # Parse request body manually to handle different request formats
        body = await request.json()
        
        # Convert request to our standard format
        standardized_request = ChatCompletionRequest(
            model=body.get("model", "economic-chatbot"),
            messages=[
                ChatMessage(
                    role=msg.get("role", "user"),
                    content=msg.get("content", "")
                )
                for msg in body.get("messages", [])
            ],
            temperature=body.get("temperature", 0.3),
            user=body.get("user", "default")
        )
        
        # Process the request using our standard endpoint
        return await chat_completions(standardized_request, chatbot, api_key)
        
    except Exception as e:
        logger.error(f"Error in direct chat completions endpoint: {e}", exc_info=True)
        # Return a more detailed error response that Mattermost can understand
        return {
            "error": {
                "message": str(e),
                "type": "server_error",
                "param": None,
                "code": 500
            }
        }