#!/usr/bin/env python3
"""
Test the enhanced WebSocket authentication system.
"""

import asyncio
import logging
from BinomoAPI import BinomoAPI

async def test_enhanced_websocket():
    """Test the enhanced WebSocket authentication system."""
    
    print("🚀 Testing Enhanced WebSocket Authentication")
    print("=" * 60)
    
    # Enable detailed logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Step 1: Login and create API instance
        print("🔐 Step 1: Login and API creation...")
        login_response = await BinomoAPI.login("testUser", "testPassword")
        
        api = BinomoAPI.create_from_login(
            login_response=login_response,
            demo=True,
            enable_logging=True,
            log_level=logging.INFO
        )
        
        print(f"✅ API created with token: {login_response.authtoken[:10]}...")
        
        # Step 2: Test WebSocket connection
        print("\n📡 Step 2: Testing WebSocket connection...")
        try:
            # This should trigger the enhanced authentication
            await api._ensure_websocket_connection()
            print("✅ WebSocket connection established successfully!")
            
            # Step 3: Test subscribing to channels
            print("\n📺 Step 3: Testing channel subscription...")
            await api.subscribe_to_channels(["balance", "trades"])
            print("✅ Channel subscription successful!")
            
            # Step 4: Test placing a demo trade
            print("\n💰 Step 4: Testing demo trade placement...")
            
            # Get available assets first
            assets = api.get_available_assets()
            if assets:
                test_asset = assets[0]  # Use first available asset
                print(f"Using test asset: {test_asset}")
                
                # Place a small demo trade
                result = await api.buy_call_option(
                    asset_ric=test_asset,
                    amount=1,  # $1 demo trade
                    duration_seconds=60
                )
                
                print(f"✅ Demo trade placed successfully: {result}")
                
            else:
                print("⚠️ No assets available for testing")
            
            print("\n🎉 All WebSocket tests completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
            return False
            
        finally:
            # Cleanup
            await api.close()
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

async def test_websocket_strategies_individually():
    """Test each WebSocket authentication strategy individually."""
    
    print("\n🔍 Testing Individual Authentication Strategies")
    print("=" * 60)
    
    try:
        # Login first
        login_response = await BinomoAPI.login("testUser", "testPassword")
        
        # Import the enhanced client directly
        from BinomoAPI.wss.enhanced_client import EnhancedWebSocketClient
        
        # Create enhanced client
        client = EnhancedWebSocketClient(
            auth_token=login_response.authtoken,
            device_id=login_response.user_id,
            session=login_response._session
        )
        
        # Test each strategy
        strategies = [
            ("Session Cookies", client._auth_strategy_session_cookies),
            ("WAMP Protocol", client._auth_strategy_wamp_protocol),
            ("Post-Connect Auth", client._auth_strategy_post_connect_auth),
            ("Fresh Token", client._auth_strategy_fresh_token),
            ("Alternative Endpoints", client._auth_strategy_alternative_endpoint)
        ]
        
        successful_strategies = []
        
        for name, strategy in strategies:
            print(f"\n🔧 Testing: {name}")
            try:
                success = await strategy()
                if success:
                    print(f"✅ {name} - SUCCESS!")
                    successful_strategies.append(name)
                    await client.close()  # Close before trying next strategy
                else:
                    print(f"❌ {name} - FAILED")
            except Exception as e:
                print(f"❌ {name} - EXCEPTION: {e}")
        
        print(f"\n📊 Results: {len(successful_strategies)}/{len(strategies)} strategies successful")
        if successful_strategies:
            print(f"✅ Working strategies: {', '.join(successful_strategies)}")
        else:
            print("❌ No strategies worked")
        
        return len(successful_strategies) > 0
        
    except Exception as e:
        print(f"❌ Individual strategy testing failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🧪 Enhanced WebSocket Authentication Test Suite")
    print("=" * 70)
    
    # Test 1: Full integration test
    print("\n🔬 Test 1: Full Integration Test")
    success1 = await test_enhanced_websocket()
    
    # Test 2: Individual strategy testing
    print("\n🔬 Test 2: Individual Strategy Testing")
    success2 = await test_websocket_strategies_individually()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 70)
    print(f"Full Integration Test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Individual Strategy Test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 or success2:
        print("\n🎉 WebSocket authentication improvements are working!")
        print("The enhanced system provides better reliability and fallback options.")
    else:
        print("\n⚠️ WebSocket authentication still needs work.")
        print("The server-side authentication mechanism may require browser simulation.")

if __name__ == "__main__":
    asyncio.run(main())
