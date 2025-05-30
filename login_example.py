#!/usr/bin/env python3
"""
Example of how to use the login function from BinomoAPI
"""

from BinomoAPI.api import BinomoAPI

def main():
    # Replace with your actual credentials
    email = "your_email@example.com"
    password = "your_password"
    
    # Login and get authentication data
    login_data = BinomoAPI.login(email, password)
    
    if login_data:
        print("Login successful!")
        print(f"Auth Token: {login_data['authtoken']}")
        print(f"User ID: {login_data['user_id']}")
        
        # Now you can create a BinomoAPI instance with the auth token
        device_id = "1b6290ce761c82f3a97189d35d2ed138"  # or use your own device ID
        api = BinomoAPI(
            AuthToken=login_data['authtoken'],
            device_id=device_id,
            demo=True,  # Set to False for real trading
            AddLogging=True
        )
        
        print("BinomoAPI instance created successfully!")
        
    else:
        print("Login failed!")

if __name__ == "__main__":
    main()
