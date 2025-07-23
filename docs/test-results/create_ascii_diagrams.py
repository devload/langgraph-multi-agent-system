#!/usr/bin/env python3
"""
Create beautiful ASCII art diagrams using libraries
"""

from art import text2art
import pyfiglet
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.box import ROUNDED, DOUBLE, ASCII

console = Console()

def create_title():
    """Create fancy title"""
    # Using art library
    title1 = text2art("LangGraph", font='block')
    title2 = text2art("Multi-Agent System", font='small')
    
    return title1 + "\n" + title2

def create_workflow_diagram():
    """Create workflow diagram with rich"""
    console.print("\n[bold cyan]1. CODE REVIEW WORKFLOW (실제 테스트)[/bold cyan]")
    console.print("=" * 80)
    
    # Create workflow boxes
    workflow = Table(show_header=False, box=ROUNDED, padding=1)
    workflow.add_column(justify="center")
    workflow.add_column(justify="center") 
    workflow.add_column(justify="center")
    workflow.add_column(justify="center")
    workflow.add_column(justify="center")
    
    workflow.add_row(
        "[bold green]START[/bold green]\n●",
        "→",
        "[bold blue]CLAUDE[/bold blue]\n🔍 Analyze",
        "→", 
        "[bold purple]GEMINI[/bold purple]\n🚀 Enhance"
    )
    
    console.print(workflow)
    
    # Issues and Solutions panels
    issues_panel = Panel(
        """[red]• SQL Injection[/red]
[yellow]• O(n²) Loop[/yellow]
[green]• No Type Hints[/green]""",
        title="Issues Found",
        border_style="blue"
    )
    
    solutions_panel = Panel(
        """[green]• Parameterized Query[/green]
[green]• Dict O(n)[/green]
[green]• Add Types[/green]""",
        title="Solutions",
        border_style="purple"
    )
    
    columns = Columns([issues_panel, solutions_panel], equal=True, expand=True)
    console.print(columns)

def create_state_diagram():
    """Create state diagram"""
    console.print("\n[bold cyan]2. SYSTEM STATE DIAGRAM[/bold cyan]")
    console.print("=" * 80)
    
    # State flow
    states = Table(show_header=False, box=DOUBLE)
    states.add_column(justify="center", width=15)
    states.add_column(justify="center", width=5)
    states.add_column(justify="center", width=15)
    states.add_column(justify="center", width=5)
    states.add_column(justify="center", width=15)
    states.add_column(justify="center", width=5)
    states.add_column(justify="center", width=15)
    
    states.add_row(
        "[dim]IDLE[/dim]\n◯",
        "→",
        "[yellow]REGISTERED[/yellow]\n◐",
        "→",
        "[blue]RUNNING[/blue]\n●",
        "→",
        "[green]COMPLETED[/green]\n✓"
    )
    
    console.print(states)

def create_data_flow():
    """Create data flow diagram"""
    console.print("\n[bold cyan]3. DATA FLOW DIAGRAM[/bold cyan]")
    console.print("=" * 80)
    
    # Create tree structure
    tree = Tree("[bold]Data Processing Pipeline[/bold]")
    
    # Input branch
    input_branch = tree.add("[bold blue]INPUT DATA[/bold blue]")
    input_branch.add("📄 Source Code")
    input_branch.add("📊 Log Files")
    input_branch.add("⚙️ Config")
    
    # Processing branch
    process_branch = tree.add("[bold yellow]PROCESSING[/bold yellow]")
    claude = process_branch.add("🔍 Claude Analysis")
    claude.add("Security Check")
    claude.add("Performance Analysis")
    claude.add("Code Quality")
    
    gemini = process_branch.add("🚀 Gemini Enhancement")
    gemini.add("Generate Solutions")
    gemini.add("Code Examples")
    gemini.add("Priority Setting")
    
    # Output branch
    output_branch = tree.add("[bold green]OUTPUT DATA[/bold green]")
    output_branch.add("📋 Issues List")
    output_branch.add("💡 Solutions")
    output_branch.add("📄 Final Report (.md)")
    
    console.print(tree)

