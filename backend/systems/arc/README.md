# 🎯 Enhanced Arc System

> **Enterprise-grade narrative arc management system with advanced relationship modeling, LLM integration, and comprehensive progression tracking**

## 🚀 Quick Start

### Prerequisites
- PostgreSQL 12+
- Python 3.9+
- Anthropic Claude API access (for LLM features)
- Development Bible compliance knowledge

### Basic Usage

```python
from backend.systems.arc.models.arc import ArcModel, ArcType, ArcPriority
from backend.systems.arc.business_rules import validate_arc_business_rules
from backend.systems.arc.services.arc_relationship_service import ArcRelationshipService

# Create a new arc
arc = ArcModel(
    title="The Shadow War",
    description="Ancient forces awaken to threaten the realm",
    arc_type=ArcType.GLOBAL,
    priority=ArcPriority.HIGH,
    faction_ids=["shadow_syndicate", "light_covenant"],
    difficulty_level=8,
    estimated_duration_hours=45
)

# Validate business rules
violations = validate_arc_business_rules(arc.dict())
if violations:
    print(f"Business rule violations: {violations}")

# Create relationships
relationship_service = ArcRelationshipService()
relationship_service.create_relationship(
    source_arc_id=arc.id,
    target_arc_id=previous_arc.id,
    relationship_type="SEQUEL",
    influence_level="MAJOR"
)
```

---

## 📊 Features Overview

### ✅ **Development Bible Compliant**
- **Enum Alignment**: All enums match Bible specifications (GLOBAL, REGIONAL, CHARACTER, NPC, FACTION, QUEST)
- **Model Structure**: Complete field coverage as per Bible requirements
- **Business Rules**: Comprehensive validation and constraint checking
- **Cross-System Integration**: Proper referencing to Character, NPC, Faction, and Region systems

### 🔗 **Advanced Relationship System**
- **8 Relationship Types**: SEQUEL, PREQUEL, PARALLEL, BRANCHING, CONFLUENCE, THEMATIC_LINK, CONTINUATION, CONSEQUENCE
- **Influence Levels**: MINIMAL, MODERATE, MAJOR, CRITICAL
- **LLM Integration**: AI-powered follow-up arc generation
- **Network Analysis**: Circular dependency detection and relationship validation

### 📈 **Comprehensive Progress Tracking**
- **Milestone System**: 8+ milestone types with automatic detection
- **Predictive Analytics**: Completion confidence scoring and risk assessment
- **Engagement Patterns**: Velocity tracking and break analysis
- **Achievement System**: Dynamic milestone recognition and formatting

### 🤖 **LLM-Powered Features**
- **Follow-up Generation**: Structured prompts for next arc suggestions
- **Relationship Suggestions**: AI analysis of thematic and character overlaps
- **Quality Analysis**: Narrative text validation and improvement suggestions

---

## 🗂️ System Architecture

```
backend/systems/arc/
├── models/
│   ├── arc.py                    # Core Arc model with relationships
│   ├── arc_step.py              # Enhanced step model with validation
│   └── arc_progression.py       # Progress tracking models
├── services/
│   ├── arc_relationship_service.py  # Relationship management
│   ├── progression_tracker.py       # Advanced progress analytics
│   └── arc_generator.py            # Arc creation and management
├── business_rules.py            # Comprehensive validation logic
├── tests/
│   └── test_integration_compliance.py  # Full system tests
└── scripts/
    └── validate_bible_compliance.py    # Compliance validator
```

---

## 🔧 API Examples

### Create Arc with Relationships
```python
POST /api/arcs
{
  "title": "The Fallen Kingdom",
  "description": "Reclaim the lost throne from usurpers",
  "arc_type": "regional",
  "region_id": "eastern_kingdoms",
  "faction_ids": ["royal_guard", "rebellion"],
  "predecessor_arcs": [
    {
      "arc_id": "uuid-of-predecessor",
      "relationship_type": "PREQUEL",
      "influence_level": "MAJOR"
    }
  ],
  "difficulty_level": 7,
  "estimated_duration_hours": 25
}
```

