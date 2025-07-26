"""
Test the corrected WebSocket connection using exact curl parameters
"""

import asyncio
import os
import dotenv
from BinomoAPI import BinomoAPI

dotenv.load_dotenv()

async def test_corrected_websocket():
    """Test WebSocket connection with corrected parameters"""
    
    print("🧪 Testing Corrected WebSocket Connection")
    print("=" * 60)
    
    # Step 1: Login to get real credentials
    print("🔐 Step 1: Login and get real credentials...")
    login_response = BinomoAPI.login(os.getenv("email"), os.getenv("password"))
    print(f"✅ Login successful! Token: {login_response.authtoken[:20]}...")
    print(f"✅ Device ID: {login_response.user_id}")
    
    # Step 2: Create API with corrected WebSocket
    print("\n🔧 Step 2: Creating API with corrected WebSocket...")
    api = BinomoAPI.create_from_login(
        login_response=login_response,
        device_id=login_response.user_id,
        demo=True
    )
    print("✅ API created with corrected WebSocket client")
    
    # Step 3: Test WebSocket connection
    print("\n🌐 Step 3: Testing corrected WebSocket connection...")
    try:
        connected = await api.connect()
        if connected:
            print("🎉 SUCCESS! WebSocket connected with corrected parameters!")
            print("✅ The curl parameters fixed the connection issue!")
            
            # Test a simple WebSocket operation
            print("\n📈 Step 4: Testing WebSocket trading...")
            try:
                # Test place call option
                call_result = await api.place_call_option("EUR/USD", 1.0, 60)
                print(f"✅ CALL option placed successfully: {call_result}")
                
                # Test place put option  
                put_result = await api.place_put_option("EUR/USD", 1.0, 60)
                print(f"✅ PUT option placed successfully: {put_result}")
                
                print("\n🎯 COMPLETE SUCCESS!")
                print("✅ WebSocket connection working")
                print("✅ Trading functions working")
                print("✅ API fully functional!")
                
            except Exception as trade_error:
                print(f"⚠️ Trading error (connection OK): {trade_error}")
                print("   WebSocket connected but trading needs refinement")
                
        else:
            print("❌ WebSocket connection still failed")
            print("   May need additional authentication steps")
            
    except Exception as e:
        print(f"❌ WebSocket connection error: {e}")
        print("🔍 Check if additional authentication is needed")
        
        # Show what we can test that still works
        print("\n📊 Testing non-WebSocket functions...")
        
        # Test balance
        try:
            balance = await api.get_balance()
            print(f"✅ Balance: ${balance.amount}")
        except Exception as be:
            print(f"⚠️ Balance error: {be}")
            
        # Test assets
        try:
            assets = api.get_available_assets()
            print(f"✅ Assets: {len(assets)} available")
        except Exception as ae:
            print(f"⚠️ Assets error: {ae}")
    
    # Cleanup
    await api.close()
    print("\n✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_corrected_websocket())
