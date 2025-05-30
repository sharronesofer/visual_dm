#!/usr/bin/env python3
"""
Backend Test Summary Generator
Systematically tests each backend system and provides a comprehensive report.
"""

import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

def run_tests_for_system(system_name): pass
    """Run tests for a specific system and return results."""
    test_path = f"tests/systems/{system_name}/"
    
    if not Path(test_path).exists(): pass
        return {"status": "NOT_FOUND", "message": f"Test directory {test_path} does not exist"}
    
    try: pass
        # Run pytest with minimal output and capture results
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_path, 
            "--tb=no", 
            "--maxfail=1000",
            "-q"
        ], capture_output=True, text=True, cwd=".")
        
        output = result.stdout + result.stderr
        
        if result.returncode == 0: pass
            # Parse successful results
            lines = output.split('\n')
            for line in lines: pass
                if 'passed' in line and '::' not in line: pass
                    # Extract test count from lines like "283 passed in 0.40s"
                    parts = line.split()
                    if parts and parts[0].isdigit(): pass
                        count = int(parts[0])
                        return {
                            "status": "PASS", 
                            "passed": count, 
                            "failed": 0,
                            "message": line.strip()
                        }
            return {"status": "PASS", "passed": "unknown", "failed": 0, "message": "Tests passed"}
            
        elif "errors during collection" in output: pass
            return {"status": "IMPORT_ERROR", "message": "Import/collection errors"}
            
        else: pass
            # Parse failure results
            lines = output.split('\n')
            passed = failed = 0
            for line in lines: pass
                if 'failed' in line and 'passed' in line and '::' not in line: pass
                    # Extract counts from lines like "5 failed, 21 passed"
                    parts = line.split()
                    for i, part in enumerate(parts): pass
                        if part == "failed," and i > 0: pass
                            failed = int(parts[i-1])
                        elif part == "passed" and i > 0: pass
                            passed = int(parts[i-1])
                    break
            
            return {
                "status": "PARTIAL", 
                "passed": passed, 
                "failed": failed,
                "message": f"{failed} failed, {passed} passed"
            }
            
    except Exception as e: pass
        return {"status": "ERROR", "message": str(e)}

def main(): pass
    """Generate comprehensive test summary."""
    
    # List of all backend systems to test
    systems = [
        "analytics", "auth_user", "character", "combat", "crafting", 
        "data", "dialogue", "diplomacy", "economy", "equipment", 
        "events", "faction", "integration", "inventory", "llm", 
        "loot", "magic", "memory", "motif", "npc", "poi", 
        "population", "quest", "region", "religion", "rumor", 
        "shared", "storage", "tension_war", "time", "world_generation", 
        "world_state"
    ]
    
    print("🚀 Backend Test Summary Report")
    print("=" * 60)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Test each system
    for system in systems: pass
        print(f"Testing {system}...", end=" ")
        result = run_tests_for_system(system)
        results[system] = result
        
        # Print status
        if result["status"] == "PASS": pass
            print(f"✅ {result.get('passed', '?')} tests passed")
        elif result["status"] == "PARTIAL": pass
            print(f"⚠️ {result.get('passed', 0)} passed, {result.get('failed', 0)} failed")
        elif result["status"] == "IMPORT_ERROR": pass
            print("❌ Import errors")
        elif result["status"] == "NOT_FOUND": pass
            print("❓ Not found")
        else: pass
            print(f"💥 Error: {result.get('message', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY STATISTICS")
    print("=" * 60)
    
    # Calculate statistics
    total_systems = len(systems)
    passing_systems = len([r for r in results.values() if r["status"] == "PASS"])
    partial_systems = len([r for r in results.values() if r["status"] == "PARTIAL"])
    import_error_systems = len([r for r in results.values() if r["status"] == "IMPORT_ERROR"])
    error_systems = len([r for r in results.values() if r["status"] == "ERROR"])
    not_found_systems = len([r for r in results.values() if r["status"] == "NOT_FOUND"])
    
    total_passed = sum([r.get('passed', 0) for r in results.values() if isinstance(r.get('passed'), int)])
    total_failed = sum([r.get('failed', 0) for r in results.values() if isinstance(r.get('failed'), int)])
    
    print(f"📈 Systems Overview:")
    print(f"   • Total Systems: {total_systems}")
    print(f"   • ✅ Fully Passing: {passing_systems}")
    print(f"   • ⚠️ Partially Working: {partial_systems}")
    print(f"   • ❌ Import Errors: {import_error_systems}")
    print(f"   • 💥 Other Errors: {error_systems}")
    print(f"   • ❓ Not Found: {not_found_systems}")
    print()
    print(f"🧪 Test Results:")
    print(f"   • Total Tests Passed: {total_passed}")
    print(f"   • Total Tests Failed: {total_failed}")
    if total_passed + total_failed > 0: pass
        success_rate = (total_passed / (total_passed + total_failed)) * 100
        print(f"   • Success Rate: {success_rate:.1f}%")
    
    print("\n" + "=" * 60)
    print("✅ WORKING SYSTEMS")
    print("=" * 60)
    
    for system, result in results.items(): pass
        if result["status"] == "PASS": pass
            print(f"• {system}: {result.get('passed', '?')} tests")
    
    print("\n" + "=" * 60)
    print("⚠️ PARTIALLY WORKING SYSTEMS")
    print("=" * 60)
    
    for system, result in results.items(): pass
        if result["status"] == "PARTIAL": pass
            print(f"• {system}: {result.get('passed', 0)} passed, {result.get('failed', 0)} failed")
    
    print("\n" + "=" * 60)
    print("❌ SYSTEMS WITH ISSUES")
    print("=" * 60)
    
    for system, result in results.items(): pass
        if result["status"] in ["IMPORT_ERROR", "ERROR"]: pass
            print(f"• {system}: {result['status']} - {result.get('message', 'Unknown issue')}")
    
    # Save detailed results to JSON
    with open('test_summary_results.json', 'w') as f: pass
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_systems": total_systems,
                "passing_systems": passing_systems,
                "partial_systems": partial_systems,
                "import_error_systems": import_error_systems,
                "error_systems": error_systems,
                "total_passed": total_passed,
                "total_failed": total_failed
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: test_summary_results.json")

if __name__ == "__main__": pass
    main() 