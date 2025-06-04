# Arc System Enhancement Deployment Checklist

## 📋 Pre-Deployment Validation

### 🔍 **Phase 1: Compliance Verification**
- [ ] **Run Compliance Validator**
  ```bash
  python backend/systems/arc/scripts/validate_bible_compliance.py
  ```
  - Target: 95%+ compliance score
  - Zero critical failures
  - Address all high-priority issues

- [ ] **Execute Integration Tests**
  ```bash
  pytest backend/systems/arc/tests/test_integration_compliance.py -v
  ```
  - All tests passing
  - Coverage > 90%

- [ ] **Validate Mock Data**
  - [ ] All JSON files use correct enums (GLOBAL, REGIONAL, etc.)
  - [ ] Arc templates match new structure
  - [ ] Test data includes relationship fields

### 🗄️ **Phase 2: Database Migration**
- [ ] **Run Migration Script**
  ```sql
  -- Execute: backend/systems/arc/migrations/add_arc_enhancements.sql
  ```
  - [ ] New fields added to `arc_entities`
  - [ ] `arc_relationships` table created
  - [ ] `arc_milestones` table created
  - [ ] Indexes and constraints applied
  - [ ] Triggers functioning correctly

- [ ] **Validate Migration**
  ```sql
  SELECT * FROM information_schema.columns 
  WHERE table_name = 'arc_entities' 
  AND column_name IN ('predecessor_arcs', 'successor_arcs', 'related_arcs');
  ```

- [ ] **Test Data Insertion**
  ```sql
  INSERT INTO arc_entities (title, arc_type, predecessor_arcs, outcome_influences) 
  VALUES ('Test Arc', 'regional', '[]', '{}');
  ```

### 🔧 **Phase 3: API Integration**
- [ ] **Update API Endpoints**
  - [ ] Arc creation accepts new relationship fields
  - [ ] Arc retrieval includes relationship data
  - [ ] Relationship management endpoints
  - [ ] Progression tracking endpoints

- [ ] **Test API Responses**
  ```bash
  # Test arc creation with relationships
  curl -X POST /api/arcs -d '{
    "title": "Test Arc",
    "arc_type": "regional",
    "predecessor_arcs": [],
    "outcome_influences": {}
  }'
  ```

---

## 🚀 Deployment Steps

### **Step 1: Code Deployment**
- [ ] **Deploy Enhanced Models**
  - [ ] `backend/systems/arc/models/arc.py` ✅
  - [ ] `backend/systems/arc/models/arc_step.py` ✅
  - [ ] New relationship enums and fields

- [ ] **Deploy Business Logic**
  - [ ] `backend/systems/arc/business_rules.py` ✅
  - [ ] Enhanced validation functions
  - [ ] Complexity calculation logic

- [ ] **Deploy Services**
  - [ ] `backend/systems/arc/services/arc_relationship_service.py` ✅
  - [ ] `backend/systems/arc/services/progression_tracker.py` ✅
  - [ ] LLM integration capabilities

### **Step 2: Database Updates**
- [ ] **Execute Migration (Non-Production First)**
  ```bash
  psql -d development_db -f backend/systems/arc/migrations/add_arc_enhancements.sql
  ```

- [ ] **Verify Schema Changes**
  ```sql
  \d arc_entities
  \d arc_relationships 
  \d arc_milestones
  ```

- [ ] **Test Database Functions**
  ```sql
  SELECT validate_arc_business_rules('{"arc_type": "global", "priority": "high"}');
  ```

### **Step 3: Data Migration & Validation**
- [ ] **Update Existing Arc Data**
  ```sql
  UPDATE arc_entities 
  SET predecessor_arcs = '[]', 
      successor_arcs = '[]', 
      related_arcs = '[]',
      outcome_influences = '{}'
  WHERE predecessor_arcs IS NULL;
  ```

- [ ] **Validate Business Rules on Existing Data**
  ```sql
  SELECT id, title, validate_arc_business_rules(row_to_json(arc_entities.*))
  FROM arc_entities 
  WHERE jsonb_array_length(validate_arc_business_rules(row_to_json(arc_entities.*))) > 0;
  ```

### **Step 4: Mock Data Updates**
- [ ] **Update Test Data Files**
  - [ ] `data/public/mocks/arc/arc.json` ✅
  - [ ] `data/public/mocks/arc/arc_steps.json` ✅  
  - [ ] `data/public/mocks/arc/arcs_list.json` ✅
  - [ ] `data/public/templates/arc/arc_templates.json` ✅

- [ ] **Verify JSON Schema Compliance**
  ```bash
  python -m json.tool data/public/mocks/arc/arc.json
  ```

---

## 🔍 Post-Deployment Validation

### **Testing Phase**
- [ ] **Functional Testing**
  - [ ] Create new arc with relationships
  - [ ] Test business rule validation
  - [ ] Verify step progression logic
  - [ ] Test complexity analysis

- [ ] **Integration Testing**
  - [ ] Arc-to-arc relationships
  - [ ] Cross-system field validation
  - [ ] LLM prompt generation
  - [ ] Progression milestone tracking

