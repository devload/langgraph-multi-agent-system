#!/usr/bin/env python3
"""
Demo Scenario: Multi-Agent Collaboration Examples
Shows various use cases for the multi-agent system
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.code_review_graph import run_code_review

def demo_code_review():
    """Demonstrate code review workflow"""
    print("\n" + "="*60)
    print("📋 DEMO 1: Code Review Workflow")
    print("="*60)
    
    # Create a sample code file
    sample_code = """
import sqlite3
import os

def get_user_data(user_id):
    # Potential SQL injection vulnerability
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchall()

def process_large_dataset(data):
    # Inefficient nested loop
    results = []
    for item in data:
        for other in data:
            if item['id'] == other['parent_id']:
                results.append({
                    'item': item,
                    'parent': other
                })
    return results

def save_config(config_dict):
    # Missing error handling
    with open('config.json', 'w') as f:
        json.dump(config_dict, f)
"""
    
    # Save sample code
    os.makedirs("/tmp/demo_code", exist_ok=True)
    with open("/tmp/demo_code/sample.py", "w") as f:
        f.write(sample_code)
    
    print("📝 Created sample code with issues:")
    print("   - SQL injection vulnerability")
    print("   - Performance issues (O(n²) complexity)")
    print("   - Missing error handling")
    
    print("\n🔍 Running multi-agent code review...")
    
    # Run code review
    result = run_code_review(
        code_path="/tmp/demo_code/sample.py",
        mission="Review this Python code for security vulnerabilities, performance issues, and best practices",
        review_type="comprehensive"
    )
    
    print("\n✅ Code review completed!")
    print(f"   Status: {result['status']}")
    print(f"   Issues found: {len(result['issues_found'])}")
    
    # Save and display report
    report_path = "/tmp/demo_code/review_report.md"
    with open(report_path, "w") as f:
        f.write(result['final_report'])
    
    print(f"\n📄 Report saved to: {report_path}")
    print("\n--- Report Preview ---")
    print(result['final_report'][:1000] + "..." if len(result['final_report']) > 1000 else result['final_report'])

def demo_workflow_patterns():
    """Show different workflow patterns"""
    print("\n" + "="*60)
    print("🔀 DEMO 2: Workflow Patterns")
    print("="*60)
    
    patterns = {
        "Sequential Analysis": {
            "description": "Each agent builds on the previous one's work",
            "workflow": [
                {"from": "start", "to": "claude"},
                {"from": "claude", "to": "gemini"},
                {"from": "gemini", "to": "end"}
            ],
            "use_case": "Progressive enhancement of analysis"
        },
        
        "Single Agent": {
            "description": "Use only one specific agent",
            "workflow": [
                {"from": "start", "to": "claude"},
                {"from": "claude", "to": "end"}
            ],
            "use_case": "Quick analysis or specific agent capabilities"
        },
        
        "Validation Chain": {
            "description": "Second agent validates first agent's work",
            "workflow": [
                {"from": "start", "to": "claude"},
                {"from": "claude", "to": "gemini"},
                {"from": "gemini", "to": "validator"},
                {"from": "validator", "to": "end"}
            ],
            "use_case": "Quality assurance and verification"
        }
    }
    
    for name, pattern in patterns.items():
        print(f"\n📌 {name}")
        print(f"   Description: {pattern['description']}")
        print(f"   Use case: {pattern['use_case']}")
        print("   Workflow:")
        for edge in pattern['workflow']:
            print(f"     {edge['from']} → {edge['to']}")

def demo_mission_examples():
    """Show example missions for different scenarios"""
    print("\n" + "="*60)
    print("📝 DEMO 3: Mission Examples")
    print("="*60)
    
    missions = [
        {
            "name": "Security Audit",
            "mission": """Perform a comprehensive security audit on the provided code:
1. Identify all security vulnerabilities (SQL injection, XSS, etc.)
2. Check for insecure dependencies
3. Review authentication and authorization patterns
4. Suggest specific fixes with code examples
5. Prioritize issues by severity""",
            "workflow": "Sequential Analysis"
        },
        
        {
            "name": "Performance Optimization",
            "mission": """Analyze the code for performance bottlenecks:
1. Identify inefficient algorithms and data structures
2. Find memory leaks or excessive memory usage
3. Suggest caching strategies
4. Provide optimized code alternatives
5. Estimate performance improvements""",
            "workflow": "Sequential Analysis"
        },
        
        {
            "name": "Documentation Generation",
            "mission": """Generate comprehensive documentation:
1. Create function and class docstrings
2. Generate API documentation
3. Write usage examples
4. Create a README with setup instructions
5. Add inline comments for complex logic""",
            "workflow": "Single Agent"
        },
        
        {
            "name": "Test Suite Creation",
            "mission": """Create a comprehensive test suite:
