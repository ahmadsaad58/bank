from collections import defaultdict
from typing import Dict, List

from flask import Blueprint, Flask, jsonify

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

utilities_bp = Blueprint("utilities", __name__)


@utilities_bp.route("/api/v1/check_cache", methods=["GET"])
def check_account_name_to_username_cache() -> str:
    """Check the account name to username cache.
    Returns:
        str: A JSON response containing the account name to username mapping.
    """
    return jsonify(ACCOUNT_NAME_TO_USERNAME), 200
