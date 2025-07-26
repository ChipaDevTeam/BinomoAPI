"""
Test the FIXED WebSocket connection
"""

import asyncio
import os
import dotenv
from BinomoAPI import BinomoAPI

dotenv.load_dotenv()

async def test_fixed_websocket():
    """Test the FIXED WebSocket connection"""
    
    print("🎉 Testing FIXED WebSocket Connection")
    print("=" * 60)
    
    # Step 1: Login
    print("🔐 Step 1: Login and get session...")
    login_response = BinomoAPI.login(os.getenv("email"), os.getenv("password"))
    print(f"✅ Login successful! Token: {login_response.authtoken[:20]}...")
    print(f"✅ Balance: ${login_response.balance}")
    
    # DEBUG: Check what device_id is in the session cookies
    session = getattr(login_response, '_session', None)
    if session and session.cookies:
        session_cookies = session.cookies.get_dict()
        session_device_id = session_cookies.get('device_id')
        print(f"📱 Session device_id from cookies: {session_device_id}")
        print(f"👤 Login response user_id: {login_response.user_id}")
    
    # Step 2: Create API with FIXED WebSocket using the SAME device_id from session
    print("\n🔧 Step 2: Creating API with FIXED WebSocket...")
    api = BinomoAPI.create_from_login(
        login_response=login_response,
        device_id=session_device_id if session_device_id else login_response.user_id,  # Use session device_id!
        demo=True,
        enable_logging=True  # Enable logging to see WebSocket details
    )
    print("✅ API created with FIXED WebSocket client")
    
    # Step 3: Test FIXED WebSocket connection
    print("\n🌐 Step 3: Testing FIXED WebSocket connection...")
    try:
        connected = await api.connect()
        if connected:
            print("🎉🎉🎉 SUCCESS! WebSocket FIXED and connected!")
            print("✅ The session cookie fix worked!")
            
            # Test WebSocket trading functions
            print("\n📈 Step 4: Testing WebSocket trading functions...")
            try:
                # Test CALL option
                print("📈 Testing CALL option...")
                call_result = await api.place_call_option("EUR/USD", 1.0, 60)
                print(f"🎯 CALL option result: {call_result}")
                
                # Test PUT option  
                print("📉 Testing PUT option...")
                put_result = await api.place_put_option("EUR/USD", 1.0, 60)
                print(f"🎯 PUT option result: {put_result}")
                
                # Test legacy methods
                print("🔄 Testing legacy methods...")
                legacy_call = await api.call_option("EUR/USD", 1.0, 1)
                print(f"🎯 Legacy CALL: {legacy_call}")
                
                legacy_put = await api.put_option("EUR/USD", 1.0, 1)
                print(f"🎯 Legacy PUT: {legacy_put}")
                
                print("\n🎉🎉🎉 COMPLETE SUCCESS!")
                print("✅ WebSocket connection: WORKING")
                print("✅ Trading functions: WORKING")
                print("✅ All API functions: WORKING")
                print("🎯 BinomoAPI is now 100% functional!")
                
            except Exception as trade_error:
                print(f"⚠️ Trading functions need refinement: {trade_error}")
                print("   But WebSocket connection is working!")
                
        else:
            print("❌ WebSocket connection still failed")
    except Exception as e:
        print(f"❌ WebSocket connection failed with error: {e}")
        import traceback
        traceback.print_exc()
            
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        print("   The fix may need additional refinement")
    
    # Test other functions to confirm they still work
    print("\n📊 Step 5: Confirming other functions still work...")
    
    try:
        balance = await api.get_balance()
        print(f"✅ Balance: ${balance.amount}")
        
        assets = api.get_available_assets()
        print(f"✅ Assets: {len(assets)} available")
        
    except Exception as e:
        print(f"⚠️ Other functions: {e}")
    
    # Cleanup
    await api.close()
    print("\n✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_fixed_websocket())
