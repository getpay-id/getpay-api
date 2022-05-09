from app.extensions.mongodb import getpay_db

users = getpay_db.users
api_keys = getpay_db.api_keys
payment_gateway = getpay_db.payment_gateway
payment_method = getpay_db.payment_method
payment_channel = getpay_db.payment_channel
transactions = getpay_db.transactions
