# API Folder

This folder contains the Flask Blueprints and route definitions for the Simple Bank API.

## Structure

- `accounts.py` — Endpoints related to bank account operations 
- `transactions.py` - Endpoints related to transactions on a bank account
- `users.py` — Endpoints related to user management 
- `__init__.py` — Initializes the API package and can be used to register blueprints.

## How It Works

Each module defines a Flask Blueprint that encapsulates related routes. These blueprints are imported and registered in the main `app.py` file.

## Example

```python
from flask import Flask
from bank.api.accounts import accounts_bp
from bank.api.users import users_bp
from bank.api.transactions import transactions_bp

app = Flask(__name__)
app.register_blueprint(accounts_bp)
app.register_blueprint(users_bp)
app.register_blueprint(transactions_bp)
```