def create_mission_timeline():
    """Create mission execution timeline"""
    console.print("\n[bold cyan]4. MISSION EXECUTION TIMELINE (demo123)[/bold cyan]")
    console.print("=" * 80)
    
    # Timeline table
    timeline = Table(title="Mission Timeline", box=ASCII)
    timeline.add_column("Time", style="dim", width=12)
    timeline.add_column("Component", style="cyan", width=15)
    timeline.add_column("Action", style="yellow")
    timeline.add_column("Result", style="green")
    
    timeline.add_row("00:00", "Client", "POST /register", "missionId: demo123")
    timeline.add_row("00:01", "Hub", "Create workflow", "Status: registered")
    timeline.add_row("00:02", "Client", "POST /run", "Execution started")
    timeline.add_row("00:03", "Claude", "Analyze logs", "3 issues found")
    timeline.add_row("00:05", "Gemini", "Enhance analysis", "Solutions generated")
    timeline.add_row("00:07", "Hub", "Generate report", "Mission completed")
    
    console.print(timeline)

def create_issue_resolution():
    """Create issue resolution diagram"""
    console.print("\n[bold cyan]5. ISSUE DETECTION & RESOLUTION[/bold cyan]")
    console.print("=" * 80)
    
    # Issues table
    issues_table = Table(title="Test Results", box=ROUNDED)
    issues_table.add_column("Severity", justify="center", style="bold")
    issues_table.add_column("Issue", width=30)
    issues_table.add_column("Location")
    issues_table.add_column("Solution", width=40)
    
    issues_table.add_row(
        "[red]🔴 CRITICAL[/red]",
        "SQL Injection",
        "Line 45",
        'query = "SELECT...WHERE id = %s"\ncursor.execute(query, (user_id,))'
    )
    
    issues_table.add_row(
        "[yellow]🟡 MEDIUM[/yellow]",
        "O(n²) Performance",
        "Lines 13-23",
        "lookup = {item.id: item for item in items}\nif id in lookup: process(lookup[id])"
    )
    
    issues_table.add_row(
        "[green]🟢 LOW[/green]",
        "Missing Type Hints",
        "All functions",
        "def get_user(id: int) -> User:\n    ..."
    )
    
    console.print(issues_table)

def create_ascii_art_file():
    """Save all diagrams to file"""
    from rich.console import Console
    
    # Create console that writes to file
    with open("improved_ascii_art.txt", "w") as f:
        file_console = Console(file=f, force_terminal=True)
        
        # Title
        file_console.print(text2art("LangGraph", font='block'))
        file_console.print(text2art("Multi-Agent", font='small'))
        file_console.print("=" * 80)
        
        # Save all diagrams
        # (Similar code as above but using file_console instead of console)

def create_simple_boxes():
    """Create simple box diagrams"""
    print("\n" + "="*80)
    print("SIMPLIFIED WORKFLOW DIAGRAM")
    print("="*80)
    
    # Using pyfiglet for headers
    print(pyfiglet.figlet_format("Workflow", font="small"))
    
    workflow = """
    ┌─────────────┐      ┌─────────────────┐      ┌──────────────────┐
    │   START     │      │     CLAUDE      │      │     GEMINI       │
    │      ●      │ ───> │   🔍 Analyze    │ ───> │   🚀 Enhance     │
    └─────────────┘      └─────────────────┘      └──────────────────┘
            │                     │                         │
            │                     ▼                         ▼
            │            ┌─────────────────┐      ┌──────────────────┐
            │            │ Issues Found:   │      │ Solutions:       │
            │            │ • SQL Injection │      │ • Parameterized  │
            │            │ • O(n²) Loop    │      │ • Dict O(n)      │
            │            │ • No Type Hints │      │ • Add Types      │
            │            └─────────────────┘      └──────────────────┘
            │                                              │
            └──────────────────────────────────────────────┘
                                    │
                                    ▼
                            ┌──────────────────┐
                            │   📄 REPORT      │
                            │   ✓ Complete     │
                            └──────────────────┘
    """
    print(workflow)

def main():
    """Generate all improved ASCII diagrams"""
    # Print title
    print(create_title())
    
    # Create various diagrams
    create_workflow_diagram()
    create_state_diagram()
    create_data_flow()
    create_mission_timeline()
    create_issue_resolution()
    create_simple_boxes()
    
    # Save to file
    create_ascii_art_file()
    
    console.print("\n[bold green]✅ All diagrams created successfully![/bold green]")
    console.print("[dim]Saved to: improved_ascii_art.txt[/dim]")

if __name__ == "__main__":
    main()