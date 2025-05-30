from BinomoAPI.config.conf import Config
from BinomoAPI.wss.client import WebSocketClient
import requests
import time
import json
import logging

class BinomoAPI:
    @staticmethod
    def login(email: str, password: str, device_id: str = "1b6290ce761c82f3a97189d35d2ed138"):
        """
        Login to Binomo API and return authentication data.
        
        Args:
            email (str): User email
            password (str): User password
            device_id (str): Device ID (optional, uses default if not provided)
            
        Returns:
            dict: Dictionary containing 'authtoken' and 'user_id' if successful
            None: If login failed
        """
        url = 'https://api.binomo.com/passport/v2/sign_in?locale=en'
        
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache, no-store, must-revalidate',
            'content-type': 'application/json',
            'device-id': device_id,
            'device-type': 'web',
            'origin': 'https://binomo.com',
            'priority': 'u=1, i',
            'referer': 'https://binomo.com/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Opera GX";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0',
            'user-timezone': 'America/Santiago'
        }
        
        data_raw = {
            "email": email,
            "password": password,
        }
        
        try:
            response = requests.post(url, headers=headers, json=data_raw)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Check if login was successful and return the data
            if 'data' in response_data and 'authtoken' in response_data['data']:
                return response_data['data']
            else:
                print("Login failed: Invalid response format")
                return None
                
        except requests.exceptions.HTTPError as errh:
            print(f"Http Error: {errh}")
            if hasattr(errh.response, 'content'):
                print(f"Response content: {errh.response.content}")
            return None
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
            return None
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
            return None
        except requests.exceptions.RequestException as err:
            print(f"Request Error: {err}")
            return None
        except json.JSONDecodeError as err:
            print(f"JSON Decode Error: {err}")
            return None

    def __init__(self, AuthToken: str, device_id: str, demo: bool = False, AddLogging: bool = False):
        self.logger = logging.getLogger(__name__) if AddLogging else None
        if AddLogging:
            logging.basicConfig(level=logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
        else:
            self.logger = None

        self.ws = None
        self.walletType = "demo" if demo else "real"
        self.AuthToken = AuthToken
        self.device_id = device_id
        self.config = Config()
        self.ref = 1
        self.assetRic_default = "EURO"

        with open("BinomoAPI/assets.json", "r") as f:
            self.assetList = json.load(f)

        self.api_host = f"{self.config.API_HOST}?authtoken={self.AuthToken}&device=web&device_id={self.device_id}&?v=2&vsn=2.0.0"

        # Connect
        if self.logger:
            self.logger.info("Connecting to Binomo API")
        self.ws = WebSocketClient(self.api_host)
        self.ws.run()
        if self.logger:
            self.logger.info("Connected to Binomo API")

        self.phxJoin()
    def _GetAssetRic(self,asset):
        for i in self.assetList:
            if i["name"] == asset:
                return i["ric"]
    async def connect(self):
        self.ws = WebSocketClient(self.api_host)
        self.ws.run()
    def phxJoin(self):
        self.sendWs('{"topic":"account","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"user","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"base","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"cfd_zero_spread","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"marathon","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"asset:'+self.assetRic_default+'","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.logger.info("Sent all the requests")
    async def Getbalance(self):
        headers = {'device-id': self.device_id, 'device-type': 'web','authorization-token': self.AuthToken, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
        res = requests.get("https://api.binomo.com/bank/v1/read?locale=en",headers=headers).json()
        for i in res["data"]:
            if i["account_type"] == self.walletType:
                return i["amount"]/100
    def sendWs(self,data):
        self.ws.send(data.replace("~~",str(self.ref)))
        self.ref+=1;self.lastSend = time.time()
    
    async def Call(self, ric, duration, amount, is_demo=False):
        duration = int(time.time()) + duration * 1_000_000
        demo_str = None
        if is_demo:
            demo_str = "demo"
        elif not is_demo:
            demo_str = "real"
        payload = {
            "topic": "bo",
            "event": "create",
            "payload": {
                "created_at": int(time.time()),
                "ric": ric,
                "deal_type": demo_str,
                "expire_at": duration,
                "option_type": "turbo",
                "trend": "call",
                "tournament_id": None,
                "is_state": False,
                "amount": amount
            },
            "ref": self.ref+1,
            "join_ref": "9"
        }
        await self.ws.send(json.dumps(payload))
    async def Put(self, ric, duration, amount, is_demo=False):
        duration = int(time.time()) + duration * 1_000_000
        demo_str = None
        if is_demo:
            demo_str = "demo"
        elif not is_demo:
            demo_str = "real"
        payload = {
            "topic": "bo",
            "event": "create",
            "payload": {
                "created_at": int(time.time()),
                "ric": ric,
                "deal_type": demo_str,
                "expire_at": duration,
                "option_type": "turbo",
                "trend": "put",
                "tournament_id": None,
                "is_state": False,
                "amount": amount
            },
            "ref": self.ref+1,
            "join_ref": "9"
        }
        await self.ws.send(json.dumps(payload))

