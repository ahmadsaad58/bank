# Simple Bank API

A simple RESTful API for managing users, bank accounts, and transactions. Built with Flask.

---

## Features

- Create a new bank account with an initial deposit (a customer may have multiple accounts)
- Transfer amounts between any two accounts (including those owned by different customers)
- Retrieve balances for a given account
- Retrieve transfer (transaction) history for a given account
- Update or delete accounts
- Manage users

---

## API Endpoints

Visit `/apidocs/#/` to get more info

> Replace `<user_name>`, `<account_name>`, and `<transaction_id>` with actual values.

### User Endpoints

- `POST   /api/v1/users`  
  Create a new user.

- `GET    /api/v1/users/<user_name>`  
  Get user details.

- `GET    /api/v1/users/`  
  Get all user details.

- `PUT    /api/v1/users/<user_name>`  
  Update user details.

- `DELETE /api/v1/users/<user_name>`  
  Delete a user.

---

### Account Endpoints

- `POST   /api/v1/accounts/<user_name>`  
  Create a new account for a user.

- `GET    /api/v1/accounts/`  
  List all accounts.

- `GET    /api/v1/accounts/<user_name>`  
  List all accounts for a user.

- `PUT    /api/v1/accounts/<user_name>/<account_name>`  
  Update account details.

- `DELETE /api/v1/accounts/<user_name>/<account_name>`  
  Delete an account.

---

### Transaction Endpoints

- `POST   /api/v1/accounts/deposit/<user_name>/<account_name>`  
  Deposit money into an account.

- `POST   /api/v1/accounts/withdraw/<user_name>/<account_name>`  
  Withdraw money from an account.

- `POST   /api/v1/accounts/transfer`  
  Transfer money between accounts (provide source and destination in the request body).

- `GET    /api/v1/accounts/<account_name>?balance=true&transactions=true`  
  Get balance and/or transaction history for an account (use query params to specify what to return).

---

## Data Models

### User

```python
class User:
    user_name: str
    full_name: str
    email: str
    # ...other fields and methods
```

### BankAccount

```python
class BankAccount:
    account_name: str
    user_name: str
    account_type: AccountType
    balance: float
    currency: str
    # ...other fields and methods
```

### Transaction

```python
class Transaction:
    transaction_id: str
    source_account_name: str
    destination_account_name: str
    amount: float
    currency: str
    transaction_type: TransactionType
    timestamp: datetime
    # ...other fields and methods
```

### Enums

```python
class AccountType(Enum):
    SAVINGS
    CHECKING
    # ...other types

class TransactionType(Enum):
    DEPOSIT
    WITHDRAWAL
    TRANSFER
    # ...other types
```

---

## Usage

1. Clone the repo.
2. Install dependencies:  
   `pip install -r requirements.txt`
3. Run the app:  
   `python -m bank.app`
4. Use a tool like Postman or `curl` to interact with the API.

---

## Project Structure

```
bank/
  api/        # API endpoints (Flask Blueprints)
  models/     # Data models and enums
  utils/      # Utility functions
  app.py      # Main Flask app
  README.md
```

## Things to Add 
1. Pagination for some endpoints would be really good. We are not adding it currently since the data is not too big
1. Authentication could be very nice but that might be more add more friction than needed
1. Robust validation with Pydantic or Marshmellow would be great but leaving that out too
