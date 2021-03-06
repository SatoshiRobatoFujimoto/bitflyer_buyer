import base64
import boto3
import logging
import os
import pybitflyer
from collections import namedtuple

def get_credencials():
    kms = boto3.client('kms')
    key = kms.decrypt(CiphertextBlob = base64.b64decode(os.environ["BITFLYER_API_KEY"]))['Plaintext']
    secret = kms.decrypt(CiphertextBlob = base64.b64decode(os.environ["BITFLYER_API_SECRET"]))['Plaintext']
    result = namedtuple('Credencials', ['key', 'secret'])
    return result(key = key, secret = secret)

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    credencials = get_credencials()
    api = pybitflyer.API(api_key = credencials.key, api_secret = credencials.secret)

    response = api.ticker(product_code="BTC_JPY")
    price = response['best_bid']

    size = round(float(os.environ["BITFLYER_PURCHASE_SIZE_IN_JPY"]) / price, 3)
    logger.info("purchase_size: " + str(size))

    response = api.sendchildorder(
      product_code = "BTC_JPY",
      child_order_type = "MARKET",
      side = "BUY",
      size = size
    )

    logger.info(response)
