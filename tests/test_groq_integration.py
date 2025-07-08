#!/usr/bin/env python3
"""
Test script to verify Groq API integration
"""

import os
import sys
import unittest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.ai_chat import AIChatManager

class TestGroqIntegration(unittest.TestCase):
    """Test cases for Groq API integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.groq_key = os.getenv('GROQ_API_KEY')
        
    def test_groq_api_key_exists(self):
        """Test that Groq API key is configured"""
        self.assertIsNotNone(self.groq_key, "GROQ_API_KEY not found in environment variables")
        self.assertTrue(self.groq_key.startswith('gsk_'), "Groq API key should start with 'gsk_'")
        
    def test_ai_chat_manager_initialization(self):
        """Test that AI Chat Manager initializes with Groq"""
        if not self.groq_key:
            self.skipTest("GROQ_API_KEY not configured")
            
        chat_manager = AIChatManager()
        self.assertEqual(chat_manager.api_type, "groq")
        self.assertIsNotNone(chat_manager.model)
        
    def test_basic_chat_functionality(self):
        """Test basic chat functionality with Groq"""
        if not self.groq_key:
            self.skipTest("GROQ_API_KEY not configured")
            
        chat_manager = AIChatManager()
        chat_manager.start_session()
        
        response = chat_manager.send_message("Hello! Please respond with just 'Test successful'")
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
    def test_task_step_generation(self):
        """Test task step generation with Groq"""
        if not self.groq_key:
            self.skipTest("GROQ_API_KEY not configured")
            
        chat_manager = AIChatManager()
        steps = chat_manager.generate_task_steps("Open a web browser and go to google.com")
        
        self.assertIsInstance(steps, list)
        self.assertGreater(len(steps), 0)
        
        # Check that each step has required fields
        for step in steps:
            self.assertIsInstance(step, dict)
            self.assertIn('step_number', step)
            self.assertIn('action', step)
            self.assertIn('description', step)

def run_groq_tests():
    """Run Groq integration tests"""
    print("Running Groq API integration tests...")
    
    # Check if Groq API key is set
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        print("Please set your Groq API key in the .env file:")
        print("GROQ_API_KEY=your_groq_api_key_here")
        return False
    
    # Run the tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGroqIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n🎉 All Groq integration tests passed!")
        return True
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return False

if __name__ == "__main__":
    success = run_groq_tests()
    sys.exit(0 if success else 1)#!/usr/bin/env python3
"""
Test script to verify Groq API integration
"""

import os
import sys
import unittest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.ai_chat import AIChatManager

class TestGroqIntegration(unittest.TestCase):
    """Test cases for Groq API integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.groq_key = os.getenv('GROQ_API_KEY')
        
    def test_groq_api_key_exists(self):
        """Test that Groq API key is configured"""
        self.assertIsNotNone(self.groq_key, "GROQ_API_KEY not found in environment variables")
        self.assertTrue(self.groq_key.startswith('gsk_'), "Groq API key should start with 'gsk_'")
        
    def test_ai_chat_manager_initialization(self):
        """Test that AI Chat Manager initializes with Groq"""
        if not self.groq_key:
            self.skipTest("GROQ_API_KEY not configured")
            
        chat_manager = AIChatManager()
        self.assertEqual(chat_manager.api_type, "groq")
        self.assertIsNotNone(chat_manager.model)
        
    def test_basic_chat_functionality(self):
        """Test basic chat functionality with Groq"""
        if not self.groq_key:
            self.skipTest("GROQ_API_KEY not configured")
            
        chat_manager = AIChatManager()
        chat_manager.start_session()
        
        response = chat_manager.send_message("Hello! Please respond with just 'Test successful'")
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
    def test_task_step_generation(self):
        """Test task step generation with Groq"""
        if not self.groq_key:
            self.skipTest("GROQ_API_KEY not configured")
            
        chat_manager = AIChatManager()
        steps = chat_manager.generate_task_steps("Open a web browser and go to google.com")
        
        self.assertIsInstance(steps, list)
        self.assertGreater(len(steps), 0)
        
        # Check that each step has required fields
        for step in steps:
            self.assertIsInstance(step, dict)
            self.assertIn('step_number', step)
            self.assertIn('action', step)
            self.assertIn('description', step)

def run_groq_tests():
    """Run Groq integration tests"""
    print("Running Groq API integration tests...")
    
    # Check if Groq API key is set
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        print("Please set your Groq API key in the .env file:")
        print("GROQ_API_KEY=your_groq_api_key_here")
        return False
    
    # Run the tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGroqIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n🎉 All Groq integration tests passed!")
        return True
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return False

if __name__ == "__main__":
    success = run_groq_tests()
    sys.exit(0 if success else 1)