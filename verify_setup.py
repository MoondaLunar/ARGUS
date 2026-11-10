"""
Verify Ollama model setup and test crawler readiness
"""

import subprocess
import json
import time
import sys
from pathlib import Path

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            print(f"   {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("❌ Ollama is not installed or not in PATH")
        return False

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        print("✅ Ollama service is running")
        return True
    except Exception as e:
        print(f"❌ Ollama service is not running")
        print(f"   Error: {e}")
        return False

def list_models():
    """List available models"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        models = result.stdout.strip().split('\n')[1:]  # Skip header
        print(f"\n📦 Available Models ({len(models)}):")
        for model in models:
            if model.strip():
                print(f"   {model}")
        return models
    except Exception as e:
        print(f"❌ Could not list models: {e}")
        return []

def test_model(model_name):
    """Test if a model responds"""
    try:
        import requests
        
        payload = {
            "model": model_name,
            "prompt": "What is entity relationship detection?",
            "stream": False
        }
        
        print(f"\n🧪 Testing model: {model_name}")
        print("   Sending test prompt... (timeout: 60s)")
        
        start = time.time()
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            tokens = len(result['response'].split())
            print(f"✅ Model responded successfully")
            print(f"   Response time: {elapsed:.1f}s for {tokens} tokens")
            print(f"   Speed: {tokens/elapsed:.1f} tokens/sec")
            return True
        else:
            print(f"❌ Model returned error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Model request timed out after 60s")
        return False
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

def check_crawler_files():
    """Verify crawler files exist"""
    required_files = [
        "trawler_enhanced.py",
        "metadata_extractor.py",
        "analysis_engine.py",
        "requirements.txt"
    ]
    
    print(f"\n📁 Checking crawler files:")
    missing = []
    for file in required_files:
        path = Path(file)
        if path.exists():
            size = path.stat().st_size / 1024  # KB
            print(f"   ✅ {file} ({size:.1f} KB)")
        else:
            print(f"   ❌ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0

def check_dependencies():
    """Check Python dependencies"""
    required = {
        'requests': 'Web requests',
        'beautifulsoup4': 'HTML parsing',
        'PIL': 'Image processing',
        'PyPDF2': 'PDF extraction',
        'fuzzywuzzy': 'Fuzzy matching'
    }
    
    print(f"\n📚 Checking Python dependencies:")
    missing = []
    for package, desc in required.items():
        try:
            __import__(package)
            print(f"   ✅ {package} ({desc})")
        except ImportError:
            print(f"   ❌ {package} ({desc}) - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n   Install missing packages with:")
        print(f"   pip install {' '.join(missing)}")
    
    return len(missing) == 0

def check_ollama_model_config():
    """Check if trawler_enhanced.py has correct model"""
    try:
        with open("trawler_enhanced.py", "r") as f:
            content = f.read()
            if "dolphin-llama3" in content:
                print("\n✅ Crawler configured for Dolphin-llama3")
                return True
            else:
                print("\n⚠️  Could not detect model configuration")
                return False
    except Exception as e:
        print(f"\n❌ Error checking config: {e}")
        return False

def print_summary(checks):
    """Print summary of all checks"""
    total = len(checks)
    passed = sum(1 for v in checks.values() if v)
    
    print("\n" + "="*50)
    print("📊 SETUP VERIFICATION SUMMARY")
    print("="*50)
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ Everything looks good! Ready to crawl!")
        print("\nNext steps:")
        print("  1. python examples.py  # Run test examples")
        print("  2. Configure your target URL and entities")
        print("  3. Run your crawler!")
        return True
    else:
        print("\n⚠️  Some setup items need attention.")
        print("\nFailed checks:")
        for name, result in checks.items():
            if not result:
                print(f"  - {name}")
        return False

def main():
    print("="*50)
    print("🔍 OLLAMA & CRAWLER VERIFICATION")
    print("="*50)
    
    checks = {}
    
    # Run all checks
    checks["Ollama installed"] = check_ollama_installed()
    
    if not checks["Ollama installed"]:
        print("\n❌ Please install Ollama from https://ollama.ai")
        return False
    
    checks["Ollama running"] = check_ollama_running()
    
    if not checks["Ollama running"]:
        print("\n⚠️  Start Ollama service:")
        print("   Windows: Open 'Ollama' from Start Menu")
        print("   Or: ollama serve")
        return False
    
    models = list_models()
    
    # Check for recommended model
    has_mixtral = any("mixtral" in m.lower() for m in models)
    has_old = any("llama3" in m.lower() for m in models)
    
    if not has_mixtral and not has_old:
        print("\n⚠️  No recommended models found. Download one:")
        print("   ollama pull dolphin-mixtral:8x7b  # Recommended")
        print("   OR")
        print("   ollama pull dolphin-llama3         # Current")
        checks["Recommended model"] = False
    else:
        checks["Recommended model"] = True
        
        # Test the best available model
        if has_mixtral:
            checks["Model responds"] = test_model("dolphin-mixtral:8x7b")
        elif has_old:
            checks["Model responds"] = test_model("dolphin-llama3")
    
    checks["Crawler files"] = check_crawler_files()
    checks["Python dependencies"] = check_dependencies()
    checks["Correct model config"] = check_ollama_model_config()
    
    # Print summary
    success = print_summary(checks)
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nVerification cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
