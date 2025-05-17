import json
import asyncio
import time
from typing import Dict, List, Any, Optional, TypedDict, Union
import aiohttp
from events import EventEmitter

class GPTConfig(TypedDict, total=False):
    model: str
    temperature: float
    max_tokens: int
    stop: List[str]

class GPTUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class GPTResponse(TypedDict):
    text: str
    usage: Optional[GPTUsage]
    raw: Optional[Any]
    error: Optional[str]

class GPTClientOptions(TypedDict, total=False):
    api_key: str
    api_url: str
    rate_limit: int
    timeout_ms: int
    max_retries: int
    backoff_base_ms: int

class GPTUsageStats(TypedDict):
    total_tokens: int
    rolling_tokens: int
    window_ms: int
    last_reset: float

class GPTClient:
    """
    GPTClient: Handles GPT/OpenAI API requests, prompt/context management, and emotion context formatting for LLMs.
    Emits events for request, error, and fallback. Provides static helpers for prompt injection.
    """
    
    def __init__(self, options: GPTClientOptions):
        self.api_key = options['api_key']
        self.api_url = options.get('api_url', 'https://api.openai.com/v1/chat/completions')
        self.rate_limit = options.get('rate_limit', 60)
        self.timeout_ms = options.get('timeout_ms', 10000)
        self.max_retries = options.get('max_retries', 3)
        self.backoff_base_ms = options.get('backoff_base_ms', 500)
        self.requests: List[float] = []
        self.usage_window_ms = 60000
        self.usage_stats: GPTUsageStats = {
            'total_tokens': 0,
            'rolling_tokens': 0,
            'window_ms': self.usage_window_ms,
            'last_reset': time.time() * 1000
        }
        self.event_emitter = EventEmitter()
    
    def on(self, event: str, handler):
        """Register an event handler"""
        self.event_emitter.on(event, handler)
    
    def off(self, event: str, handler):
        """Unregister an event handler"""
        self.event_emitter.off(event, handler)
    
    def emit(self, event: str, *args, **kwargs):
        """Emit an event"""
        self.event_emitter.emit(event, *args, **kwargs)
    
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
        
        payload = {
            **config,
            'messages': messages,
            'temperature': config.get('temperature', 0.7),
            'max_tokens': config.get('max_tokens', 512),
            'stop': config.get('stop', None)
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        self.emit('request', {'prompt': prompt, 'context': context, 'config': payload})
        
        try:
            # Initial request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout_ms / 1000  # aiohttp uses seconds
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API Error: {response.status} {error_text}")
                    
                    data = await response.json()
                    choice = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    self._update_usage(data.get('usage', {}).get('total_tokens'))
                    
                    return {
                        'text': choice,
                        'usage': data.get('usage'),
                        'raw': data,
                        'error': None
                    }
        
        except Exception as error:
            self.emit('error', error)
            
            # Fallback logic: retry with exponential backoff up to max_retries
            for attempt in range(1, self.max_retries + 1):
                await self._sleep(2 ** attempt * self.backoff_base_ms)
                
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            self.api_url,
                            headers=headers,
                            json=payload,
                            timeout=self.timeout_ms / 1000
                        ) as response:
                            if response.status != 200:
                                error_text = await response.text()
                                raise Exception(f"API Error: {response.status} {error_text}")
                            
                            data = await response.json()
                            choice = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                            self._update_usage(data.get('usage', {}).get('total_tokens'))
                            
                            return {
                                'text': choice,
                                'usage': data.get('usage'),
                                'raw': data,
                                'error': None
                            }
                
                except Exception as err:
                    if attempt == self.max_retries:
                        self.emit('fallback', err)
                        return {'text': '', 'error': str(err), 'raw': None, 'usage': None}
            
            return {'text': '', 'error': str(error), 'raw': None, 'usage': None}
    
    async def _enforce_rate_limit(self):
        """Enforces the rate limit by delaying if necessary."""
        now = time.time() * 1000
        self.requests = [t for t in self.requests if now - t < 60000]
        
        if len(self.requests) >= self.rate_limit:
            wait = 60000 - (now - self.requests[0])
            await self._sleep(wait)
        
        self.requests.append(now)
    
    def _update_usage(self, tokens: Optional[int]):
        """Updates token usage statistics."""
        now = time.time() * 1000
        
        if now - self.usage_stats['last_reset'] > self.usage_window_ms:
            self.usage_stats['rolling_tokens'] = 0
            self.usage_stats['last_reset'] = now
        
        if tokens:
            self.usage_stats['total_tokens'] += tokens
            self.usage_stats['rolling_tokens'] += tokens
    
    def get_usage_stats(self) -> GPTUsageStats:
        """Returns current usage statistics."""
        return self.usage_stats.copy()
    
    @staticmethod
    async def _sleep(ms: float):
        """Utility to sleep for ms milliseconds."""
        await asyncio.sleep(ms / 1000)
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """Counts tokens in a string (approximate, for OpenAI models)."""
        # Simple approximation: 1 token ≈ 4 characters (for English)
        return int((len(text) + 3) / 4)
    
    @staticmethod
    def format_emotion_context_for_prompt(emotions: List[Dict[str, Any]]) -> str:
        """
        Formats emotion context for prompt injection.
        
        Args:
            emotions: Array of emotion objects with name, intensity, and optional description
            
        Returns:
            String for prompt injection, e.g., 'Current emotions: joy (intensity: 0.8), anger (intensity: 0.5)'
        """
        if not emotions:
            return 'No emotions are currently active.'
        
        formatted_emotions = []
        for e in emotions:
            desc = f", {e.get('description')}" if e.get('description') else ''
            formatted_emotions.append(f"{e['name']} (intensity: {e['intensity']}{desc})")
        
        return 'Current emotions: ' + ', '.join(formatted_emotions) 