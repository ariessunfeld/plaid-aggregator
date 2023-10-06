import os
import csv
from datetime import datetime

from flask import Flask, request, jsonify, render_template
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from dotenv import load_dotenv

load_dotenv()

# CHANGE THE ENVIRONMENT BETWEEN 'sandbox' AND 'development'
# ==========================================================
# ==========================================================
PLAID_ENV = os.getenv('PLAID_ENVIRONMENT')
# ==========================================================
# ==========================================================
# ==========================================================


PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET_SANDBOX = os.getenv('PLAID_SECRET_SANDBOX')
PLAID_SECRET_DEVELOPMENT = os.getenv('PLAID_SECRET_DEVELOPMENT')
secrets = {'sandbox': PLAID_SECRET_SANDBOX, 'development': PLAID_SECRET_DEVELOPMENT}

app = Flask(__name__)

configuration = plaid.Configuration(
    host=getattr(plaid.Environment, PLAID_ENV.capitalize()),
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': secrets[PLAID_ENV],
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def transform_transaction(raw_transaction):
    """Transform raw transaction data to a more concise format."""
    return {
        'amount': raw_transaction['amount'],
        'date': raw_transaction['date'],
        'description': raw_transaction['name'],
        'category': ' > '.join(raw_transaction['category']),
        'merchant_name': raw_transaction.get('merchant_name', None),
        'payment_channel': raw_transaction['payment_channel']
    }

def save_to_csv(transactions):
    """Save a list of transactions to a CSV file."""
    filename = f'transactions_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['date', 'description', 'category', 'amount', 'merchant_name', 'payment_channel']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)

@app.route('/')
def index():
    return render_template('link.html')

@app.route('/get_access_token', methods=['POST'])
def get_access_token():
    public_token = request.json['public_token']
    # Create a request object for the public token exchange
    exchange_request = plaid.model.item_public_token_exchange_request.ItemPublicTokenExchangeRequest(public_token=public_token)
    # Exchange public token for access token
    exchange_response = client.item_public_token_exchange(item_public_token_exchange_request=exchange_request)
    access_token = exchange_response['access_token']
    
    # For the sake of simplicity, we're just sending it as a response here.
    # In a real application, store the access_token securely associated with the user.
    return jsonify(access_token=access_token)

@app.route('/get_transactions', methods=['POST'])
def get_transactions():
    access_token = request.json['access_token']

    request_obj = TransactionsSyncRequest(
        access_token=access_token,
    )
    response = client.transactions_sync(request_obj)
    transactions = response['added']

    # Retrieve all transactions if paginated
    while (response['has_more']):
        request_obj = TransactionsSyncRequest(
            access_token=access_token,
            cursor=response['next_cursor']
        )
        response = client.transactions_sync(request_obj)
        transactions += response['added']
    
    return jsonify(transactions=transactions)

@app.route('/create_link_token', methods=['POST'])
def create_link_token():
    # Create a link token
    response = client.link_token_create({ 
        'user': {
            # This should be a unique ID for the user
            'client_user_id': 'user-id',
        },
        'client_name': 'Transactions Exporter',
        'products': ['auth', 'transactions'],
        'country_codes': ['US'],
        'language': 'en',
        'webhook': 'https://your-webhook-url.com',  # Optional
    })
    link_token = response['link_token']
    return jsonify(link_token=link_token)

@app.route('/fetch_transactions', methods=['POST'])
def fetch_transactions():
    access_token = request.json['access_token']

    request_obj = TransactionsSyncRequest(
        access_token=access_token,
    )
    response = client.transactions_sync(request_obj)
    transactions = [transform_transaction(transaction.to_dict()) for transaction in response['added']]

    # Retrieve all transactions if paginated
    while (response['has_more']):
        request_obj = TransactionsSyncRequest(
            access_token=access_token,
            cursor=response['next_cursor']
        )
        response = client.transactions_sync(request_obj)
        transactions += [transform_transaction(transaction.to_dict()) for transaction in response['added']]
    
    save_to_csv(transactions)

    return jsonify(transactions=transactions)


if __name__ == '__main__':
    app.run(debug=True)