### Query Arc Relationships
```python
GET /api/arcs/{arc_id}/relationships
Response:
{
  "predecessor_arcs": [...],
  "successor_arcs": [...],
  "related_arcs": [...],
  "relationship_complexity": 0.75,
  "suggested_follow_ups": [...]
}
```

### Get Progress Analytics
```python
GET /api/arcs/{arc_id}/progress
Response:
{
  "completion_percentage": 67.5,
  "milestones_achieved": [
    {
      "type": "half_complete",
      "achieved_at": "2024-01-15T10:30:00Z",
      "description": "Reached the halfway point"
    }
  ],
  "engagement_metrics": {
    "average_session_length": 45,
    "completion_confidence": 0.87,
    "velocity_trend": "increasing"
  },
  "risk_assessment": {
    "abandonment_risk": "low",
    "factors": ["steady_progress", "high_engagement"]
  }
}
```

---

## 🛠️ Development Workflow

### 1. **Compliance Validation**
Always run compliance checks before committing:
```bash
python backend/systems/arc/scripts/validate_bible_compliance.py
```
Target: 95%+ compliance score with zero critical issues.

### 2. **Testing Strategy**
```bash
# Run all arc system tests
pytest backend/systems/arc/tests/ -v --cov=backend.systems.arc

# Integration compliance tests
pytest backend/systems/arc/tests/test_integration_compliance.py -v

# Business rule validation
python -c "
from backend.systems.arc.business_rules import validate_arc_business_rules
violations = validate_arc_business_rules({'arc_type': 'global', 'priority': 'high'})
print(f'Violations: {violations}')
"
```

### 3. **Mock Data Usage**
Use compliant mock data for development:
```python
import json

# Load compliant arc data
with open('data/public/mocks/arc/arc.json') as f:
    arc_data = json.load(f)

# All mock data uses correct enums (GLOBAL, REGIONAL, etc.)
print(f"Arc type: {arc_data['arc_type']}")  # Will be valid enum
```

---

## 🔍 Business Rules Reference

### **Arc Type Requirements**
- **GLOBAL**: Must have `faction_ids`, `world_impact` = "world-changing"
- **REGIONAL**: Must have `region_id`, regional scope
- **CHARACTER**: Must have `character_id`, personal focus
- **NPC**: Must have `npc_id`, NPC-centered narrative
- **FACTION**: Must have `faction_ids`, faction-focused storyline
- **QUEST**: Must have quest objectives and completion criteria

### **Validation Rules**
```python
# Narrative quality requirements
- Minimum 50 characters for descriptions
- No prohibited content (violence thresholds, etc.)
- Proper grammar and structure

# Step progression rules
- Prerequisites must be completed before activation
- Completion criteria must be well-defined
- Rewards must be balanced and appropriate

# Relationship constraints
- No circular dependencies in arc chains
- Influence levels must match relationship types
- Maximum 5 direct relationships per arc
```

---

## 🎨 Frontend Integration

### **Arc Visualization**
```javascript
// Display arc relationships
const ArcRelationshipGraph = ({ arcId }) => {
  const [relationships, setRelationships] = useState([]);
  
  useEffect(() => {
    fetch(`/api/arcs/${arcId}/relationships`)
      .then(res => res.json())
      .then(data => setRelationships(data));
  }, [arcId]);
  
  return (
    <div className="arc-network">
      {relationships.predecessor_arcs.map(rel => (
        <ArcNode key={rel.arc_id} 
                relationship={rel} 
                type="predecessor" />
      ))}
    </div>
  );
};
```

### **Progress Dashboard**
```javascript
// Progress tracking component
const ArcProgressDashboard = ({ arcId }) => {
  const [progress, setProgress] = useState(null);
  
  const getProgressData = async () => {
    const response = await fetch(`/api/arcs/${arcId}/progress`);
    const data = await response.json();
    setProgress(data);
  };
  
  return (
    <div className="progress-dashboard">
      <ProgressBar percentage={progress?.completion_percentage} />
      <MilestonesList milestones={progress?.milestones_achieved} />
      <RiskIndicator risk={progress?.risk_assessment} />
    </div>
  );
};
```

---

## 🔧 Configuration

