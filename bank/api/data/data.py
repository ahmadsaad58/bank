from collections import defaultdict
from typing import Dict, List
import pickle
import os


from bank.models.bank_account import BankAccount
from bank.models.transaction import Transaction
from bank.models.user import User

# Store Users: username -> User
USERS: Dict[str, User] = {}
# Store Users: account_name -> username
ACCOUNT_NAME_TO_USERNAME: Dict[str, str] = {}
# Store BankAccounts: username -> List[BankAccount]
ACCOUNTS: Dict[str, List[BankAccount]] = defaultdict(list)
# Store all Transactions, typically linked to accounts for history retrieval
TRANSACTIONS: List[Transaction] = []

DATA_PATH = "bank_data.pkl"

def save_data():
    with open(DATA_PATH, "wb") as f:
        pickle.dump({
            "USERS": USERS,
            "ACCOUNT_NAME_TO_USERNAME": ACCOUNT_NAME_TO_USERNAME,
            "ACCOUNTS": ACCOUNTS,
            "TRANSACTIONS": TRANSACTIONS,
        }, f)

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "rb") as f:
            data = pickle.load(f)
            USERS.update(data.get("USERS", {}))
            ACCOUNT_NAME_TO_USERNAME.update(data.get("ACCOUNT_NAME_TO_USERNAME", {}))
            ACCOUNTS.update(data.get("ACCOUNTS", {}))
            TRANSACTIONS.extend(data.get("TRANSACTIONS", []))

