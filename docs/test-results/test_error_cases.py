#!/usr/bin/env python3
"""
Error case tests for Multi-Agent Mission System
"""

import requests
import json
import sys
import subprocess
import time
import os
import signal

# Configuration
HUB_URL = "http://localhost:8000"

# Process storage
processes = []

def cleanup():
    """Clean up all processes"""
    print("\n🧹 Cleaning up processes...")
    for p in processes:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except:
            pass

def start_hub():
    """Start Hub service"""
    print("🚀 Starting Hub...")
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "app:app", "--port", "8000"],
        cwd="hub",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,
        env=env
    )
    processes.append(proc)
    
    # Wait for service
    time.sleep(3)
    return proc

def test_invalid_workflow():
    """Test registration with invalid workflow"""
    print("\n❌ Testing invalid workflow (no start node)...")
    
    workflow = [
        {"from": "claude", "to": "gemini"},
        {"from": "gemini", "to": "end"}
    ]
    
    response = requests.post(f"{HUB_URL}/api/mission/register", json={
        "workflow": workflow,
        "mission": "Test mission"
    })
    
    if response.status_code != 200:
        print(f"✅ Correctly rejected invalid workflow: {response.status_code}")
        return True
    else:
        print(f"❌ Accepted invalid workflow!")
        return False

def test_circular_workflow():
    """Test registration with circular workflow"""
    print("\n❌ Testing circular workflow...")
    
    workflow = [
        {"from": "start", "to": "claude"},
        {"from": "claude", "to": "gemini"},
        {"from": "gemini", "to": "claude"},  # Circular reference
        {"from": "claude", "to": "end"}
    ]
    
    response = requests.post(f"{HUB_URL}/api/mission/register", json={
        "workflow": workflow,
        "mission": "Test mission"
    })
    
    if response.status_code != 200:
        print(f"✅ Correctly rejected circular workflow: {response.status_code}")
        return True
    else:
        print(f"❌ Accepted circular workflow!")
        return False

def test_missing_mission():
    """Test accessing non-existent mission"""
    print("\n❌ Testing non-existent mission...")
    
    fake_id = "nonexistent123"
    
    # Test graph endpoint
    response = requests.get(f"{HUB_URL}/api/mission/{fake_id}/graph")
    if response.status_code == 404:
        print("✅ Graph endpoint correctly returns 404")
    else:
        print(f"❌ Graph endpoint returned {response.status_code}")
        return False
    
    # Test status endpoint
    response = requests.get(f"{HUB_URL}/api/mission/{fake_id}/status")
    if response.status_code == 404:
        print("✅ Status endpoint correctly returns 404")
    else:
        print(f"❌ Status endpoint returned {response.status_code}")
        return False
    
    # Test run endpoint
    response = requests.post(f"{HUB_URL}/api/mission/{fake_id}/run")
    if response.status_code == 404:
        print("✅ Run endpoint correctly returns 404")
    else:
        print(f"❌ Run endpoint returned {response.status_code}")
        return False
    
    return True

def test_malformed_request():
    """Test with malformed request data"""
    print("\n❌ Testing malformed request...")
    
    # Missing workflow
    response = requests.post(f"{HUB_URL}/api/mission/register", json={
        "mission": "Test mission"
    })
    
    if response.status_code == 422:
        print("✅ Correctly rejected request without workflow")
    else:
        print(f"❌ Accepted malformed request: {response.status_code}")
        return False
    
    # Missing mission
    response = requests.post(f"{HUB_URL}/api/mission/register", json={
        "workflow": [{"from": "start", "to": "end"}]
    })
    
    if response.status_code == 422:
        print("✅ Correctly rejected request without mission")
    else:
        print(f"❌ Accepted malformed request: {response.status_code}")
        return False
    
    return True

def test_agent_failure_simulation():
    """Test system behavior when agent fails"""
    print("\n❌ Testing agent failure handling...")
    
    # Register a normal mission
    workflow = [
        {"from": "start", "to": "claude"},
        {"from": "claude", "to": "end"}
    ]
    
    response = requests.post(f"{HUB_URL}/api/mission/register", json={
        "workflow": workflow,
        "mission": "Test mission"
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to register mission: {response.status_code}")
        return False
    
    mission_id = response.json()["missionId"]
    
    # Manually send a failure result
    response = requests.post(f"{HUB_URL}/api/agent/result", json={
        "missionId": mission_id,
        "agent": "claude",
        "status": "failed",
        "message": "Simulated agent failure",
        "result_path": ""
    })
    
    if response.status_code == 200:
        print("✅ System accepted agent failure report")
        
        # Check mission status
        status_response = requests.get(f"{HUB_URL}/api/mission/{mission_id}/status")
        status = status_response.json()
        
        if "claude" in status["results"] and status["results"]["claude"]["status"] == "failed":
            print("✅ Mission status correctly shows agent failure")
            return True
        else:
            print("❌ Mission status doesn't reflect agent failure")
            return False
    else:
        print(f"❌ Failed to report agent failure: {response.status_code}")
        return False

def run_error_tests():
    """Run all error case tests"""
    print("🧪 Starting Error Case Tests")
    print("=" * 50)
    
    try:
        # Start Hub only
        start_hub()
        
        # Run error tests
        tests_passed = 0
        total_tests = 5
        
        if test_invalid_workflow():
            tests_passed += 1
            
        if test_circular_workflow():
            tests_passed += 1
            
        if test_missing_mission():
            tests_passed += 1
            
        if test_malformed_request():
            tests_passed += 1
            
        if test_agent_failure_simulation():
            tests_passed += 1
        
        print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
        
        if tests_passed == total_tests:
            print("✅ All error case tests passed!")
            return True
        else:
            print("❌ Some error case tests failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error test failed with exception: {e}")
        return False
    finally:
        cleanup()

if __name__ == "__main__":
    success = run_error_tests()
    sys.exit(0 if success else 1)