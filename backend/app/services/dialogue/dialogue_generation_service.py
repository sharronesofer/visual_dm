import logging
from typing import List, Dict, Any, Optional
import time
from .gpt_client import GPTClient, GPTConfig, GPTResponse

logger = logging.getLogger(__name__)

class DialogueGenerationService:
    """
    DialogueGenerationService provides a high-level interface for generating dialogue using GPTClient.
    Handles prompt formatting, context, error propagation, and logging.
    """
    
    def __init__(self, gpt_client: GPTClient, default_config: GPTConfig):
        """
        Initialize the service with a GPTClient and default configuration.
        
        Args:
            gpt_client: An initialized GPTClient for API communication
            default_config: Default configuration for GPT requests
        """
        self.gpt_client = gpt_client
        self.default_config = default_config
    
    async def generate_dialogue(
        self, 
        prompt: str, 
        context: List[str] = None, 
        config: Optional[Dict[str, Any]] = None
    ) -> GPTResponse:
        """
        Generates dialogue text given a prompt and context.
        
        Args:
            prompt: The main prompt string.
            context: Array of previous conversation strings.
            config: Optional GPTConfig overrides.
            
        Returns:
            GPTResponse with generated text or error information
        """
        if context is None:
            context = []
            
        # Merge default config with any overrides
        merged_config = {**self.default_config}
        if config:
            merged_config.update(config)
        
        start_time = time.time()
        
        try:
            response = await self.gpt_client.generate_completion(prompt, context, merged_config)
            
            if 'error' in response and response['error']:
                self._log_error(
                    'GPT API Error', 
                    response['error'], 
                    {'prompt': prompt, 'context': context, 'config': merged_config}
                )
            
            return response
        except Exception as err:
            error_message = str(err)
            self._log_error(
                'DialogueGenerationService Exception',
                error_message,
                {'prompt': prompt, 'context': context, 'config': merged_config}
            )
            return {'text': '', 'error': error_message}
    
    def _log_error(self, message: str, error: str, meta: Dict[str, Any]):
        """
        Logs errors for debugging and monitoring.
        
        Args:
            message: Error context message
            error: The error string
            meta: Additional metadata about the error context
        """
        logger.error(f"[DialogueGenerationService] {message}: {error}", extra=meta) 