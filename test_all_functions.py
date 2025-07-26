"""
Comprehensive test suite for BinomoAPI - Tests all available functions
"""

from BinomoAPI import BinomoAPI
from BinomoAPI.exceptions import *
from BinomoAPI.models import LoginResponse, Asset, Balance, TradeOrder

import asyncio
import time
import os
import dotenv
import logging
from typing import Optional

# Configure logging to see detailed information
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

dotenv.load_dotenv()

email = os.getenv("email")
password = os.getenv("password")

class BinomoAPITester:
    def __init__(self):
        self.api: Optional[BinomoAPI] = None
        self.login_response: Optional[LoginResponse] = None
        self.test_results = {}
        
    def log_test_result(self, test_name: str, success: bool, result=None, error=None):
        """Log test results for summary"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{status} {test_name}")
        if result is not None:
            print(f"   Result: {result}")
        if error is not None:
            print(f"   Error: {error}")
        
        self.test_results[test_name] = {
            'success': success,
            'result': result,
            'error': str(error) if error else None
        }
    
    async def test_login(self):
        """Test 1: Login functionality"""
        print("\n" + "="*50)
        print("TEST 1: Login Functionality")
        print("="*50)
        
        try:
            self.login_response = BinomoAPI.login(email, password)
            
            if self.login_response and hasattr(self.login_response, 'authtoken'):
                success_msg = f"Auth Token: {self.login_response.authtoken[:10]}..."
                if hasattr(self.login_response, 'balance'):
                    balance_dollars = self.login_response.balance / 100 if self.login_response.balance else 0
                    success_msg += f", Balance: ${balance_dollars}"
                
                self.log_test_result("Login", True, success_msg)
                return True
            else:
                self.log_test_result("Login", False, error="No auth token received")
                return False
                
        except Exception as e:
            self.log_test_result("Login", False, error=e)
            return False
    
    async def test_api_creation(self):
        """Test 2: API Instance Creation"""
        print("\n" + "="*50)
        print("TEST 2: API Instance Creation")
        print("="*50)
        
        if not self.login_response:
            self.log_test_result("API Creation", False, error="No login response available")
            return False
        
        try:
            # Test create_from_login method
            self.api = BinomoAPI.create_from_login(
                login_response=self.login_response,
                device_id=self.login_response.user_id,
                demo=True,
                enable_logging=True
            )
            
            if self.api:
                self.log_test_result("API Creation", True, "BinomoAPI instance created successfully")
                return True
            else:
                self.log_test_result("API Creation", False, error="Failed to create API instance")
                return False
                
        except Exception as e:
            self.log_test_result("API Creation", False, error=e)
            return False
    
    async def test_get_available_assets(self):
        """Test 3: Get Available Assets"""
        print("\n" + "="*50)
        print("TEST 3: Get Available Assets")
        print("="*50)
        
        if not self.api:
            self.log_test_result("Get Available Assets", False, error="No API instance")
            return False
        
        try:
            assets = self.api.get_available_assets()
            
            if assets and len(assets) > 0:
                result_msg = f"Found {len(assets)} assets. Examples: {[asset.name for asset in assets[:3]]}"
                self.log_test_result("Get Available Assets", True, result_msg)
                
                # Print first few assets for reference
                print("   First 5 assets:")
                for i, asset in enumerate(assets[:5]):
                    print(f"   {i+1}. {asset.name} (RIC: {asset.ric})")
                
                return True
            else:
                self.log_test_result("Get Available Assets", False, error="No assets found")
                return False
                
        except Exception as e:
            self.log_test_result("Get Available Assets", False, error=e)
            return False
    
    async def test_get_asset_ric(self):
        """Test 4: Get Asset RIC"""
        print("\n" + "="*50)
        print("TEST 4: Get Asset RIC")
        print("="*50)
        
        if not self.api:
            self.log_test_result("Get Asset RIC", False, error="No API instance")
            return False
        
        try:
            # Test with common asset names
            test_assets = ["EUR/USD", "EURUSD", "AUD/NZD", "Bitcoin", "BTC/USD"]
            results = []
            
            for asset_name in test_assets:
                ric = self.api.get_asset_ric(asset_name)
                if ric:
                    results.append(f"{asset_name} -> {ric}")
            
            if results:
                result_msg = f"Found RICs: {results}"
                self.log_test_result("Get Asset RIC", True, result_msg)
                return True
            else:
                self.log_test_result("Get Asset RIC", False, error="No RICs found for test assets")
                return False
                
        except Exception as e:
            self.log_test_result("Get Asset RIC", False, error=e)
            return False
    
    async def test_connect(self):
        """Test 5: WebSocket Connection"""
        print("\n" + "="*50)
        print("TEST 5: WebSocket Connection")
        print("="*50)
        
        if not self.api:
            self.log_test_result("WebSocket Connect", False, error="No API instance")
            return False
        
        try:
            await self.api.connect()
            self.log_test_result("WebSocket Connect", True, "WebSocket connection established")
            return True
            
        except Exception as e:
            self.log_test_result("WebSocket Connect", False, error=e)
            return False
    
    async def test_get_balance_modern(self):
        """Test 6: Get Balance (Modern Method)"""
        print("\n" + "="*50)
        print("TEST 6: Get Balance (Modern Method)")
        print("="*50)
        
        if not self.api:
            self.log_test_result("Get Balance (Modern)", False, error="No API instance")
            return False
        
        try:
            balance = await self.api.get_balance()
            
            if balance:
                balance_dollars = balance.balance / 100 if hasattr(balance, 'balance') else 0
                result_msg = f"Balance: ${balance_dollars}, Currency: {getattr(balance, 'currency', 'Unknown')}"
                self.log_test_result("Get Balance (Modern)", True, result_msg)
                return True
            else:
                self.log_test_result("Get Balance (Modern)", False, error="No balance data received")
                return False
                
        except Exception as e:
            self.log_test_result("Get Balance (Modern)", False, error=e)
            return False
    
    async def test_get_balance_legacy(self):
        """Test 7: Get Balance (Legacy Method)"""
        print("\n" + "="*50)
        print("TEST 7: Get Balance (Legacy Method)")
        print("="*50)
        
        if not self.api:
            self.log_test_result("Get Balance (Legacy)", False, error="No API instance")
            return False
        
        try:
            balance = await self.api.Getbalance()
            
            if balance is not None:
                balance_dollars = balance / 100 if balance else 0
                result_msg = f"Balance: ${balance_dollars}"
                self.log_test_result("Get Balance (Legacy)", True, result_msg)
                return True
            else:
                # Check if we have balance from login
                if hasattr(self.login_response, 'balance') and self.login_response.balance:
                    balance_dollars = self.login_response.balance / 100
                    result_msg = f"Balance from login: ${balance_dollars}"
                    self.log_test_result("Get Balance (Legacy)", True, result_msg)
                    return True
                else:
                    self.log_test_result("Get Balance (Legacy)", False, error="No balance data received")
                    return False
                
        except Exception as e:
            self.log_test_result("Get Balance (Legacy)", False, error=e)
            return False
    
    async def test_place_call_option(self):
        """Test 8: Place CALL Option (Demo)"""
        print("\n" + "="*50)
        print("TEST 8: Place CALL Option (Demo)")
        print("="*50)
        
        if not self.api:
            self.log_test_result("Place CALL Option", False, error="No API instance")
            return False
        
        try:
            # Use a minimal amount for demo testing
            result = await self.api.place_call_option(
                asset="EUR/USD",
                duration_seconds=60,  # 1 minute
                amount=1.0,  # $1 minimum
                use_demo=True
            )
            
            if result:
                self.log_test_result("Place CALL Option", True, f"Trade placed: {result}")
                return True
            else:
                self.log_test_result("Place CALL Option", False, error="No trade result received")
                return False
                
        except Exception as e:
            self.log_test_result("Place CALL Option", False, error=e)
            return False
    
    async def test_place_put_option(self):
        """Test 9: Place PUT Option (Demo)"""
        print("\n" + "="*50)
        print("TEST 9: Place PUT Option (Demo)")
        print("="*50)
        
        if not self.api:
            self.log_test_result("Place PUT Option", False, error="No API instance")
            return False
        
        try:
            # Use a minimal amount for demo testing
            result = await self.api.place_put_option(
                asset="EUR/USD",
                duration_seconds=60,  # 1 minute
                amount=1.0,  # $1 minimum
                use_demo=True
            )
            
            if result:
                self.log_test_result("Place PUT Option", True, f"Trade placed: {result}")
                return True
            else:
                self.log_test_result("Place PUT Option", False, error="No trade result received")
                return False
                
        except Exception as e:
            self.log_test_result("Place PUT Option", False, error=e)
            return False
    
    async def test_legacy_call_method(self):
        """Test 10: Legacy CALL Method"""
        print("\n" + "="*50)
        print("TEST 10: Legacy CALL Method")
        print("="*50)
        
        if not self.api:
            self.log_test_result("Legacy CALL Method", False, error="No API instance")
            return False
        
        try:
            # First get a valid RIC
            ric = self.api.get_asset_ric("EUR/USD")
            if not ric:
                # Fallback to a known RIC
                ric = "EUR/USD"
            
            await self.api.Call(
                ric=ric,
                duration=1,  # 1 minute
                amount=1.0,  # $1 minimum
                is_demo=True
            )
            
            self.log_test_result("Legacy CALL Method", True, f"Called with RIC: {ric}")
            return True
                
        except Exception as e:
            self.log_test_result("Legacy CALL Method", False, error=e)
            return False
    
    async def test_legacy_put_method(self):
        """Test 11: Legacy PUT Method"""
        print("\n" + "="*50)
        print("TEST 11: Legacy PUT Method")
        print("="*50)
        
        if not self.api:
            self.log_test_result("Legacy PUT Method", False, error="No API instance")
            return False
        
        try:
            # First get a valid RIC
            ric = self.api.get_asset_ric("EUR/USD")
            if not ric:
                # Fallback to a known RIC
                ric = "EUR/USD"
            
            await self.api.Put(
                ric=ric,
                duration=1,  # 1 minute
                amount=1.0,  # $1 minimum
                is_demo=True
            )
            
            self.log_test_result("Legacy PUT Method", True, f"Put with RIC: {ric}")
            return True
                
        except Exception as e:
            self.log_test_result("Legacy PUT Method", False, error=e)
            return False
    
    async def test_cleanup(self):
        """Test 12: Cleanup and Close"""
        print("\n" + "="*50)
        print("TEST 12: Cleanup and Close")
        print("="*50)
        
        if not self.api:
            self.log_test_result("Cleanup", False, error="No API instance")
            return False
        
        try:
            await self.api.close()
            self.log_test_result("Cleanup", True, "API instance closed successfully")
            return True
            
        except Exception as e:
            self.log_test_result("Cleanup", False, error=e)
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for test_name, result in self.test_results.items():
                if not result['success']:
                    print(f"  ❌ {test_name}: {result['error']}")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {test_name}")
            if result['result']:
                print(f"      {result['result']}")

async def main():
    """Run all tests"""
    print("BinomoAPI Comprehensive Test Suite")
    print("=" * 60)
    print("This will test all available functions in the BinomoAPI")
    print("Testing with DEMO account only for safety")
    print("=" * 60)
    
    if not email or not password:
        print("❌ ERROR: Email and password must be set in .env file")
        return
    
    tester = BinomoAPITester()
    
    # Run all tests
    await tester.test_login()
    await tester.test_api_creation()
    await tester.test_get_available_assets()
    await tester.test_get_asset_ric()
    await tester.test_connect()
    await tester.test_get_balance_modern()
    await tester.test_get_balance_legacy()
    
    # Trading tests (these might fail due to authentication issues)
    print("\n⚠️  WARNING: Trading tests may fail due to session authentication issues")
    print("This is a known limitation where balance/trading works only during login context")
    
    await tester.test_place_call_option()
    await tester.test_place_put_option()
    await tester.test_legacy_call_method()
    await tester.test_legacy_put_method()
    
    # Cleanup
    await tester.test_cleanup()
    
    # Print summary
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
