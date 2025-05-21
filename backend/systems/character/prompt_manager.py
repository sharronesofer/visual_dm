from typing import Dict

class RumorPromptManager:
    """Manages prompt templates and variable substitution for rumor transformation."""
    BASE_TEMPLATE = (
        "Given the following event: '{event}', and the current rumor: '{rumor}', "
        "transform the rumor as it might be retold by an NPC with the following traits: {traits}. "
        "Apply a distortion level of {distortion_level} (0=truthful, 1=wildly distorted). "
        "Preserve the main theme, but allow for natural rumor evolution. "
        "Output only the new rumor text."
    )

    @staticmethod
    def build_prompt(event: str, rumor: str, traits: str, distortion_level: float) -> str:
        return RumorPromptManager.BASE_TEMPLATE.format(
            event=event,
            rumor=rumor,
            traits=traits,
            distortion_level=distortion_level
        ) 