- [ ] **Performance Testing**
  - [ ] Database query performance
  - [ ] Relationship network analysis
  - [ ] Large dataset handling

### **Monitoring & Validation**
- [ ] **Error Monitoring**
  - [ ] No critical errors in logs
  - [ ] Business rule violations tracked
  - [ ] Performance metrics within bounds

- [ ] **Feature Validation**
  - [ ] Relationship creation works
  - [ ] Milestone tracking functions
  - [ ] Complexity scoring accurate
  - [ ] LLM integration operational

---

## 🎯 Integration Roadmap

### **Phase 1: Core System Integration (Weeks 1-2)**
- [ ] **Character System Integration**
  - [ ] Validate `character_id` references
  - [ ] Test character arc business rules
  - [ ] Cross-reference character data

- [ ] **Faction System Integration**
  - [ ] Validate `faction_ids` arrays
  - [ ] Test multi-faction arc rules
  - [ ] Cross-reference faction data

### **Phase 2: Advanced Integration (Weeks 3-4)**
- [ ] **NPC System Integration**
  - [ ] Validate `npc_id` references
  - [ ] Test NPC arc constraints
  - [ ] Cross-reference NPC data

- [ ] **Region System Integration**
  - [ ] Validate `region_id` references
  - [ ] Test regional arc scoping
  - [ ] Cross-reference region data

### **Phase 3: Real-time Integration (Weeks 5-6)**
- [ ] **Event-Driven Updates**
  - [ ] Arc status change events
  - [ ] Progress milestone events
  - [ ] Relationship change notifications

- [ ] **LLM Service Integration**
  - [ ] Claude API integration
  - [ ] Follow-up arc generation
  - [ ] Prompt optimization

---

## 🛡️ Rollback Plan

### **Emergency Rollback Procedures**
- [ ] **Database Rollback**
  ```sql
  -- Drop new tables
  DROP TABLE IF EXISTS arc_relationships CASCADE;
  DROP TABLE IF EXISTS arc_milestones CASCADE;
  DROP TABLE IF EXISTS arc_complexity_reports CASCADE;
  
  -- Remove new columns
  ALTER TABLE arc_entities 
  DROP COLUMN IF EXISTS predecessor_arcs,
  DROP COLUMN IF EXISTS successor_arcs,
  DROP COLUMN IF EXISTS related_arcs,
  DROP COLUMN IF EXISTS relationship_generation_prompt,
  DROP COLUMN IF EXISTS outcome_influences;
  ```

- [ ] **Code Rollback**
  - [ ] Revert to previous model versions
  - [ ] Restore original mock data
  - [ ] Remove new service files

- [ ] **Validation Post-Rollback**
  - [ ] Existing functionality intact
  - [ ] No broken references
  - [ ] API endpoints functional

---

## 📊 Success Metrics

### **Compliance Metrics**
- [ ] **Development Bible Compliance: 95%+**
- [ ] **Test Coverage: 90%+**
- [ ] **Zero Critical Failures**
- [ ] **All High-Priority Issues Resolved**

### **Performance Metrics**
- [ ] **Arc creation time: <100ms**
- [ ] **Relationship queries: <50ms**
- [ ] **Complexity analysis: <200ms**
- [ ] **Database migration time: <30 seconds**

### **Feature Completeness**
- [ ] **8 Relationship Types Implemented**
- [ ] **8+ Milestone Types Available**
- [ ] **Comprehensive Business Rules**
- [ ] **LLM Integration Functional**

---

## 🔧 Troubleshooting Guide

### **Common Issues & Solutions**

#### **Database Migration Issues**
```sql
-- Check migration status
SELECT COUNT(*) FROM information_schema.columns 
WHERE table_name = 'arc_relationships';

-- Verify constraints
SELECT conname, contype FROM pg_constraint 
WHERE conrelid = 'arc_relationships'::regclass;
```

#### **Enum Mismatch Issues**
```python
# Verify enum values
from backend.systems.arc.models.arc import ArcType
print([t.value for t in ArcType])  # Should be: global, regional, character, npc, faction, quest
```

#### **Business Rule Validation Issues**
```python
# Test business rules
from backend.systems.arc.business_rules import validate_arc_business_rules
violations = validate_arc_business_rules(arc_data)
print(f"Violations: {violations}")
```

---

## ✅ Final Checklist

- [ ] All compliance checks pass (95%+)
- [ ] Database migration successful
- [ ] API endpoints updated and tested
- [ ] Mock data updated and valid
- [ ] Integration tests passing
- [ ] Performance benchmarks met
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Rollback plan verified

---

**Deployment Authorization Required:**
- [ ] Tech Lead Approval
- [ ] Database Admin Approval  
- [ ] QA Sign-off
- [ ] Product Owner Approval

**Post-Deployment:**
- [ ] Monitor for 24 hours
- [ ] Collect performance metrics
- [ ] Gather user feedback
- [ ] Document lessons learned 