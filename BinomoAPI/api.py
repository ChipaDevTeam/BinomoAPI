from BinomoAPI.config.conf import Config
from BinomoAPI.wss.client import WebSocketClient
import requests
import asyncio
import time
import urllib
import datetime

class BinomoAPI:
    def __init__(self, AuthToken: str, device_id: str, demo: bool = False):
        self.ws = None
        self.walletType = None
        if demo:
            self.walletType = "demo"
        else:
            self.walletType = "real"
        self.AuthToken = AuthToken
        self.device_id = device_id
        self.walletType
        self.config = Config()
        self.ref=1

        self.api_host = f"{self.config.API_HOST}?authtoken={self.AuthToken}&device=web&device_id={self.device_id}&?v=2&vsn=2.0.0"

        # connect
        self._connect()
    async def _connect(self):
        self.ws = WebSocketClient(self.api_host)
        self.ws.run()
    def phxJoin(self):
        self.sendWs('{"topic":"account","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"user","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"base","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"cfd_zero_spread","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"marathon","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"asset:'+self.assetRic+'","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
    async def Getbalance(self):
        headers = {'device-id': self.device_id, 'device-type': 'web','authorization-token': self.AuthToken, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
        res = requests.get("https://api.binomo.com/bank/v1/read?locale=en",headers=headers).json()
        for i in res["data"]:
            if i["account_type"] == self.walletType:
                return i["amount"]/100
    def sendWs(self,data):
        self.ws.send(data.replace("~~",str(self.ref)))
        self.ref+=1;self.lastSend = time.time()
    def getHistoryMarket(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        return requests.get("https://api.binomo.com/platform/candles/"+urllib.parse.quote_plus(self.assetRic)+"/"+str(now)+"T00:00:00/60?locale=en",headers=self.headers).json()["data"]
    def parseBidTime(self, m=1):
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:00")
        bid = datetime.datetime.strptime(now, "%d/%m/%Y %H:%M:%S")+datetime.timedelta(minutes=m)
        return str(int(time.mktime(bid.timetuple())))

    def getBid(self, status, amount):
        if int(datetime.datetime.now().strftime("%S")) < 30:bidTime=self.parseBidTime()
        else:bidTime=self.parseBidTime(2)
        self.sendWs('{"topic":"base","event":"create_deal","payload":{"amount":'+str(amount*100)+',"asset":"'+self.assetRic+'","asset_id":'+str(self.assetId)+',"asset_name":"'+self.currency+'","created_at":'+str(int(time.time()))+',"currency_iso":"IDR","deal_type":"'+self.walletType+'","expire_at":'+bidTime+',"option_type":"turbo","tournament_id":null,"trend":"'+status+'","is_state":false},"ref":"~~","join_ref":"~~"}')
