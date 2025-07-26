#!/usr/bin/env python3
"""
Browser-based WebSocket Authentication for BinomoAPI.
This uses selenium to establish authenticated WebSocket connections in a real browser context.
"""

import asyncio
import json
import time
from typing import Optional, Dict, Any
import logging

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class BrowserWebSocketAuth:
    """Browser-based WebSocket authentication for Binomo."""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.driver: Optional[webdriver.Chrome] = None
        self.websocket_url = None
        self.auth_headers = {}
        self.cookies = {}
        self.logger = logging.getLogger(__name__)
        
    def setup_browser(self) -> bool:
        """Setup browser with WebSocket monitoring capabilities."""
        if not SELENIUM_AVAILABLE:
            self.logger.error("Selenium not available. Install with: pip install selenium")
            return False
            
        try:
            # Chrome options for WebSocket monitoring
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            # Enable logging to capture network traffic
            caps = DesiredCapabilities.CHROME
            caps['goog:loggingPrefs'] = {'performance': 'ALL'}
            
            # Create driver
            self.driver = webdriver.Chrome(options=chrome_options, desired_capabilities=caps)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ Browser setup successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    async def authenticate_and_capture_websocket(self) -> Dict[str, Any]:
        """Login to Binomo and capture WebSocket authentication data."""
        if not self.driver:
            if not self.setup_browser():
                return {"success": False, "error": "Browser setup failed"}
        
        try:
            self.logger.info("🔐 Starting browser-based authentication...")
            
            # Step 1: Navigate to Binomo
            self.driver.get("https://binomo.com")
            time.sleep(3)
            
            # Step 2: Click Login button
            try:
                login_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'login') or contains(text(), 'Log in') or contains(text(), 'Login')]"))
                )
                login_btn.click()
                self.logger.info("✅ Login button clicked")
                time.sleep(2)
            except Exception as e:
                self.logger.warning(f"Could not find login button: {e}")
            
            # Step 3: Fill in credentials
            try:
                email_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email' i]"))
                )
                email_field.send_keys(self.email)
                
                password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
                password_field.send_keys(self.password)
                
                # Submit form
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button:contains('Log in')")
                submit_btn.click()
                
                self.logger.info("✅ Login form submitted")
                time.sleep(5)  # Wait for login to complete
                
            except Exception as e:
                self.logger.error(f"❌ Login form filling failed: {e}")
                return {"success": False, "error": f"Login failed: {e}"}
            
            # Step 4: Wait for dashboard and capture network data
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda driver: "binomo.com" in driver.current_url and "login" not in driver.current_url
                )
                self.logger.info("✅ Login successful, now capturing WebSocket data...")
                
            except Exception as e:
                self.logger.warning(f"Login verification unclear: {e}")
            
            # Step 5: Capture authentication data
            auth_data = await self._capture_websocket_auth_data()
            
            return auth_data
            
        except Exception as e:
            self.logger.error(f"❌ Authentication process failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _capture_websocket_auth_data(self) -> Dict[str, Any]:
        """Capture WebSocket authentication data from browser network logs."""
        try:
            # Capture cookies
            self.cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
            self.logger.info(f"✅ Captured {len(self.cookies)} cookies")
            
            # Capture local storage
            local_storage = {}
            try:
                local_storage = self.driver.execute_script("return Object.assign({}, localStorage);")
                self.logger.info(f"✅ Captured {len(local_storage)} localStorage items")
            except:
                pass
            
            # Capture session storage  
            session_storage = {}
            try:
                session_storage = self.driver.execute_script("return Object.assign({}, sessionStorage);")
                self.logger.info(f"✅ Captured {len(session_storage)} sessionStorage items")
            except:
                pass
            
            # Monitor network logs for WebSocket connections
            logs = self.driver.get_log('performance')
            websocket_data = []
            
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.webSocketCreated':
                    ws_data = message['message']['params']
                    websocket_data.append(ws_data)
                    self.logger.info(f"🔍 Found WebSocket: {ws_data.get('url', 'Unknown URL')}")
            
            # Try to trigger WebSocket connection by navigating to trading
            try:
                self.driver.execute_script("window.location.href = 'https://binomo.com/trading'")
                time.sleep(5)
                
                # Get additional logs after trading page load
                new_logs = self.driver.get_log('performance')
                for log in new_logs:
                    message = json.loads(log['message'])
                    if message['message']['method'] == 'Network.webSocketCreated':
                        ws_data = message['message']['params']
                        websocket_data.append(ws_data)
                        self.logger.info(f"🔍 Found trading WebSocket: {ws_data.get('url', 'Unknown URL')}")
                        
            except Exception as e:
                self.logger.warning(f"Could not navigate to trading page: {e}")
            
            # Extract authentication token from cookies/storage
            auth_token = None
            for key, value in {**self.cookies, **local_storage, **session_storage}.items():
                if 'auth' in key.lower() or 'token' in key.lower():
                    auth_token = value
                    self.logger.info(f"✅ Found auth token in {key}: {value[:10]}...")
                    break
            
            return {
                "success": True,
                "cookies": self.cookies,
                "local_storage": local_storage,
                "session_storage": session_storage,
                "websocket_connections": websocket_data,
                "auth_token": auth_token,
                "current_url": self.driver.current_url
            }
            
        except Exception as e:
            self.logger.error(f"❌ Data capture failed: {e}")
            return {"success": False, "error": str(e)}
    
    def create_authenticated_websocket_config(self, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create WebSocket configuration from captured browser data."""
        if not auth_data.get("success"):
            return {"success": False, "error": "No valid auth data"}
        
        # Build WebSocket URL with captured auth token
        auth_token = auth_data.get("auth_token")
        if not auth_token:
            # Try to find token in cookies
            cookies = auth_data.get("cookies", {})
            auth_token = cookies.get("authtoken") or cookies.get("auth_token") or cookies.get("token")
        
        if not auth_token:
            return {"success": False, "error": "No auth token found"}
        
        # Build headers from browser data
        headers = {
            'User-Agent': self.driver.execute_script("return navigator.userAgent;"),
            'Origin': 'https://binomo.com',
            'Cookie': '; '.join([f"{k}={v}" for k, v in auth_data.get("cookies", {}).items()])
        }
        
        # Build WebSocket URL
        device_id = auth_data.get("cookies", {}).get("device_id", "browser_device")
        ws_url = f"wss://ws.binomo.com?authtoken={auth_token}&device=web&device_id={device_id}&v=2&vsn=2.0.0"
        
        return {
            "success": True,
            "websocket_url": ws_url,
            "headers": headers,
            "auth_token": auth_token,
            "device_id": device_id
        }
    
    def close(self):
        """Close browser."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("✅ Browser closed")
            except:
                pass

async def test_browser_websocket_auth():
    """Test browser-based WebSocket authentication."""
    print("🌐 Browser-Based WebSocket Authentication Test")
    print("=" * 60)
    
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium not available. Install with:")
        print("   pip install selenium")
        print("   And download ChromeDriver from: https://chromedriver.chromium.org/")
        return False
    
    # Get credentials from environment or user input
    import os
    email = os.getenv("email") or input("Enter Binomo email: ")
    password = os.getenv("password") or input("Enter Binomo password: ")
    
    browser_auth = BrowserWebSocketAuth(email, password)
    
    try:
        # Capture authentication data
        auth_data = await browser_auth.authenticate_and_capture_websocket()
        
        if auth_data.get("success"):
            print("✅ Browser authentication successful!")
            print(f"   Cookies: {len(auth_data.get('cookies', {}))}")
            print(f"   WebSocket connections: {len(auth_data.get('websocket_connections', []))}")
            print(f"   Auth token: {auth_data.get('auth_token', 'Not found')[:10]}...")
            
            # Create WebSocket config
            ws_config = browser_auth.create_authenticated_websocket_config(auth_data)
            
            if ws_config.get("success"):
                print("✅ WebSocket configuration created!")
                print(f"   URL: {ws_config['websocket_url'][:80]}...")
                print(f"   Headers: {len(ws_config['headers'])} items")
                
                # TODO: Test the WebSocket connection with this config
                print("\n🚀 Ready to implement browser-authenticated WebSocket!")
                return True
            else:
                print(f"❌ WebSocket config failed: {ws_config.get('error')}")
                return False
        else:
            print(f"❌ Browser authentication failed: {auth_data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        browser_auth.close()

if __name__ == "__main__":
    asyncio.run(test_browser_websocket_auth())
