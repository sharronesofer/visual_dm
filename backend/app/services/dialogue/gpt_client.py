import asyncio
import time
import math
from typing import Dict, List, Optional, Any, TypedDict, AsyncIterator
from datetime import datetime
import aiohttp
import json
import logging
from pyee import EventEmitter

logger = logging.getLogger(__name__)

class GPTConfig(TypedDict, total=False):
    """Configuration for GPT API requests."""
    model: str
    temperature: Optional[float]
    maxTokens: Optional[int]
    stop: Optional[List[str]]

class GPTResponse(TypedDict, total=False):
    """Response from GPT API with generated text and usage statistics."""
    text: str
    usage: Optional[Dict[str, int]]
    raw: Optional[Any]
    error: Optional[str]

class GPTClientOptions(TypedDict, total=False):
    """Configuration options for GPTClient."""
    apiKey: str
    apiUrl: Optional[str]
    rateLimit: Optional[int]
    timeoutMs: Optional[int]
    maxRetries: Optional[int]
    backoffBaseMs: Optional[int]

class GPTUsageStats(TypedDict):
    """Usage statistics for token consumption."""
    totalTokens: int
    rollingTokens: int
    windowMs: int
    lastReset: int

class GPTClient(EventEmitter):
    """
    GPTClient: Handles GPT/OpenAI API requests, prompt/context management, 
    and emotion context formatting for LLMs.
    Emits events for request, error, and fallback. Provides static helpers for prompt injection.
    """
    
    def __init__(self, options: GPTClientOptions):
        """Initialize the GPTClient with API configuration."""
        super().__init__()
        self.api_key = options['apiKey']
        self.api_url = options.get('apiUrl', 'https://api.openai.com/v1/chat/completions')
        self.rate_limit = options.get('rateLimit', 60)
        self.timeout_ms = options.get('timeoutMs', 10000)
        self.max_retries = options.get('maxRetries', 3)
        self.backoff_base_ms = options.get('backoffBaseMs', 500)
        self.requests = []  # Timestamps of recent requests for rate limiting
        self.usage_window_ms = 60000  # 1 minute window
        self.usage_stats = {
            'totalTokens': 0,
            'rollingTokens': 0,
            'windowMs': self.usage_window_ms,
            'lastReset': int(time.time() * 1000)
        }
        
        # Headers for API requests
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    async def generate_completion(self, prompt: str, context: List[str], config: GPTConfig) -> GPTResponse:
        """
        Generates a GPT completion given a prompt and context.
        Emits 'request', 'error', and 'fallback' events.
        """
        await self._enforce_rate_limit()
        messages = [
            {'role': 'system', 'content': c} for c in context
        ]
        messages.append({'role': 'user', 'content': prompt})
        
        # Prepare API payload
        payload = {
            **config,
            'messages': messages,
            'temperature': config.get('temperature', 0.7),
            'max_tokens': config.get('maxTokens', 512),
        }
        if 'stop' in config and config['stop']:
            payload['stop'] = config['stop']
            
        self.emit('request', {'prompt': prompt, 'context': context, 'config': payload})
        
        # Attempt API request with retry logic
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout_ms / 1000  # aiohttp uses seconds
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=error_text,
                            headers=response.headers
                        )
                    
                    data = await response.json()
                    choice = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    if 'usage' in data:
                        self._update_usage(data['usage'].get('total_tokens'))
                    
                    return {
                        'text': choice,
                        'usage': data.get('usage'),
                        'raw': data
                    }
        except Exception as error:
            self.emit('error', error)
            logger.error(f"GPT API error: {str(error)}")
            
            # Retry logic with exponential backoff
            for attempt in range(1, self.max_retries + 1):
                try:
                    await asyncio.sleep(2 ** attempt * self.backoff_base_ms / 1000)
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            self.api_url,
                            headers=self.headers,
                            json=payload,
                            timeout=self.timeout_ms / 1000
                        ) as response:
                            if response.status != 200:
                                continue
                                
                            data = await response.json()
                            choice = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                            if 'usage' in data:
                                self._update_usage(data['usage'].get('total_tokens'))
                            
                            return {
                                'text': choice,
                                'usage': data.get('usage'),
                                'raw': data
                            }
                except Exception as retry_error:
                    if attempt == self.max_retries:
                        self.emit('fallback', retry_error)
                        logger.error(f"All retry attempts failed: {str(retry_error)}")
                        return {'text': '', 'error': str(retry_error)}
            
            return {'text': '', 'error': str(error)}
    
    async def _enforce_rate_limit(self):
        """Enforces the rate limit by delaying if necessary."""
        now = int(time.time() * 1000)
        # Filter out requests older than 1 minute
        self.requests = [t for t in self.requests if now - t < 60000]
        
        if len(self.requests) >= self.rate_limit:
            # Wait until we're allowed to make another request
            wait_time = 60000 - (now - self.requests[0])
            await asyncio.sleep(wait_time / 1000)  # Convert to seconds
        
        self.requests.append(int(time.time() * 1000))
    
    def _update_usage(self, tokens: Optional[int]):
        """Updates token usage statistics."""
        now = int(time.time() * 1000)
        if now - self.usage_stats['lastReset'] > self.usage_window_ms:
            self.usage_stats['rollingTokens'] = 0
            self.usage_stats['lastReset'] = now
        
        if tokens:
            self.usage_stats['totalTokens'] += tokens
            self.usage_stats['rollingTokens'] += tokens
    
    def get_usage_stats(self) -> GPTUsageStats:
        """Returns current usage statistics."""
        return dict(self.usage_stats)
    
    @staticmethod
    async def sleep(ms: int):
        """Utility to sleep for ms milliseconds."""
        await asyncio.sleep(ms / 1000)
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """Counts tokens in a string (approximate, for OpenAI models)."""
        # Simple approximation: 1 token ≈ 4 characters (for English)
        return math.ceil(len(text) / 4)
    
    @staticmethod
    def format_emotion_context_for_prompt(emotions: List[Dict[str, Any]]) -> str:
        """
        Formats emotion context for prompt injection.
        @param emotions Array of emotion objects with name, intensity, and optional description
        @returns String for prompt injection
        """
        if not emotions:
            return 'No emotions are currently active.'
        
        formatted_emotions = []
        for emotion in emotions:
            emotion_str = f"{emotion['name']} (intensity: {emotion['intensity']}"
            if 'description' in emotion and emotion['description']:
                emotion_str += f", {emotion['description']}"
            emotion_str += ")"
            formatted_emotions.append(emotion_str)
        
        return 'Current emotions: ' + ', '.join(formatted_emotions) 