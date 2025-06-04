"""
Test Suite for Utilization-Based Durability System

This test suite validates that the utilization-based durability system meets
the specific requirement: "if you were using it every day for a week and it 
was a 'basic' item it would be likely to break rather than having it just 
decay at a set rate."
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
import statistics

from backend.systems.equipment.services.business_logic_service import EquipmentBusinessLogicService
from backend.systems.equipment.services.equipment_usage_tracker import (
    EquipmentUsageTracker, 
    UsageEventType,
    UsageEvent
)


class TestUtilizationBasedDurability:
    """Test suite for utilization-based durability mechanics"""
    
    @pytest.fixture
    def business_service(self):
        """Create business logic service for testing"""
        return EquipmentBusinessLogicService()
    
    @pytest.fixture
    def usage_tracker(self, business_service):
        """Create usage tracker service for testing"""
        return EquipmentUsageTracker(business_service)
    
    def test_basic_item_one_week_daily_use_breakage_requirement(self, business_service):
        """
        Core Requirement Test: Basic item used every day for a week should likely break
        
        This test validates the primary requirement stated by the user.
        """
        # Simulate one week of daily usage for a basic item
        simulation_result = business_service.simulate_item_usage_lifecycle(
            quality_tier='basic',
            daily_usage_frequency=24,  # 24 uses per day (approximately hourly during waking hours)
            simulation_days=7,
            environmental_factor=1.0
        )
        
        # Check if item broke within the week
        item_broke_in_week = simulation_result['results']['item_broke']
        days_until_broken = simulation_result['results']['days_until_broken']
        
        # The item should have a high probability of breaking within a week
        # We'll accept if it breaks within 7 days
        assert item_broke_in_week, (
            f"Basic item should break within one week of daily use. "
            f"Item lasted {days_until_broken} days with final durability "
            f"{simulation_result['results']['final_durability']}%"
        )
        
        # Additional validation: should break within reasonable time frame
        assert days_until_broken <= 7, (
            f"Basic item took {days_until_broken} days to break, "
            f"should break within 7 days of daily use"
        )
        
        print(f"✅ Basic item broke after {days_until_broken} days of daily use")
        print(f"   Total uses: {simulation_result['results']['total_uses']}")
        print(f"   Final durability: {simulation_result['results']['final_durability']}%")
    
    def test_quality_tier_durability_differences(self, business_service):
        """Test that different quality tiers have appropriate durability differences"""
        results = {}
        
        for quality_tier in ['basic', 'military', 'mastercraft']:
            simulation = business_service.simulate_item_usage_lifecycle(
                quality_tier=quality_tier,
                daily_usage_frequency=24,
                simulation_days=30,  # Longer simulation to see differences
                environmental_factor=1.0
            )
            results[quality_tier] = simulation['results']
        
        # Basic items should break first
        basic_days = results['basic']['days_until_broken'] or 30
        military_days = results['military']['days_until_broken'] or 30
        mastercraft_days = results['mastercraft']['days_until_broken'] or 30
        
        assert basic_days <= military_days, (
            f"Basic items should break before military items. "
            f"Basic: {basic_days} days, Military: {military_days} days"
        )
        
        assert military_days <= mastercraft_days, (
            f"Military items should break before mastercraft items. "
            f"Military: {military_days} days, Mastercraft: {mastercraft_days} days"
        )
        
        print(f"✅ Quality tier durability progression:")
        print(f"   Basic: {basic_days} days")
        print(f"   Military: {military_days} days") 
        print(f"   Mastercraft: {mastercraft_days} days")
    
    def test_expected_usage_calculations(self, business_service):
        """Test that expected usage calculations match the durability constants"""
        for quality_tier in ['basic', 'military', 'mastercraft']:
            expected_uses = business_service.QUALITY_DURABILITY_USES[quality_tier]
            
            # Calculate what the business logic thinks
            lifespan_info = business_service.calculate_expected_item_lifespan(
                quality_tier=quality_tier,
                daily_usage_frequency=24,
                usage_type='normal_use',
                environmental_factor=1.0
            )
            
            calculated_total_uses = lifespan_info['expected_total_uses']
            
            # Should be approximately equal (within 10% due to variance)
            assert abs(calculated_total_uses - expected_uses) <= expected_uses * 0.1, (
                f"Expected uses calculation mismatch for {quality_tier}. "
                f"Configured: {expected_uses}, Calculated: {calculated_total_uses}"
            )
            
            print(f"✅ {quality_tier.title()} expected uses: {calculated_total_uses} "
                  f"(configured: {expected_uses})")
    
    def test_utilization_based_vs_time_based_decay(self, business_service):
        """Test that utilization-based decay differs from time-based decay"""
        initial_durability = 100.0
        quality_tier = 'basic'
        
        # Test heavy usage (many events)
        heavy_usage_durability, heavy_breakdown = business_service.calculate_utilization_based_durability_loss(
            current_durability=initial_durability,
            quality_tier=quality_tier,
            usage_type='heavy_use',
            usage_count=10,  # 10 usage events
            environmental_factor=1.0,
            is_critical=False
        )
        
        # Test light usage (few events)
        light_usage_durability, light_breakdown = business_service.calculate_utilization_based_durability_loss(
            current_durability=initial_durability,
            quality_tier=quality_tier,
            usage_type='light_use',
            usage_count=1,  # 1 usage event
            environmental_factor=1.0,
            is_critical=False
        )
        
        # Heavy usage should cause more durability loss
        heavy_loss = initial_durability - heavy_usage_durability
        light_loss = initial_durability - light_usage_durability
        
        assert heavy_loss > light_loss, (
            f"Heavy usage should cause more durability loss than light usage. "
            f"Heavy: {heavy_loss}, Light: {light_loss}"
        )
        
        print(f"✅ Utilization-based decay working:")
        print(f"   Heavy usage (10 events): {heavy_loss:.2f}% durability loss")
        print(f"   Light usage (1 event): {light_loss:.2f}% durability loss")
    
    def test_critical_usage_increased_wear(self, business_service):
        """Test that critical usage events cause more wear"""
        initial_durability = 100.0
        quality_tier = 'basic'
        
        # Normal usage
        normal_durability, normal_breakdown = business_service.calculate_utilization_based_durability_loss(
            current_durability=initial_durability,
            quality_tier=quality_tier,
            usage_type='normal_use',
            usage_count=1,
            environmental_factor=1.0,
            is_critical=False
        )
        
        # Critical usage
        critical_durability, critical_breakdown = business_service.calculate_utilization_based_durability_loss(
            current_durability=initial_durability,
            quality_tier=quality_tier,
            usage_type='normal_use',
            usage_count=1,
            environmental_factor=1.0,
            is_critical=True
        )
        
        normal_loss = initial_durability - normal_durability
        critical_loss = initial_durability - critical_durability
        
        assert critical_loss > normal_loss, (
            f"Critical usage should cause more durability loss. "
            f"Normal: {normal_loss}, Critical: {critical_loss}"
        )
        
        print(f"✅ Critical usage increases wear:")
        print(f"   Normal usage: {normal_loss:.3f}% durability loss")
        print(f"   Critical usage: {critical_loss:.3f}% durability loss")
    
    def test_low_durability_accelerated_degradation(self, business_service):
        """Test that items degrade faster when at low durability"""
        quality_tier = 'basic'
        
        # High durability usage
        high_durability, high_breakdown = business_service.calculate_utilization_based_durability_loss(
            current_durability=80.0,
            quality_tier=quality_tier,
            usage_type='normal_use',
            usage_count=1,
            environmental_factor=1.0,
            is_critical=False
        )
        
        # Low durability usage 
        low_durability, low_breakdown = business_service.calculate_utilization_based_durability_loss(
            current_durability=20.0,  # Low durability
            quality_tier=quality_tier,
            usage_type='normal_use',
            usage_count=1,
            environmental_factor=1.0,
            is_critical=False
        )
        
        high_loss = 80.0 - high_durability
        low_loss = 20.0 - low_durability
        
        # Calculate loss as percentage of current durability to normalize
        high_loss_percent = high_loss / 80.0
        low_loss_percent = low_loss / 20.0
        
        assert low_breakdown['degradation_accelerated'], (
            "Low durability should trigger accelerated degradation"
        )
        
        print(f"✅ Accelerated degradation at low durability:")
        print(f"   High durability (80%): {high_loss:.3f}% loss ({high_loss_percent:.1%} relative)")
        print(f"   Low durability (20%): {low_loss:.3f}% loss ({low_loss_percent:.1%} relative)")
        print(f"   Degradation accelerated: {low_breakdown['degradation_accelerated']}")
    
    def test_breakage_probability_at_low_durability(self, business_service):
        """Test that items have a chance to break when at very low durability"""
        quality_tier = 'basic'
        
        # Run multiple tests at very low durability to check for breakage
        breakage_events = 0
        total_tests = 100
        
        for _ in range(total_tests):
            durability, breakdown = business_service.calculate_utilization_based_durability_loss(
                current_durability=3.0,  # Very low durability
                quality_tier=quality_tier,
                usage_type='normal_use',
                usage_count=1,
                environmental_factor=1.0,
                is_critical=False
            )
            
            if breakdown['broke_this_use']:
                breakage_events += 1
        
        breakage_rate = breakage_events / total_tests
        
        # Should have some chance of breakage at very low durability
        assert breakage_rate > 0, (
            f"Items should have a chance to break at very low durability. "
            f"Breakage rate: {breakage_rate:.1%} over {total_tests} tests"
        )
        
        print(f"✅ Breakage probability at low durability:")
        print(f"   Breakage rate at 3% durability: {breakage_rate:.1%} over {total_tests} tests")
    
    def test_variance_creates_realistic_degradation(self, business_service):
        """Test that variance creates realistic, non-uniform degradation"""
        quality_tier = 'basic'
        durability_losses = []
        
        # Run same usage scenario multiple times
        for _ in range(50):
            _, breakdown = business_service.calculate_utilization_based_durability_loss(
                current_durability=100.0,
                quality_tier=quality_tier,
                usage_type='normal_use',
                usage_count=1,
                environmental_factor=1.0,
                is_critical=False
            )
            durability_losses.append(breakdown['total_durability_loss'])
        
        # Calculate variance statistics
        mean_loss = statistics.mean(durability_losses)
        stdev_loss = statistics.stdev(durability_losses)
        coefficient_of_variation = stdev_loss / mean_loss
        
        # Should have reasonable variance (not all identical)
        assert coefficient_of_variation > 0.1, (
            f"Durability loss should have variance for realism. "
            f"Coefficient of variation: {coefficient_of_variation:.3f}"
        )
        
        print(f"✅ Realistic variance in degradation:")
        print(f"   Mean loss: {mean_loss:.3f}% ± {stdev_loss:.3f}%")
        print(f"   Coefficient of variation: {coefficient_of_variation:.3f}")
    
    def test_usage_tracker_integration(self, usage_tracker):
        """Test integration between usage tracker and business logic"""
        character_id = "test_character"
        equipment_id = "test_sword"
        
        # Start a usage session
        session_id = usage_tracker.start_usage_session(character_id, "combat")
        
        # Record multiple usage events
        events = [
            usage_tracker.record_equipment_usage(
                equipment_id=equipment_id,
                character_id=character_id,
                event_type=UsageEventType.WEAPON_ATTACK,
                session_id=session_id,
                is_critical=False
            ),
            usage_tracker.record_equipment_usage(
                equipment_id=equipment_id,
                character_id=character_id,
                event_type=UsageEventType.WEAPON_ATTACK,
                session_id=session_id,
                is_critical=True  # Critical hit
            ),
            usage_tracker.record_equipment_usage(
                equipment_id=equipment_id,
                character_id=character_id,
                event_type=UsageEventType.WEAPON_PARRY,
                session_id=session_id,
                is_critical=False
            )
        ]
        
        # End session
        session = usage_tracker.end_usage_session(session_id)
        
        # Apply durability loss
        final_durability, details = usage_tracker.apply_usage_durability_loss(
            equipment_id=equipment_id,
            current_durability=100.0,
            quality_tier='basic',
            usage_events=events
        )
        
        # Verify that durability was lost
        assert final_durability < 100.0, "Equipment should lose durability from usage"
        
        # Verify that critical hit caused more damage
        critical_event_detail = next(
            detail for detail in details['event_details'] 
            if 'critical' in detail['breakdown'] and detail['breakdown']['is_critical']
        )
        normal_event_detail = next(
            detail for detail in details['event_details'] 
            if 'critical' in detail['breakdown'] and not detail['breakdown']['is_critical']
        )
        
        assert critical_event_detail['durability_loss'] > normal_event_detail['durability_loss'], (
            "Critical events should cause more durability loss"
        )
        
        print(f"✅ Usage tracker integration working:")
        print(f"   Session events: {session.total_events}")
        print(f"   Final durability: {final_durability:.2f}%")
        print(f"   Total durability loss: {details['total_durability_loss']:.2f}%")
    
    def test_realistic_one_week_scenario(self, usage_tracker):
        """Test a realistic one-week usage scenario with mixed activities"""
        character_id = "adventurer"
        sword_id = "iron_sword"
        armor_id = "leather_armor"
        
        # Equipment starting states
        equipment_states = {
            sword_id: {'current_durability': 100.0, 'quality_tier': 'basic'},
            armor_id: {'current_durability': 100.0, 'quality_tier': 'basic'}
        }
        
        total_days = 7
        daily_combat_sessions = 3  # 3 combat encounters per day
        
        for day in range(total_days):
            for session_num in range(daily_combat_sessions):
                # Start combat session
                session_id = usage_tracker.start_usage_session(character_id, "combat")
                
                # Record varied usage events per session
                usage_events = [
                    # Sword attacks (8-12 per combat)
                    *[usage_tracker.record_equipment_usage(
                        equipment_id=sword_id,
                        character_id=character_id,
                        event_type=UsageEventType.WEAPON_ATTACK,
                        session_id=session_id,
                        is_critical=(i % 10 == 0)  # 10% critical rate
                    ) for i in range(10)],
                    
                    # Armor takes hits (3-5 per combat)
                    *[usage_tracker.record_equipment_usage(
                        equipment_id=armor_id,
                        character_id=character_id,
                        event_type=UsageEventType.ARMOR_HIT,
                        session_id=session_id,
                        usage_intensity=0.8
                    ) for _ in range(4)],
                    
                    # Occasional parries (1-2 per combat)
                    *[usage_tracker.record_equipment_usage(
                        equipment_id=sword_id,
                        character_id=character_id,
                        event_type=UsageEventType.WEAPON_PARRY,
                        session_id=session_id
                    ) for _ in range(2)]
                ]
                
                # End session and process durability
                session = usage_tracker.end_usage_session(session_id)
                
                # Apply durability loss for this session
                session_results = usage_tracker.process_session_durability_loss(
                    session=session,
                    equipment_states=equipment_states
                )
                
                # Update equipment states
                for eq_id, result in session_results['equipment_results'].items():
                    equipment_states[eq_id]['current_durability'] = result['final_durability']
        
        # Check final states
        sword_durability = equipment_states[sword_id]['current_durability']
        armor_durability = equipment_states[armor_id]['current_durability']
        
        # Get usage statistics
        sword_stats = usage_tracker.get_equipment_usage_stats(sword_id)
        armor_stats = usage_tracker.get_equipment_usage_stats(armor_id)
        
        print(f"✅ One week realistic scenario results:")
        print(f"   Sword durability: {sword_durability:.1f}% (used {sword_stats['total_uses']} times)")
        print(f"   Armor durability: {armor_durability:.1f}% (used {armor_stats['total_uses']} times)")
        print(f"   Sword critical hits: {sword_stats['critical_uses']}")
        
        # Validate that significant wear occurred
        assert sword_durability < 50.0, (
            f"Sword should show significant wear after a week of heavy combat. "
            f"Final durability: {sword_durability:.1f}%"
        )
        
        # Basic items should likely break or be close to breaking
        if sword_durability > 0:
            print(f"   Sword survived but heavily worn: {sword_durability:.1f}%")
        else:
            print(f"   Sword broke during the week as expected for basic quality")


if __name__ == "__main__":
    """Run the tests as a demonstration script"""
    print("🔧 Testing Utilization-Based Durability System")
    print("=" * 60)
    
    # Create services
    business_service = EquipmentBusinessLogicService()
    usage_tracker = EquipmentUsageTracker(business_service)
    
    # Create test instance
    test_suite = TestUtilizationBasedDurability()
    
    # Run core requirement test
    print("\n1. Testing Core Requirement: Basic Item Week-Long Usage")
    test_suite.test_basic_item_one_week_daily_use_breakage_requirement(business_service)
    
    print("\n2. Testing Quality Tier Differences")
    test_suite.test_quality_tier_durability_differences(business_service)
    
    print("\n3. Testing Expected Usage Calculations")
    test_suite.test_expected_usage_calculations(business_service)
    
    print("\n4. Testing Utilization vs Time-Based Decay")
    test_suite.test_utilization_based_vs_time_based_decay(business_service)
    
    print("\n5. Testing Critical Usage Effects")
    test_suite.test_critical_usage_increased_wear(business_service)
    
    print("\n6. Testing Low Durability Acceleration")
    test_suite.test_low_durability_accelerated_degradation(business_service)
    
    print("\n7. Testing Breakage Probability")
    test_suite.test_breakage_probability_at_low_durability(business_service)
    
    print("\n8. Testing Realistic Variance")
    test_suite.test_variance_creates_realistic_degradation(business_service)
    
    print("\n9. Testing Usage Tracker Integration")
    test_suite.test_usage_tracker_integration(usage_tracker)
    
    print("\n10. Testing Realistic One-Week Scenario")
    test_suite.test_realistic_one_week_scenario(usage_tracker)
    
    print(f"\n✅ All tests completed successfully!")
    print("=" * 60)
    print("The utilization-based durability system meets the requirement:")
    print("'Basic items used every day for a week are likely to break'") 