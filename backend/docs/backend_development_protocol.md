# Backend Development Protocol
**Generalized Standards for All Backend Development Tasks**

This protocol establishes comprehensive standards for all backend development work, ensuring consistency, quality, and integration compatibility across the entire Visual DM project.

## 🔧 Implementation Protocol

### **Phase 1: Assessment and Error Resolution**
- **System Analysis**: Run comprehensive analysis on target systems under `/backend/systems/` and `/backend/tests/`
- **Error Identification**: Identify import errors, missing dependencies, test failures, and structural violations  
- **Standards Compliance**: Ensure all code adheres to `Development_Bible.md` requirements
- **Missing Logic**: Implement any missing functionality with direct reference to `Development_Bible.md`
- **Integration Validation**: Verify compatibility with existing system architecture

### **Phase 2: Structure and Organization Enforcement**  
- **Canonical Structure**: Ensure all code follows `/backend/systems/` organization hierarchy
- **Test Organization**: Verify all tests reside under `/backend/tests/` with proper structure
- **File Cleanup**: Remove duplicate files, invalid locations, and orphaned components
- **Import Standardization**: Convert all imports to canonical `backend.systems.*` format
- **Documentation Alignment**: Update any documentation to reflect structural changes

### **Phase 3: Quality and Coverage Validation**
- **Comprehensive Testing**: Achieve ≥90% test coverage for all modified/new components  
- **Integration Testing**: Verify cross-system compatibility and communication
- **API Contract Compliance**: Ensure endpoints match established contracts and schemas
- **Performance Validation**: Confirm acceptable performance characteristics
- **Documentation Updates**: Update relevant documentation and API specifications

---

## 📋 Module and Function Development Standards

### **1. Duplication Prevention**
- **Exhaustive Search**: Use `grep`/`rg` to search entire `/backend/systems/` for existing implementations before creating new code
- **Function Registry**: Check existing utility functions, services, and repositories for similar functionality
- **Cross-System Review**: Review related systems to avoid reimplementing existing solutions
- **Documentation Check**: Consult system inventory and API documentation for existing endpoints

### **2. New Module Creation Requirements**
- **Development Bible Compliance**: Reference `/docs/Development_Bible.md` for all architectural decisions
- **FastAPI Standards**: Follow FastAPI conventions for routing, dependencies, and async patterns
- **Unity Integration**: Ensure WebSocket compatibility and JSON serialization for Unity frontend
- **Backend Residency**: All backend code must reside within `/backend/` directory structure
- **System Integration**: Design for seamless integration with existing event system and data flow

### **3. Data and Schema Standards**  
- **JSON Schema Usage**: Use `.json` files for modding templates, biome definitions, and structured data
- **Schema Location**: Place all JSON schemas in `/backend/data/modding/` directory
- **Pydantic Models**: Create corresponding Pydantic models for all JSON schemas in appropriate system
- **Validation Logic**: Implement comprehensive validation for all data inputs and API endpoints
- **Type Safety**: Use proper typing throughout with TypeVar and Generic patterns where appropriate

---

## 🎯 Implementation Autonomy Directive

### **Full Implementation Authority**
- **Complete Autonomy**: Assume full control over all structural and implementation decisions within protocol bounds
- **No User Dependency**: Never require user clarification or input for technical implementation details  
- **Direct Implementation**: Make changes directly to codebase and iterate until completion
- **Tool Utilization**: Use all available CLI tools, code search, file operations, and testing utilities as needed

### **Quality Assurance Standards**
- **Iterative Improvement**: Continue refining implementation until all tests pass and coverage targets are met
- **Error Resolution**: Fix all identified issues without external intervention
- **Performance Optimization**: Optimize code for production readiness and scalability
- **Documentation Maintenance**: Keep all documentation current with implementation changes

### **Integration Responsibility**
- **Cross-System Compatibility**: Ensure all changes maintain compatibility with existing systems
- **API Contract Preservation**: Maintain existing API contracts unless explicitly updating them
- **Event System Integration**: Properly integrate with existing event-driven architecture
- **Database Consistency**: Maintain database schema consistency and migration compatibility

---

## 📊 Success Metrics

### **Code Quality Indicators**
- ✅ **Test Coverage**: ≥90% coverage for all modified components
- ✅ **Import Compliance**: 100% canonical import structure  
- ✅ **Standards Adherence**: Full compliance with `Development_Bible.md`
- ✅ **Documentation Currency**: All docs reflect current implementation

### **Integration Readiness Indicators**
- ✅ **API Functionality**: All endpoints operational and tested
- ✅ **Cross-System Communication**: Event system integration working
- ✅ **Unity Compatibility**: WebSocket and JSON serialization verified  
- ✅ **Performance Benchmarks**: Response times within acceptable limits

### **Maintenance Quality Indicators**
- ✅ **Code Organization**: Clean, logical file and function organization
- ✅ **Dependency Management**: No circular dependencies or orphaned imports
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **Scalability Readiness**: Code structured for future expansion

---

## 🔗 Reference Documents

- **Primary Standard**: `/docs/Development_Bible.md`
- **System Inventory**: `backend/backend_systems_inventory.md`  
- **Testing Results**: `backend/task41_implementation_summary.md`
- **API Contracts**: `api_contracts.yaml` (when available)

---

*This protocol ensures consistent, high-quality backend development that seamlessly integrates with the Visual DM architecture and supports efficient Unity frontend development.* 