### **Environment Variables**
```bash
# Required for LLM features
ANTHROPIC_API_KEY=your_claude_api_key

# Optional customization
ARC_MAX_RELATIONSHIPS=5
ARC_COMPLEXITY_THRESHOLD=7.5
ENABLE_ARC_ANALYTICS=true
LLM_MODEL_VERSION=claude-3-sonnet-20240229
```

### **Database Configuration**
```sql
-- Enable JSONB indexing for better performance
CREATE INDEX idx_arc_entities_predecessor_arcs ON arc_entities USING GIN(predecessor_arcs);
CREATE INDEX idx_arc_entities_faction_ids ON arc_entities USING GIN(faction_ids);
CREATE INDEX idx_arc_relationships_type ON arc_relationships(relationship_type);
```

---

## 📚 Advanced Features

### **LLM-Powered Arc Generation**
```python
from backend.systems.arc.services.arc_relationship_service import ArcRelationshipService

service = ArcRelationshipService()

# Generate follow-up arcs based on completion
follow_ups = await service.generate_follow_up_arcs(
    completed_arc_id="uuid-of-completed-arc",
    context="Player chose the diplomatic path",
    count=3
)

for arc_suggestion in follow_ups:
    print(f"Suggested: {arc_suggestion['title']}")
    print(f"Reason: {arc_suggestion['generation_rationale']}")
```

### **Complex Relationship Analysis**
```python
from backend.systems.arc.services.arc_relationship_service import ArcRelationshipService

service = ArcRelationshipService()

# Analyze narrative chains
chains = service.identify_narrative_chains(starting_arc_id="uuid")
print(f"Found {len(chains)} narrative paths")

# Detect circular dependencies
cycles = service.detect_circular_dependencies()
if cycles:
    print(f"Warning: Circular dependencies detected: {cycles}")

# Get relationship suggestions
suggestions = service.suggest_relationships(arc_id="uuid")
print(f"Recommended relationships: {[s['target_title'] for s in suggestions]}")
```

### **Advanced Analytics**
```python
from backend.systems.arc.services.progression_tracker import ProgressionTracker

tracker = ProgressionTracker()

# Comprehensive metrics
metrics = tracker.calculate_comprehensive_metrics(arc_data, steps_data)
print(f"Completion confidence: {metrics['completion_confidence']}")
print(f"Engagement score: {metrics['engagement_score']}")

# Predictive insights
insights = tracker.generate_progress_insights(metrics)
for insight in insights['recommendations']:
    print(f"📊 {insight}")
```

---

## ⚠️ Important Notes

### **Compliance Requirements**
1. **Always validate business rules** before saving arc data
2. **Use correct enum values** (GLOBAL, REGIONAL, etc. - not PRIMARY, SECONDARY)
3. **Include cross-system references** (character_id, faction_ids, etc.) where applicable
4. **Test relationship logic** to avoid circular dependencies

### **Performance Considerations**
- Relationship queries are optimized with JSONB indexing
- LLM calls are rate-limited and cached where possible
- Complex network analysis should be run asynchronously
- Consider pagination for large arc lists

### **Security Notes**
- Validate all input against business rules
- Sanitize narrative text for XSS prevention
- Rate limit LLM API calls per user
- Log all relationship modifications for audit trails

---

## 🚀 Getting Started Checklist

- [ ] **Read Development Bible** - Understand arc system requirements
- [ ] **Set up environment** - Configure database and API keys
- [ ] **Run compliance validator** - Ensure 95%+ compliance score
- [ ] **Execute integration tests** - Verify all functionality works
- [ ] **Review mock data** - Understand compliant data structures
- [ ] **Test API endpoints** - Familiarize with request/response formats
- [ ] **Deploy to staging** - Follow deployment checklist
- [ ] **Monitor performance** - Validate metrics and error rates

---

## 📞 Support & Documentation

- **Development Bible**: Primary source of truth for arc requirements
- **API Documentation**: `/docs/api/arc-system.md`
- **Database Schema**: `/docs/database/arc-schema.md`
- **Deployment Guide**: `DEPLOYMENT_CHECKLIST.md`
- **Business Rules**: See `business_rules.py` for complete validation logic

**For issues or questions**: Create a ticket with the Arc System team 