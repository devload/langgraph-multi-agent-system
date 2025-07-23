#!/usr/bin/env python3
"""
Simple test without external dependencies
"""

import subprocess
import time
import os
import signal
import sys

def test_basic_langgraph():
    """Test basic LangGraph functionality"""
    print("🧪 Testing Basic LangGraph Implementation")
    print("=" * 50)
    
    # Test the code review graph example
    try:
        # Run the example
        result = subprocess.run(
            [sys.executable, "examples/code_review_graph.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ LangGraph example executed successfully")
            print("\nOutput Preview:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            
            # Check if report was created
            if os.path.exists("code_review_report.md"):
                print("\n✅ Report file created successfully")
                with open("code_review_report.md", "r") as f:
                    print("\nReport Preview:")
                    print(f.read()[:800] + "...")
            return True
        else:
            print(f"❌ LangGraph example failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running LangGraph example: {e}")
        return False

def test_hub_standalone():
    """Test Hub server in standalone mode"""
    print("\n🧪 Testing Hub Server Standalone")
    print("=" * 50)
    
    # Start hub with direct Python
    hub_process = None
    try:
        print("🚀 Starting Hub server...")
        hub_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "hub.app:app", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        # Wait for startup
        time.sleep(5)
        
        # Check if running
        if hub_process.poll() is None:
            print("✅ Hub server started successfully")
            
            # Test API endpoints
            import requests
            try:
                # Test health
                response = requests.get("http://localhost:8000/docs")
                if response.status_code == 200:
                    print("✅ API documentation accessible")
                
                # Test mission registration
                test_workflow = [
                    {"from": "start", "to": "claude"},
                    {"from": "claude", "to": "end"}
                ]
                
                response = requests.post(
                    "http://localhost:8000/api/mission/register",
                    json={
                        "workflow": test_workflow,
                        "mission": "Test mission"
                    }
                )
                
                if response.status_code == 200:
                    mission_id = response.json()["missionId"]
                    print(f"✅ Mission registered: {mission_id}")
                    
                    # Test status check
                    response = requests.get(f"http://localhost:8000/api/mission/{mission_id}/status")
                    if response.status_code == 200:
                        print("✅ Mission status endpoint working")
                        return True
                else:
                    print(f"❌ Mission registration failed: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print("❌ Could not connect to Hub API")
        else:
            # Read error output
            _, stderr = hub_process.communicate(timeout=1)
            print(f"❌ Hub server failed to start: {stderr.decode()}")
            
    except Exception as e:
        print(f"❌ Error testing Hub: {e}")
    finally:
        # Clean up
        if hub_process and hub_process.poll() is None:
            print("\n🧹 Stopping Hub server...")
            os.killpg(os.getpgid(hub_process.pid), signal.SIGTERM)
            hub_process.wait(timeout=5)
    
    return False

def test_agent_base():
    """Test agent base functionality"""
    print("\n🧪 Testing Agent Base Class")
    print("=" * 50)
    
    try:
        # Import and check
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from agent_base import AgentBase
        print("✅ Agent base class imported successfully")
        
        # Check configuration files
        configs = [
            "agent-claude/agent_config.yaml",
            "agent-gemini/agent_config.yaml"
        ]
        
        for config in configs:
            if os.path.exists(config):
                print(f"✅ Configuration found: {config}")
            else:
                print(f"❌ Missing configuration: {config}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent base: {e}")
        return False

def main():
    """Run all tests"""
    print("🔬 Multi-Agent System Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic LangGraph
    if test_basic_langgraph():
        tests_passed += 1
    
    # Test 2: Hub Server
    if test_hub_standalone():
        tests_passed += 1
    
    # Test 3: Agent Base
    if test_agent_base():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())