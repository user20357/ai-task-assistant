#!/usr/bin/env python3
"""
Test script to verify the AI Task Assistant setup
"""

import sys
import os
import importlib.util

def test_python_version():
    """Test Python version"""
    print("🐍 Testing Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def test_imports():
    """Test required imports"""
    print("\n📦 Testing imports...")
    
    required_packages = [
        ('PyQt6', 'PyQt6'),
        ('requests', 'requests'),
        ('PIL', 'Pillow'),
        ('mss', 'mss'),
        ('cv2', 'opencv-python'),
        ('openai', 'openai'),
        ('dotenv', 'python-dotenv')
    ]
    
    all_good = True
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"✅ {package_name} - OK")
        except ImportError:
            print(f"❌ {package_name} - Missing")
            all_good = False
    
    return all_good

def test_env_file():
    """Test environment file"""
    print("\n🔧 Testing configuration...")
    
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("   Please copy .env.example to .env and add your OpenAI API key")
        return False
    
    # Check for OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in .env file")
        return False
    
    if not api_key.startswith('sk-'):
        print("⚠️  OPENAI_API_KEY format looks incorrect")
        return False
    
    print("✅ Configuration - OK")
    return True

def test_app_structure():
    """Test app structure"""
    print("\n📁 Testing app structure...")
    
    required_files = [
        'main.py',
        'src/core/app_manager.py',
        'src/core/ai_chat.py',
        'src/ui/main_window.py',
        'backend/main.py'
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - OK")
        else:
            print(f"❌ {file_path} - Missing")
            all_good = False
    
    return all_good

def test_ai_connection():
    """Test AI API connection (OpenAI/OpenRouter)"""
    print("\n🤖 Testing AI API connection...")
    
    try:
        from dotenv import load_dotenv
        import openai
        
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key or api_key == 'your_openrouter_api_key_here':
            print("⚠️  No API key configured")
            print("   Please get your API key from:")
            print("   - OpenRouter: https://openrouter.ai/keys (cheaper)")
            print("   - OpenAI: https://platform.openai.com/api-keys")
            return False
        
        # Setup client
        base_url = os.getenv('OPENAI_BASE_URL')
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        if base_url:
            client = openai.OpenAI(api_key=api_key, base_url=base_url)
            provider = "OpenRouter"
        else:
            client = openai.OpenAI(api_key=api_key)
            provider = "OpenAI"
        
        # Simple test request
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print(f"✅ {provider} API - OK (Model: {model})")
        return True
        
    except Exception as e:
        print(f"❌ AI API - Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI Task Assistant Setup Test")
    print("=" * 40)
    
    tests = [
        test_python_version,
        test_imports,
        test_app_structure,
        test_env_file,
        test_ai_connection
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("\n✨ Your AI Task Assistant is ready to run!")
        print("   Execute: python main.py")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\n🔧 Please fix the issues above before running the app")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)