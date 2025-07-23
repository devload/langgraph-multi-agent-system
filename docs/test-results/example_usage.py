"""
Example usage of the Multi-Agent Mission System
"""

import requests
import json
import time

# Hub API endpoint
HUB_URL = "http://localhost:8000"

def register_mission():
    """Register a new mission with Claude -> Gemini workflow"""
    
    workflow = [
        {"from": "start", "to": "claude"},
        {"from": "claude", "to": "gemini"},
        {"from": "gemini", "to": "end"}
    ]
    
    mission_data = {
        "workflow": workflow,
        "mission": "다음 log.txt를 분석해서 에러 요약하고 해결방안을 제시해주세요."
    }
    
    response = requests.post(f"{HUB_URL}/api/mission/register", json=mission_data)
    result = response.json()
    print(f"Mission registered: {result}")
    return result["missionId"]

def get_mission_graph(mission_id):
    """Get mission workflow visualization"""
    response = requests.get(f"{HUB_URL}/api/mission/{mission_id}/graph")
    result = response.json()
    print(f"Mission graph:\n{result['mermaid']}")
    return result

def run_mission(mission_id):
    """Execute the mission"""
    response = requests.post(f"{HUB_URL}/api/mission/{mission_id}/run")
    result = response.json()
    print(f"Mission started: {result}")
    return result

def check_mission_status(mission_id):
    """Check mission execution status"""
    response = requests.get(f"{HUB_URL}/api/mission/{mission_id}/status")
    result = response.json()
    print(f"Mission status: {json.dumps(result, indent=2)}")
    return result

def main():
    print("=== Multi-Agent Mission System Example ===\n")
    
    # 1. Register mission
    print("1. Registering mission...")
    mission_id = register_mission()
    print(f"   Mission ID: {mission_id}\n")
    
    # 2. Get mission graph
    print("2. Getting mission graph...")
    get_mission_graph(mission_id)
    print()
    
    # 3. Run mission
    print("3. Running mission...")
    run_mission(mission_id)
    print()
    
    # 4. Monitor status
    print("4. Monitoring mission status...")
    while True:
        time.sleep(5)
        status = check_mission_status(mission_id)
        
        if status["status"] in ["completed", "failed"]:
            print(f"\nMission {status['status']}!")
            break
        
        print(f"   Current agent: {status.get('current_agent', 'N/A')}")

if __name__ == "__main__":
    main()