"""
AI-Enhanced Diplomacy System Example

This script demonstrates how to use the AI-powered diplomacy features
including treaty evaluation, optimization, and automated decision-making.
"""

import asyncio
from uuid import UUID, uuid4
from datetime import datetime

from backend.systems.diplomacy.models.core_models import TreatyType
from backend.systems.diplomacy.services.ai_enhanced_services import (
    create_ai_enhanced_treaty_service,
    create_ai_enhanced_negotiation_service
)


async def example_treaty_evaluation():
    """Example of AI treaty evaluation"""
    print("\\n=== AI Treaty Evaluation Example ===")
    
    # Create AI service
    ai_service = create_ai_enhanced_treaty_service()
    
    # Example faction IDs (these would be real faction IDs in practice)
    faction_a = uuid4()
    faction_b = uuid4()
    
    # Example treaty terms
    treaty_terms = {
        "duration_years": 5,
        "tariff_reduction": 0.15,
        "trade_volume_target": "increased by 25%",
        "trade_route_protection": True,
        "renewable": True,
        "termination_notice_days": 30
    }
    
    try:
        # Evaluate the treaty proposal
        evaluation = ai_service.evaluate_treaty_proposal(
            faction_a, faction_b, TreatyType.TRADE, treaty_terms
        )
        
        print(f"Treaty Evaluation Results:")
        print(f"  Acceptance Probability: {evaluation['acceptance_probability']}")
        print(f"  Recommendation: {evaluation['recommendation']}")
        print(f"  Confidence: {evaluation['confidence']}")
        print(f"  Reasoning: {evaluation['reasoning']}")
        
        # Get key factors
        factors = evaluation.get('acceptance_factors', {})
        print(f"\\n  Key Factors:")
        for factor, value in factors.items():
            print(f"    {factor}: {value:.2f}")
            
    except Exception as e:
        print(f"Error in treaty evaluation: {e}")


async def example_treaty_optimization():
    """Example of AI treaty optimization"""
    print("\\n=== AI Treaty Optimization Example ===")
    
    # Create AI service
    ai_service = create_ai_enhanced_treaty_service()
    
    # Example faction IDs
    proposing_faction = uuid4()
    target_faction = uuid4()
    
    try:
        # Get optimized treaty terms
        optimization = ai_service.suggest_optimal_treaty_terms(
            proposing_faction, target_faction, TreatyType.ALLIANCE
        )
        
        print(f"Optimized Treaty Terms:")
        print(f"  Treaty Type: {optimization['treaty_type']}")
        print(f"  Expected Acceptance: {optimization['expected_acceptance_probability']:.2f}")
        
        print(f"\\n  Optimized Terms:")
        for term, value in optimization['optimized_terms'].items():
            print(f"    {term}: {value}")
            
        print(f"\\n  Optimization Reasoning:")
        for reason in optimization['optimization_reasoning']:
            print(f"    - {reason}")
            
    except Exception as e:
        print(f"Error in treaty optimization: {e}")


async def example_auto_negotiation():
    """Example of AI-powered negotiation response"""
    print("\\n=== AI Negotiation Response Example ===")
    
    # Create AI service
    ai_service = create_ai_enhanced_negotiation_service()
    
    # Example negotiation context
    negotiation_id = uuid4()
    responding_faction = uuid4()
    
    # Example incoming offer
    incoming_offer = {
        "treaty_type": "trade",
        "duration_years": 7,  # Long commitment
        "tariff_reduction": 0.10,  # Modest reduction
        "trade_volume_target": "increased by 15%",  # Conservative target
        "exclusive_goods": ["rare_metals"],  # Exclusivity requirement
        "military_support": False,
        "verification_mechanisms": False  # No verification
    }
    
    try:
        # Generate AI response
        response = ai_service.generate_ai_negotiation_response(
            negotiation_id, responding_faction, incoming_offer
        )
        
        print(f"AI Negotiation Response:")
        print(f"  Response Type: {response['response_type']}")
        print(f"  Message: {response['message']}")
        
        # Show analysis
        analysis = response['offer_analysis']
        print(f"\\n  Offer Analysis:")
        print(f"    Attractiveness: {analysis['attractiveness']:.2f}")
        print(f"    Economic Value: {analysis['economic_value']:.2f}")
        print(f"    Strategic Value: {analysis['strategic_value']:.2f}")
        print(f"    Risk Level: {analysis['risk_level']:.2f}")
        
        # Show concerns if any
        if analysis.get('concerns'):
            print(f"\\n  Concerns:")
            for concern in analysis['concerns']:
                print(f"    - {concern}")
        
        # Show counter-offer if applicable
        if response['response_type'] == 'counter_offer':
            print(f"\\n  Counter-offer Terms:")
            for term, value in response['counter_terms'].items():
                print(f"    {term}: {value}")
                
    except Exception as e:
        print(f"Error in negotiation response: {e}")


async def example_auto_decision_generation():
    """Example of automatic decision generation"""
    print("\\n=== AI Auto Decision Generation Example ===")
    
    # Create AI service
    ai_service = create_ai_enhanced_treaty_service()
    
    # Example faction ID
    faction_id = uuid4()
    
    try:
        # Generate automatic treaty proposal
        proposal = ai_service.auto_generate_treaty_proposal(faction_id)
        
        if proposal:
            print(f"Auto-Generated Proposal:")
            print(f"  Faction: {proposal['faction_id']}")
            print(f"  AI Confidence: {proposal['ai_confidence']:.2f}")
            print(f"  Priority Score: {proposal['priority_score']:.2f}")
            print(f"  Suggested Timing: {proposal['suggested_timing']}")
            
            print(f"\\n  Reasoning: {proposal['reasoning']}")
            
            # Show proposal details
            proposal_details = proposal['proposal']
            print(f"\\n  Proposal Details:")
            print(f"    Target Faction: {proposal_details['target_faction']}")
            print(f"    Treaty Type: {proposal_details['treaty_type']}")
            print(f"    Expected Acceptance: {proposal_details['expected_acceptance_probability']:.2f}")
            
        else:
            print("No viable treaty proposals identified for this faction at this time.")
            
    except Exception as e:
        print(f"Error in auto decision generation: {e}")


async def main():
    """Run all examples"""
    print("AI-Enhanced Diplomacy System Examples")
    print("=" * 50)
    
    # Run examples
    await example_treaty_evaluation()
    await example_treaty_optimization()
    await example_auto_negotiation()
    await example_auto_decision_generation()
    
    print("\\n" + "=" * 50)
    print("Examples completed!")
    print("\\nAPI Endpoints Available:")
    print("  POST /api/diplomacy/ai/treaties/evaluate")
    print("  POST /api/diplomacy/ai/treaties/optimize")
    print("  POST /api/diplomacy/ai/negotiations/ai-response")
    print("  GET  /api/diplomacy/ai/decisions/evaluate-all/{faction_id}")
    print("  GET  /api/diplomacy/ai/decisions/next-best/{faction_id}")
    print("  POST /api/diplomacy/ai/batch/auto-decisions")
    print("  GET  /api/diplomacy/ai/status")


if __name__ == "__main__":
    asyncio.run(main()) 