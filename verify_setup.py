#!/usr/bin/env python3
"""
Setup Verification Script
Run this to verify that everything is working correctly
"""

import sys
import subprocess
import json

def print_status(message, status="INFO"):
    """Print colored status message"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    color = colors.get(status, colors["INFO"])
    reset = colors["RESET"]
    print(f"{color}[{status}]{reset} {message}")


def check_python_version():
    """Check Python version is 3.8+"""
    print_status("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} ✓", "SUCCESS")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor} is too old. Need 3.8+", "ERROR")
        return False


def check_dependencies():
    """Check required Python packages are installed"""
    print_status("Checking Python dependencies...")
    required = ['clickhouse_connect', 'faker']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print_status(f"  {package} ✓", "SUCCESS")
        except ImportError:
            missing.append(package)
            print_status(f"  {package} ✗", "ERROR")
    
    if missing:
        print_status("Install missing packages: poetry install (or pip install -r requirements.txt)", "WARNING")
        return False
    return True


def check_docker():
    """Check if Docker is running"""
    print_status("Checking Docker...")
    try:
        result = subprocess.run(
            ['docker', 'ps'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_status("Docker is running ✓", "SUCCESS")
            return True
        else:
            print_status("Docker is not running", "ERROR")
            return False
    except FileNotFoundError:
        print_status("Docker not found. Install from https://docker.com", "ERROR")
        return False
    except subprocess.TimeoutExpired:
        print_status("Docker check timed out", "ERROR")
        return False


def check_clickhouse():
    """Check if ClickHouse container is running"""
    print_status("Checking ClickHouse container...")
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=interview-clickhouse', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'interview-clickhouse' in result.stdout:
            print_status("ClickHouse container is running ✓", "SUCCESS")
            return True
        else:
            print_status("ClickHouse container not found. Run: docker-compose up -d", "WARNING")
            return False
    except subprocess.TimeoutExpired:
        print_status("Container check timed out", "ERROR")
        return False


def test_clickhouse_connection():
    """Test connection to ClickHouse"""
    print_status("Testing ClickHouse connection...")
    try:
        import clickhouse_connect
        client = clickhouse_connect.get_client(host='localhost', port=8123)
        result = client.command("SELECT 1")
        if result == 1:
            print_status("ClickHouse connection successful ✓", "SUCCESS")
            
            # Get version
            version = client.command("SELECT version()")
            print_status(f"  ClickHouse version: {version}", "INFO")
            return True
        else:
            print_status("Unexpected response from ClickHouse", "ERROR")
            return False
    except Exception as e:
        print_status(f"Cannot connect to ClickHouse: {e}", "ERROR")
        print_status("Make sure ClickHouse is running: docker-compose up -d", "WARNING")
        return False


def test_event_generator():
    """Test event generator works"""
    print_status("Testing event generator...")
    try:
        from event_generator import RestaurantEventGenerator
        generator = RestaurantEventGenerator(seed=42)
        session = generator.generate_table_session()
        
        if session and 'events' in session and len(session['events']) > 0:
            print_status(f"Generated {len(session['events'])} events ✓", "SUCCESS")
            
            # Show sample event
            sample = session['events'][0]
            print_status(f"  Sample event type: {sample['event_type']}", "INFO")
            return True
        else:
            print_status("Event generation failed", "ERROR")
            return False
    except Exception as e:
        print_status(f"Error testing event generator: {e}", "ERROR")
        return False


def test_mock_stream():
    """Test mock stream interface"""
    print_status("Testing mock stream interface...")
    try:
        from mock_event_stream import MockKafkaConsumer
        print_status("Mock stream import successful ✓", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Error importing mock stream: {e}", "ERROR")
        return False


def generate_sample_data():
    """Generate sample data file"""
    print_status("Generating sample data file...")
    try:
        from event_generator import generate_sample_batch
        generate_sample_batch(num_tables=50, output_file="sample_events.jsonl")
        print_status("Sample data generated: sample_events.jsonl ✓", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Error generating sample data: {e}", "ERROR")
        return False


def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("Interview Exercise Setup Verification")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Python Dependencies", check_dependencies),
        ("Docker", check_docker),
        ("ClickHouse Container", check_clickhouse),
        ("ClickHouse Connection", test_clickhouse_connection),
        ("Event Generator", test_event_generator),
        ("Mock Stream", test_mock_stream),
        ("Sample Data", generate_sample_data),
    ]
    
    results = {}
    for name, check_func in checks:
        print()
        try:
            results[name] = check_func()
        except Exception as e:
            print_status(f"Unexpected error in {name}: {e}", "ERROR")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for name, result in results.items():
        status = "✓" if result else "✗"
        color = "SUCCESS" if result else "ERROR"
        print_status(f"{status} {name}", color)
    
    print(f"\n{passed}/{total} checks passed\n")
    
    if passed == total:
        print_status("🎉 All checks passed! You're ready for the interview.", "SUCCESS")
        print_status("\nNext steps:", "INFO")
        print("  1. Review README.md for exercise overview")
        print("  2. Check QUICKSTART.md for detailed setup")
        print("  3. Start designing your schema!")
        return 0
    else:
        print_status("⚠️  Some checks failed. Please fix the issues above.", "WARNING")
        print_status("\nCommon fixes:", "INFO")
        print("  - Install dependencies: poetry install (or pip install -r requirements.txt)")
        print("  - Start ClickHouse: docker-compose up -d")
        print("  - Check Docker is running: docker ps")
        return 1


if __name__ == "__main__":
    sys.exit(main())
