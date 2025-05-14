"""
NPC backstory system with hard-coded elements and dynamic generation.
"""

from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class BackstoryElementType(str, Enum):
    """Types of backstory elements."""
    ORIGIN = "origin"
    FAMILY = "family"
    EDUCATION = "education"
    CAREER = "career"
    TRAUMA = "trauma"
    ACHIEVEMENT = "achievement"
    RELATIONSHIP = "relationship"
    SECRET = "secret"
    GOAL = "goal"
    PERSONALITY = "personality"

class BackstoryElement(BaseModel):
    """Base backstory element model."""
    id: str
    type: BackstoryElementType
    content: Dict
    is_hardcoded: bool = Field(default=False)
    source: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)

class NPCBackstory(BaseModel):
    """Complete NPC backstory model."""
    npc_id: str
    elements: Dict[BackstoryElementType, List[BackstoryElement]] = Field(
        default_factory=lambda: {t: [] for t in BackstoryElementType}
    )
    hardcoded_elements: Set[str] = Field(default_factory=set)
    last_update: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)

    def add_element(self, element: BackstoryElement):
        """Add a new backstory element."""
        self.elements[element.type].append(element)
        if element.is_hardcoded:
            self.hardcoded_elements.add(element.id)
        self.last_update = datetime.utcnow()

    def remove_element(self, element_id: str) -> bool:
        """Remove a backstory element if it's not hardcoded."""
        for elements in self.elements.values():
            for i, element in enumerate(elements):
                if element.id == element_id and not element.is_hardcoded:
                    elements.pop(i)
                    self.last_update = datetime.utcnow()
                    return True
        return False

    def get_element(self, element_id: str) -> Optional[BackstoryElement]:
        """Get a backstory element by ID."""
        for elements in self.elements.values():
            for element in elements:
                if element.id == element_id:
                    return element
        return None

    def get_elements_by_type(self, element_type: BackstoryElementType) -> List[BackstoryElement]:
        """Get all elements of a specific type."""
        return self.elements.get(element_type, [])

    def get_hardcoded_elements(self) -> List[BackstoryElement]:
        """Get all hardcoded elements."""
        hardcoded = []
        for elements in self.elements.values():
            hardcoded.extend([e for e in elements if e.is_hardcoded])
        return hardcoded

    def generate_summary(self) -> Dict:
        """Generate a summary of the NPC's backstory."""
        summary = {
            "npc_id": self.npc_id,
            "version": self.version,
            "last_update": self.last_update.isoformat(),
            "elements": {}
        }
        
        for element_type, elements in self.elements.items():
            if elements:
                summary["elements"][element_type] = [
                    {
                        "id": e.id,
                        "content": e.content,
                        "is_hardcoded": e.is_hardcoded,
                        "confidence": e.confidence
                    }
                    for e in elements
                ]
        
        return summary

class BackstoryGenerator:
    """Generator for creating and evolving NPC backstories."""
    
    def __init__(self):
        self.hardcoded_templates = self._load_hardcoded_templates()
    
    def _load_hardcoded_templates(self) -> Dict[BackstoryElementType, List[Dict]]:
        """Load hardcoded backstory templates."""
        # This would load from a file or database
        return {
            BackstoryElementType.ORIGIN: [
                {"template": "Born in {location} to {parent_type} parents"},
                {"template": "Orphaned at a young age in {location}"}
            ],
            BackstoryElementType.TRAUMA: [
                {"template": "Witnessed {event} at age {age}"},
                {"template": "Lost {loved_one} to {cause}"}
            ]
            # Add more templates for other element types
        }
    
    def generate_backstory(self, npc_id: str, 
                         hardcoded_elements: List[Dict] = None) -> NPCBackstory:
        """Generate a new NPC backstory."""
        backstory = NPCBackstory(npc_id=npc_id)
        
        # Add hardcoded elements if provided
        if hardcoded_elements:
            for element_data in hardcoded_elements:
                element = BackstoryElement(
                    id=f"hardcoded_{len(backstory.hardcoded_elements)}",
                    type=element_data["type"],
                    content=element_data["content"],
                    is_hardcoded=True,
                    source="hardcoded"
                )
                backstory.add_element(element)
        
        # Generate additional elements based on hardcoded ones
        self._generate_related_elements(backstory)
        
        return backstory
    
    def _generate_related_elements(self, backstory: NPCBackstory):
        """Generate elements related to existing ones."""
        # This would use GPT to generate related elements
        # For now, just add some placeholder elements
        for element_type in BackstoryElementType:
            if not backstory.get_elements_by_type(element_type):
                element = BackstoryElement(
                    id=f"generated_{element_type}_{len(backstory.elements[element_type])}",
                    type=element_type,
                    content={"placeholder": True},
                    source="generated"
                )
                backstory.add_element(element)
    
    def evolve_backstory(self, backstory: NPCBackstory) -> NPCBackstory:
        """Evolve an existing backstory."""
        # Create a new version
        evolved = NPCBackstory(
            npc_id=backstory.npc_id,
            version=backstory.version + 1
        )
        
        # Copy hardcoded elements
        for element in backstory.get_hardcoded_elements():
            evolved.add_element(element)
        
        # Evolve non-hardcoded elements
        for element_type, elements in backstory.elements.items():
            for element in elements:
                if not element.is_hardcoded:
                    evolved_element = self._evolve_element(element)
                    evolved.add_element(evolved_element)
        
        return evolved
    
    def _evolve_element(self, element: BackstoryElement) -> BackstoryElement:
        """Evolve a single backstory element."""
        # This would use GPT to evolve the element
        # For now, just add an evolved tag
        evolved = element.model_copy()
        evolved.id = f"{element.id}_evolved"
        evolved.tags.append("evolved")
        return evolved 