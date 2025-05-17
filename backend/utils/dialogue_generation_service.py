import logging
from typing import List, Optional, Dict, Any, TypedDict
from backend.utils.gpt_client import GPTClient, GPTConfig, GPTResponse

logger = logging.getLogger('dialogue_generation')

class DialogueGenerationService:
    """
    DialogueGenerationService provides a high-level interface for generating dialogue using GPTClient.
    Handles prompt formatting, context, error propagation, and logging.
    """
    
    def __init__(self, gpt_client: GPTClient, default_config: GPTConfig):
        """
        Initialize the DialogueGenerationService.
        
        Args:
            gpt_client: An instance of GPTClient to use for generating completions
            default_config: Default configuration for GPT requests
        """
        self.gpt_client = gpt_client
        self.default_config = default_config
    
    async def generate_dialogue(self, prompt: str, context: List[str] = None, config: Optional[Dict[str, Any]] = None) -> GPTResponse:
        """
        Generates dialogue text given a prompt and context.
        
        Args:
            prompt: The main prompt string
            context: Array of previous conversation strings
            config: Optional GPTConfig overrides
            
        Returns:
            A GPTResponse containing the generated text or error information
        """
        context = context or []
        merged_config = {**self.default_config, **(config or {})}
        
        try:
            response = await self.gpt_client.generate_completion(prompt, context, merged_config)
            
            if response.get('error'):
                self._log_error('GPT API Error', response['error'], {
                    'prompt': prompt,
                    'context': context,
                    'config': merged_config
                })
            
            return response
        
        except Exception as err:
            self._log_error('DialogueGenerationService Exception', str(err), {
                'prompt': prompt,
                'context': context,
                'config': merged_config
            })
            
            return {
                'text': '',
                'error': str(err),
                'raw': err,
                'usage': None
            }
    
    def _log_error(self, message: str, error: str, meta: Any):
        """
        Logs errors for debugging and monitoring.
        
        Args:
            message: Error message summary
            error: Detailed error message
            meta: Additional metadata about the request
        """
        logger.error(f"[DialogueGenerationService] {message}: {error}", extra={'meta': meta}) 