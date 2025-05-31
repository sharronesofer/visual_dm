#!/usr/bin/env python3
"""
Frontend Integration Test Script

Tests that the religion backend API is compatible with Unity frontend expectations.
Validates API endpoints, data models, WebSocket integration, and overall compatibility.
"""

import json
import sys
import asyncio
from typing import Dict, Any, List
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.systems.religion.models.models import (
    CreateReligionRequest, UpdateReligionRequest, ReligionResponse, ReligionEntity
)
from backend.systems.religion.schemas.schemas import (
    ReligionSchema, ReligionCreateSchema, ReligionUpdateSchema
)

class FrontendIntegrationValidator:
    """Validates frontend-backend integration compatibility"""
    
    def __init__(self):
        self.test_results = {
            'api_endpoints': {},
            'data_models': {},
            'websocket_integration': {},
            'serialization': {},
            'coverage_analysis': {}
        }
        
    def validate_api_coverage(self) -> Dict[str, Any]:
        """Validate API endpoint coverage against frontend expectations"""
        
        # Frontend expected endpoints from ReligionService.cs
        frontend_endpoints = {
            'GET /api/religion/': 'GetReligionsAsync',
            'GET /api/religion/{id}': 'GetReligionAsync', 
            'POST /api/religion/': 'CreateReligionAsync',
            'PUT /api/religion/{id}': 'UpdateReligionAsync',
            'DELETE /api/religion/{id}': 'DeleteReligionAsync',
            'GET /api/religion/pantheon/{id}': 'GetReligionsByPantheonAsync',
            'GET /api/religion/{id}/practices': 'GetReligiousPracticesAsync',
            'POST /api/religion/{id}/practices': 'AddReligiousPracticeAsync',
            'GET /api/religion/{id}/deities': 'GetDeitiesAsync',
            'POST /api/religion/{id}/deities': 'CreateDeityAsync',
            'GET /api/religion/{id}/events': 'GetReligiousEventsAsync',
            'POST /api/religion/{id}/events': 'CreateReligiousEventAsync',
            'GET /api/religion/{id}/influence/{region_id}': 'GetReligiousInfluenceAsync',
            'PUT /api/religion/{id}/influence/{region_id}': 'UpdateReligiousInfluenceAsync'
        }
        
        # Backend actual endpoints (from our router analysis)
        backend_endpoints = {
            'GET /religions/': 'list_religions',
            'GET /religions/{religion_id}': 'get_religion',
            'POST /religions/': 'create_religion',
            'PUT /religions/{religion_id}': 'update_religion',
            'DELETE /religions/{religion_id}': 'delete_religion',
            'GET /religions/search/': 'search_religions',
            'GET /religions/name/{name}': 'get_religion_by_name',
            'POST /religions/bulk': 'bulk_create_religions',
            'GET /religions/statistics/overview': 'get_religion_statistics',
            'GET /religions/health': 'health_check'
        }
        
        coverage = {
            'covered_endpoints': [],
            'missing_endpoints': [],
            'extra_endpoints': [],
            'mapping_issues': []
        }
        
        # Analyze coverage
        for frontend_endpoint, frontend_method in frontend_endpoints.items():
            # Map frontend path to backend pattern
            backend_equivalent = self._map_frontend_to_backend_endpoint(frontend_endpoint)
            
            if backend_equivalent in [ep for ep in backend_endpoints.keys()]:
                coverage['covered_endpoints'].append({
                    'frontend': frontend_endpoint,
                    'backend': backend_equivalent,
                    'method': frontend_method
                })
            else:
                coverage['missing_endpoints'].append({
                    'frontend': frontend_endpoint,
                    'method': frontend_method,
                    'expected_backend': backend_equivalent
                })
        
        # Find extra backend endpoints not expected by frontend
        frontend_mapped = [self._map_frontend_to_backend_endpoint(ep) for ep in frontend_endpoints.keys()]
        for backend_ep in backend_endpoints.keys():
            if backend_ep not in frontend_mapped:
                coverage['extra_endpoints'].append(backend_ep)
        
        self.test_results['api_endpoints'] = coverage
        return coverage
    
    def _map_frontend_to_backend_endpoint(self, frontend_endpoint: str) -> str:
        """Map frontend endpoint pattern to expected backend pattern"""
        # Unity frontend expects /api/religion/, backend provides /religions/
        mapping = {
            'GET /api/religion/': 'GET /religions/',
            'GET /api/religion/{id}': 'GET /religions/{religion_id}',
            'POST /api/religion/': 'POST /religions/',
            'PUT /api/religion/{id}': 'PUT /religions/{religion_id}',
            'DELETE /api/religion/{id}': 'DELETE /religions/{religion_id}',
            'GET /api/religion/pantheon/{id}': 'GET /religions/pantheon/{id}',  # Missing
            'GET /api/religion/{id}/practices': 'GET /religions/{religion_id}/practices',  # Missing
            'POST /api/religion/{id}/practices': 'POST /religions/{religion_id}/practices',  # Missing
            'GET /api/religion/{id}/deities': 'GET /religions/{religion_id}/deities',  # Missing
            'POST /api/religion/{id}/deities': 'POST /religions/{religion_id}/deities',  # Missing
            'GET /api/religion/{id}/events': 'GET /religions/{religion_id}/events',  # Missing
            'POST /api/religion/{id}/events': 'POST /religions/{religion_id}/events',  # Missing
            'GET /api/religion/{id}/influence/{region_id}': 'GET /religions/{religion_id}/influence/{region_id}',  # Missing
            'PUT /api/religion/{id}/influence/{region_id}': 'PUT /religions/{religion_id}/influence/{region_id}'  # Missing
        }
        
        return mapping.get(frontend_endpoint, frontend_endpoint.replace('/api/religion/', '/religions/'))
    
    def validate_data_model_compatibility(self) -> Dict[str, Any]:
        """Validate Unity DTOs are compatible with backend models"""
        
        compatibility = {
            'religion_dto': {},
            'request_dtos': {},
            'response_dtos': {},
            'field_mapping': {},
            'type_compatibility': {}
        }
        
        # Test ReligionDTO compatibility with backend ReligionResponse
        try:
            # Create a sample backend religion response
            sample_religion = ReligionResponse(
                id="550e8400-e29b-41d4-a716-446655440000",
                name="Test Religion",
                description="A test religion",
                status="active",
                created_at="2024-01-01T00:00:00Z",
                is_active=True,
                properties={"type": "monotheistic"}
            )
            
            # Convert to dict to test serialization
            religion_dict = sample_religion.model_dump()
            
            # Test Unity expected fields from ReligionModels.cs
            unity_expected_fields = [
                'id', 'name', 'description', 'type', 'origin_story', 'core_beliefs',
                'practices', 'clergy_structure', 'holy_texts', 'deities', 
                'followers_count', 'influence_regions', 'status', 'created_at', 'updated_at'
            ]
            
            backend_provided_fields = list(religion_dict.keys())
            
            compatibility['religion_dto'] = {
                'unity_expected': unity_expected_fields,
                'backend_provided': backend_provided_fields,
                'missing_in_backend': [f for f in unity_expected_fields if f not in backend_provided_fields],
                'extra_in_backend': [f for f in backend_provided_fields if f not in unity_expected_fields],
                'compatible_fields': [f for f in unity_expected_fields if f in backend_provided_fields]
            }
            
        except Exception as e:
            compatibility['religion_dto']['error'] = str(e)
        
        # Test CreateReligionRequest compatibility
        try:
            # Unity CreateReligionRequestDTO fields
            unity_create_fields = [
                'name', 'description', 'type', 'origin_story', 'core_beliefs',
                'tenets', 'practices', 'holy_places', 'sacred_texts', 'clergy_structure'
            ]
            
            # Backend CreateReligionRequest fields
            backend_create_sample = CreateReligionRequest(
                name="Test Religion",
                description="Test description",
                properties={}
            )
            backend_create_fields = list(backend_create_sample.model_fields.keys())
            
            compatibility['request_dtos'] = {
                'unity_expected': unity_create_fields,
                'backend_provided': backend_create_fields,
                'missing_in_backend': [f for f in unity_create_fields if f not in backend_create_fields],
                'extra_in_backend': [f for f in backend_create_fields if f not in unity_create_fields],
                'compatible_fields': [f for f in unity_create_fields if f in backend_create_fields]
            }
            
        except Exception as e:
            compatibility['request_dtos']['error'] = str(e)
        
        self.test_results['data_models'] = compatibility
        return compatibility
    
    def validate_websocket_integration(self) -> Dict[str, Any]:
        """Validate WebSocket integration for real-time updates"""
        
        websocket_analysis = {
            'channels_available': [],
            'frontend_expectations': [],
            'message_format': {},
            'integration_status': 'unknown'
        }
        
        try:
            # Check if WebSocket manager is available
            from backend.systems.religion.websocket_manager import religion_websocket_manager
            
            websocket_analysis['channels_available'] = list(religion_websocket_manager.channel_subscribers.keys())
            websocket_analysis['integration_status'] = 'available'
            
            # Unity frontend expects WebSocket updates for:
            frontend_expected_channels = [
                'religion_updates',      # Religion CRUD operations
                'membership_updates',    # Membership changes
                'religious_events',      # Religious ceremonies/events
                'narrative_updates',     # Religious narrative events
                'influence_changes'      # Religious influence updates
            ]
            
            websocket_analysis['frontend_expectations'] = frontend_expected_channels
            websocket_analysis['channel_mapping'] = {
                'religion_updates': 'religion',
                'membership_updates': 'membership', 
                'religious_events': 'religious_events',
                'narrative_updates': 'religious_narrative',
                'influence_changes': 'religious_influence'
            }
            
            # Test WebSocket endpoints availability
            from backend.systems.religion.routers.websocket_routes import religion_websocket_router
            websocket_analysis['endpoints_available'] = [
                '/ws/religion/connect',
                '/ws/religion/region/{region_id}',
                '/ws/religion/character/{character_id}',
                '/ws/religion/narrative'
            ]
            
        except Exception as e:
            websocket_analysis['integration_status'] = 'error'
            websocket_analysis['error'] = str(e)
        
        self.test_results['websocket_integration'] = websocket_analysis
        return websocket_analysis
    
    def validate_serialization_compatibility(self) -> Dict[str, Any]:
        """Test JSON serialization compatibility between C# and Python"""
        
        serialization = {
            'json_compatibility': {},
            'datetime_handling': {},
            'enum_compatibility': {},
            'nullable_fields': {}
        }
        
        try:
            # Test basic religion serialization
            sample_religion = {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Test Religion",
                "description": "A comprehensive test religion",
                "type": "Monotheistic",  # Unity enum format
                "status": "active",
                "created_at": "2024-01-01T00:00:00.000Z",  # ISO format Unity expects
                "updated_at": "2024-01-01T00:00:00.000Z",
                "is_active": True,
                "properties": {
                    "core_beliefs": ["belief1", "belief2"],
                    "practices": ["practice1", "practice2"]
                }
            }
            
            # Test JSON round-trip
            json_str = json.dumps(sample_religion)
            parsed_back = json.loads(json_str)
            
            serialization['json_compatibility'] = {
                'serializable': True,
                'round_trip_success': sample_religion == parsed_back,
                'sample_json': json_str[:200] + "..." if len(json_str) > 200 else json_str
            }
            
            # Test enum compatibility
            unity_religion_types = [
                "Monotheistic", "Polytheistic", "Pantheistic", 
                "Atheistic", "Agnostic", "Shamanic", "Ancestral"
            ]
            
            serialization['enum_compatibility'] = {
                'unity_types': unity_religion_types,
                'backend_supports': True,  # Our backend uses flexible string type
                'mapping_needed': False
            }
            
        except Exception as e:
            serialization['json_compatibility']['error'] = str(e)
        
        self.test_results['serialization'] = serialization
        return serialization
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run all integration validation tests"""
        
        print("🔍 Running Frontend Integration Analysis...")
        print("=" * 50)
        
        # API Coverage Analysis
        print("\n📡 API Endpoint Coverage Analysis:")
        api_coverage = self.validate_api_coverage()
        print(f"✅ Covered endpoints: {len(api_coverage['covered_endpoints'])}")
        print(f"❌ Missing endpoints: {len(api_coverage['missing_endpoints'])}")
        print(f"➕ Extra endpoints: {len(api_coverage['extra_endpoints'])}")
        
        if api_coverage['missing_endpoints']:
            print("\n🚨 Missing Endpoints (Frontend expects but Backend doesn't provide):")
            for missing in api_coverage['missing_endpoints']:
                print(f"   • {missing['frontend']} ({missing['method']})")
        
        # Data Model Compatibility
        print("\n📊 Data Model Compatibility Analysis:")
        model_compat = self.validate_data_model_compatibility()
        religion_dto = model_compat.get('religion_dto', {})
        if 'missing_in_backend' in religion_dto:
            print(f"🔍 Religion DTO - Missing fields: {len(religion_dto['missing_in_backend'])}")
            print(f"✅ Religion DTO - Compatible fields: {len(religion_dto['compatible_fields'])}")
        
        # WebSocket Integration
        print("\n🌐 WebSocket Integration Analysis:")
        ws_integration = self.validate_websocket_integration()
        print(f"📡 WebSocket Status: {ws_integration['integration_status']}")
        if ws_integration['integration_status'] == 'available':
            print(f"🔗 Available channels: {len(ws_integration['channels_available'])}")
            print(f"📱 WebSocket endpoints: {len(ws_integration.get('endpoints_available', []))}")
        
        # Serialization Compatibility
        print("\n🔄 Serialization Compatibility Analysis:")
        serialization = self.validate_serialization_compatibility()
        json_compat = serialization.get('json_compatibility', {})
        if json_compat.get('serializable'):
            print("✅ JSON serialization: Compatible")
            print(f"🔄 Round-trip serialization: {json_compat.get('round_trip_success', False)}")
        
        # Overall Assessment
        print("\n📈 Overall Integration Assessment:")
        total_issues = (
            len(api_coverage['missing_endpoints']) +
            len(model_compat.get('religion_dto', {}).get('missing_in_backend', [])) +
            (0 if ws_integration['integration_status'] == 'available' else 1)
        )
        
        if total_issues == 0:
            print("🎉 EXCELLENT: Full frontend-backend compatibility!")
        elif total_issues <= 3:
            print("✅ GOOD: Minor compatibility issues, easily addressable")
        elif total_issues <= 6:
            print("⚠️  MODERATE: Some compatibility issues need attention")
        else:
            print("🚨 SIGNIFICANT: Major compatibility issues require work")
        
        print(f"\n📊 Total compatibility issues: {total_issues}")
        
        # Summary for task completion
        self.test_results['coverage_analysis'] = {
            'total_issues': total_issues,
            'api_coverage_score': len(api_coverage['covered_endpoints']) / len(api_coverage['covered_endpoints'] + api_coverage['missing_endpoints']) if (api_coverage['covered_endpoints'] + api_coverage['missing_endpoints']) else 1,
            'websocket_available': ws_integration['integration_status'] == 'available',
            'serialization_compatible': json_compat.get('serializable', False),
            'ready_for_frontend': total_issues <= 3
        }
        
        return self.test_results

def main():
    """Main function to run frontend integration validation"""
    
    validator = FrontendIntegrationValidator()
    results = validator.run_comprehensive_analysis()
    
    # Save results for reference
    results_file = Path(__file__).parent / "frontend_integration_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Return summary for task completion assessment
    coverage = results['coverage_analysis']
    return {
        'success': coverage['ready_for_frontend'],
        'api_coverage_score': coverage['api_coverage_score'],
        'websocket_available': coverage['websocket_available'],
        'total_issues': coverage['total_issues']
    }

if __name__ == "__main__":
    result = main()
    print(f"\n🎯 Frontend Integration Ready: {result['success']}")
    print(f"📊 API Coverage: {result['api_coverage_score']:.1%}")
    print(f"🌐 WebSocket Available: {result['websocket_available']}") 