1. Write unit tests for all functions
2. Create integration tests
3. Add edge case tests
4. Generate test data fixtures
5. Set up continuous integration config""",
            "workflow": "Sequential Analysis"
        },
        
        {
            "name": "Refactoring Plan",
            "mission": """Create a detailed refactoring plan:
1. Identify code smells and anti-patterns
2. Suggest design pattern implementations
3. Break down monolithic functions
4. Improve naming and code organization
5. Create a step-by-step refactoring guide""",
            "workflow": "Sequential Analysis"
        }
    ]
    
    for example in missions:
        print(f"\n🎯 {example['name']}")
        print(f"   Workflow: {example['workflow']}")
        print(f"   Mission:")
        for line in example['mission'].strip().split('\n'):
            print(f"      {line}")

def demo_real_world_scenario():
    """Demonstrate a real-world scenario"""
    print("\n" + "="*60)
    print("🌟 DEMO 4: Real-World Scenario - API Endpoint Analysis")
    print("="*60)
    
    # Create a realistic API endpoint
    api_code = """
from flask import Flask, request, jsonify
import sqlite3
import hashlib
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = "hardcoded-secret-key"  # Security issue

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # SQL injection vulnerability
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT id, password_hash FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    if user:
        # Weak password hashing
        password_hash = hashlib.md5(password.encode()).hexdigest()
        if password_hash == user[1]:
            # JWT with no expiration
            token = jwt.encode({'user_id': user[0]}, SECRET_KEY)
            return jsonify({'token': token})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    # No authentication check
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Another SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    user = cursor.fetchone()
    
    if user:
        # Exposing sensitive data
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'password_hash': user[3],  # Should never expose this
            'api_key': user[4]
        })
    
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/data/export', methods=['GET'])
def export_data():
    format = request.args.get('format', 'json')
    
    # Command injection vulnerability
    import os
    if format == 'csv':
        os.system(f"python export.py --format {format} > export.csv")
        return send_file('export.csv')
    
    # Inefficient data loading
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    
    # Loading everything into memory
    all_data = cursor.fetchall()
    
    return jsonify(all_data)
"""
    
    # Save the API code
    with open("/tmp/demo_code/api_endpoint.py", "w") as f:
        f.write(api_code)
    
    print("📱 Created realistic API endpoint with multiple issues:")
    print("   - Multiple SQL injection vulnerabilities")
    print("   - Hardcoded secrets")
    print("   - Weak password hashing (MD5)")
    print("   - Missing authentication")
    print("   - Command injection")
    print("   - Performance issues")
    print("   - Sensitive data exposure")
    
    print("\n🎯 Mission: Comprehensive security and performance audit")
    
    # This would normally call the actual multi-agent system
    print("\n🤖 Multi-Agent Analysis Process:")
    print("   1. Claude performs initial security scan")
    print("   2. Identifies critical vulnerabilities")
    print("   3. Gemini enhances with specific fixes")
    print("   4. Provides refactored secure code")
    print("   5. Generates security report")
    
    print("\n📊 Expected Outcomes:")
    print("   ✓ Parameterized queries to prevent SQL injection")
    print("   ✓ Environment variables for secrets")
    print("   ✓ bcrypt for password hashing")
    print("   ✓ JWT expiration and refresh tokens")
    print("   ✓ Authentication middleware")
    print("   ✓ Input validation and sanitization")
    print("   ✓ Pagination for data export")
    print("   ✓ Rate limiting recommendations")

def main():
    """Run all demos"""
    print("🚀 Multi-Agent System Demo Scenarios")
    print("=" * 60)
    
    demos = [
        ("Code Review Workflow", demo_code_review),
        ("Workflow Patterns", demo_workflow_patterns),
        ("Mission Examples", demo_mission_examples),
        ("Real-World Scenario", demo_real_world_scenario)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{'='*60}")
        print(f"Running Demo {i}/{len(demos)}: {name}")
        print("="*60)
        
        try:
            demo_func()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        
        if i < len(demos):
            print("\n[Continuing to next demo...]")
    
    print("\n" + "="*60)
    print("✅ All demos completed!")
    print("\n📚 Summary:")
    print("   - Code review with security and performance analysis")
    print("   - Multiple workflow patterns for different use cases")
    print("   - Practical mission examples")
    print("   - Real-world API security audit scenario")
    print("\n🔗 Next Steps:")
    print("   1. Start the system: ./start_production.sh")
    print("   2. Run example: python examples/log_analysis_example.py")
    print("   3. Access dashboard: http://localhost:8000/docs")

if __name__ == "__main__":
    main()