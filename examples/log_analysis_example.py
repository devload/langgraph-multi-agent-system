"""
Example: Log Analysis Mission
Demonstrates real multi-agent collaboration for log analysis
"""

import requests
import json
import time
from datetime import datetime

# Create sample log file
def create_sample_log():
    """Create a sample log file for analysis"""
    log_content = """2025-01-23 10:15:23 ERROR [AuthService] Failed login attempt for user: admin@example.com - Invalid password
2025-01-23 10:15:45 ERROR [AuthService] Failed login attempt for user: admin@example.com - Invalid password
2025-01-23 10:16:02 ERROR [AuthService] Failed login attempt for user: admin@example.com - Invalid password
2025-01-23 10:16:15 WARNING [AuthService] Multiple failed login attempts detected from IP: 192.168.1.100
2025-01-23 10:17:33 ERROR [DatabaseService] Connection timeout to primary database
2025-01-23 10:17:34 INFO [DatabaseService] Attempting failover to secondary database
2025-01-23 10:17:45 ERROR [DatabaseService] Secondary database connection failed
2025-01-23 10:18:01 CRITICAL [DatabaseService] All database connections lost
2025-01-23 10:18:23 ERROR [APIGateway] Request failed: No database connection
2025-01-23 10:18:24 ERROR [APIGateway] Request failed: No database connection
2025-01-23 10:18:25 ERROR [APIGateway] Request failed: No database connection
2025-01-23 10:19:45 INFO [DatabaseService] Connection to primary database restored
2025-01-23 10:19:46 INFO [APIGateway] Service resumed normal operation
2025-01-23 10:25:12 ERROR [PaymentService] Transaction failed: Invalid merchant ID
2025-01-23 10:25:13 ERROR [PaymentService] Transaction rollback initiated
2025-01-23 10:30:45 WARNING [MemoryMonitor] Memory usage at 85%
2025-01-23 10:31:00 WARNING [MemoryMonitor] Memory usage at 90%
2025-01-23 10:31:15 CRITICAL [MemoryMonitor] Memory usage at 95% - System may become unresponsive
2025-01-23 10:32:00 INFO [GarbageCollector] Emergency garbage collection triggered
2025-01-23 10:32:30 INFO [MemoryMonitor] Memory usage reduced to 70%
"""
    
    with open("/tmp/system_logs.txt", "w") as f:
        f.write(log_content)
    
    return "/tmp/system_logs.txt"

def register_log_analysis_mission(log_path: str):
    """Register a log analysis mission"""
    
    workflow = [
        {"from": "start", "to": "claude"},
        {"from": "claude", "to": "gemini"},
        {"from": "gemini", "to": "end"}
    ]
    
    mission = f"""Analyze the system logs at {log_path} and provide:

1. **Error Summary**: Categorize and summarize all errors found
2. **Critical Issues**: Identify the most critical problems that need immediate attention
3. **Root Cause Analysis**: For each major issue, provide potential root causes
4. **Recommendations**: Specific actions to prevent these issues in the future
5. **Priority Matrix**: Rank issues by severity and urgency

Focus on:
- Security incidents (failed logins, authentication issues)
- System stability (database failures, memory issues)
- Service disruptions and their impact
- Patterns that might indicate larger problems

Please structure your analysis clearly with sections and bullet points."""
    
    response = requests.post(
        "http://localhost:8000/api/mission/register",
        json={
            "workflow": workflow,
            "mission": mission
        }
    )
    
    if response.status_code == 200:
        return response.json()["missionId"]
    else:
        print(f"Failed to register mission: {response.status_code}")
        return None

def monitor_mission(mission_id: str):
    """Monitor mission progress and display results"""
    print(f"\n📊 Monitoring Mission: {mission_id}")
    print("=" * 60)
    
    # Start mission
    response = requests.post(f"http://localhost:8000/api/mission/{mission_id}/run")
    if response.status_code != 200:
        print("Failed to start mission")
        return
    
    # Monitor progress
    previous_status = None
    while True:
        response = requests.get(f"http://localhost:8000/api/mission/{mission_id}/status")
        if response.status_code == 200:
            data = response.json()
            current_status = data["status"]
            current_agent = data.get("current_agent", "N/A")
            
            if current_status != previous_status:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Status: {current_status}, Agent: {current_agent}")
                previous_status = current_status
            
            if current_status in ["completed", "failed"]:
                break
        
        time.sleep(2)
    
    # Get final results
    print("\n📋 Final Results:")
    print("=" * 60)
    
    response = requests.get(f"http://localhost:8000/api/mission/{mission_id}/results")
    if response.status_code == 200:
        results = response.json()
        
        # Display each agent's analysis
        for agent, result in results["results"].items():
            print(f"\n### {agent.upper()} Analysis ###")
            print(f"Status: {result['status']}")
            print(f"Content Preview:")
            
            # Show first 1000 characters of content
            content = result.get('content', 'No content')
            if len(content) > 1000:
                print(content[:1000] + "...\n[Content truncated]")
            else:
                print(content)
    
    # Get mission report
    print("\n📄 Generating Mission Report...")
    response = requests.get(f"http://localhost:8000/api/mission/{mission_id}/report")
    if response.status_code == 200:
        report_data = response.json()
        report_path = f"log_analysis_report_{mission_id}.md"
        with open(report_path, "w") as f:
            f.write(report_data["content"])
        print(f"✅ Report saved to: {report_path}")

def main():
    """Run the log analysis example"""
    print("🔍 Log Analysis Multi-Agent Example")
    print("=" * 60)
    
    # Check if services are running
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code != 200:
            raise Exception("Hub not responding")
    except Exception as e:
        print("❌ Error: Hub service is not running")
        print("Please start the system with: ./start_production.sh")
        return
    
    # Create sample log file
    print("📝 Creating sample log file...")
    log_path = create_sample_log()
    print(f"✅ Log file created at: {log_path}")
    
    # Register mission
    print("\n🚀 Registering log analysis mission...")
    mission_id = register_log_analysis_mission(log_path)
    
    if mission_id:
        print(f"✅ Mission registered: {mission_id}")
        
        # Monitor and display results
        monitor_mission(mission_id)
        
        # Show statistics
        print("\n📊 Mission Statistics:")
        response = requests.get("http://localhost:8000/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"Total Missions: {stats['overall']['total_missions']}")
            print(f"Completed: {stats['overall']['completed']}")
            print(f"Average Duration: {stats['overall']['avg_duration']:.2f}s")

if __name__ == "__main__":
    main()