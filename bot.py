from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware, construct_sign_and_send_raw_middleware
import json, os
from dotenv import load_dotenv
from time import sleep
import random
load_dotenv()

private_key = os.getenv('priv')
rpc = os.getenv('rpc')
with open('abi.json') as json_file:
    abi = json.load(json_file)
with open('wavax.json') as wavax_file:
    wavax_abi = json.load(wavax_file)
with open('usdc.json') as usdc_file:
    usdc_abi = json.load(usdc_file)

w3 = Web3(HTTPProvider("https://speedy-nodes-nyc.moralis.io/60e28d167e26cfc4e87ed912/avalanche/testnet"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(private_key))
w3.eth.default_account = w3.eth.account.privateKeyToAccount(private_key).address


swap_address = "0xabFD6Cf3f7381b6F1D75fB66fd30b930E51b3d9D"
USDC = "0xa9d19d5e8712C1899C4344059FD2D873a3e2697E"
WVAX = "0xd00ae08403B9bbb9124bB305C09058E32C39A48c"
AVAX_USDC = [w3.toChecksumAddress(WVAX), w3.toChecksumAddress(USDC)]
USDC_AVAX = [w3.toChecksumAddress(USDC), w3.toChecksumAddress(WVAX)]

swap = w3.eth.contract(address=swap_address, abi=abi)
usdc = w3.eth.contract(address=USDC, abi=usdc_abi)

def avax_usdc(avax_amount, deadline):
    tx = swap.functions.swapExactAVAXForTokens(
        0,
        AVAX_USDC,
        w3.eth.default_account,
        deadline
    ).transact(
        {
            'from': w3.eth.default_account,
            'value': avax_amount
        }
    )
    return tx

def usdc_avax(usdc_amount, deadline):
    tx = swap.functions.swapExactTokensForAVAX(
    usdc_amount,
    0,
    USDC_AVAX,
    w3.eth.default_account,
    deadline
    ).transact(
        {
            'from':w3.eth.default_account
        }
    )
    return tx

while True:
    try:
        balance = w3.eth.get_balance(w3.eth.default_account)
        timestamp = w3.eth.getBlock('latest').timestamp
        deadline = timestamp + random.randint(200, 250) * 110
        avax_amount = w3.toWei(random.uniform(0.2,0.3), 'ether')
        usdc_amount = w3.toWei(random.uniform(0.2,0.3), 'ether')
        if balance >= w3.toWei(1.9, 'ether'):
            tx = avax_usdc(avax_amount, deadline)
            print("Swapping {} AVAX for {} USDC".format(w3.fromWei(avax_amount,'ether'), w3.fromWei(usdc_amount,'ether')))
            print("Tx: {}".format(tx.hex()))
            print("Waiting for tx to be mined...")
            print("==================================")
        else:
            usdc_balance = usdc.functions.balanceOf(w3.eth.default_account).call()
#             if usdc_balance >= w3.toWei(0.4, 'ether'):
#                 tx = usdc_avax(usdc_amount, deadline)
#                 print("Swapping {} USDC for {} AVAX".format(w3.fromWei(usdc_amount,'ether'), w3.fromWei(avax_amount,'ether')))
#                 print("Tx: {}".format(tx.hex()))
#                 print("Waiting for tx to be mined...")
#                 print("==================================")
#             else:
#                 tx = avax_usdc(avax_amount, deadline)
#                 print("Swapping {} AVAX for {} USDC".format(w3.fromWei(avax_amount,'ether'), w3.fromWei(usdc_amount,'ether')))
#                 print("Tx: {}".format(tx.hex()))
#                 print("Waiting for tx to be mined...")
#                 print("==================================")
            tx = usdc_avax(usdc_balance, deadline)
            print("Swapping {} USDC for {} AVAX".format(w3.fromWei(usdc_amount,'ether'), w3.fromWei(avax_amount,'ether')))
            print("Tx: {}".format(tx.hex()))
            print("Waiting for tx to be mined...")
            print("==================================")
        sleep(10)
    except ValueError:
        pass
