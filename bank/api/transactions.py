from flask import Blueprint, jsonify, request

from bank.api.data.data import ACCOUNT_NAME_TO_USERNAME, ACCOUNTS, TRANSACTIONS, save_data
from bank.models.enums import TransactionType
from bank.models.transaction import Transaction
from bank.utils.utils import parse_boolean_query_param

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route(
    "/api/v1/accounts/deposit/<string:user_name>/<string:account_name>",
    methods=["POST"],
)
def deposit(user_name: str, account_name: str) -> str:
    """Deposit into a bank account.
    Args:
        user_name (str): The unique username of the user whose account to deposit into.
        account_name (str): The name of the account to deposit into.
    Returns:
        str: A JSON response containing the created transaction's information and the account modified.
    """
    accounts = ACCOUNTS.get(user_name, None)
    if not accounts:
        return jsonify({"error": "Account not found"}), 404

    account_to_update = -1
    for idx, account in enumerate(accounts):
        if account.account_name == account_name:
            account_to_update = idx
            break
    if account_to_update == -1:
        return jsonify({"error": "Account not found"}), 404

    data = request.get_json()
    required_fields = ["amount", "currency", "description"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required transaction fields"}), 400

    try:
        new_transaction = Transaction(
            type=TransactionType.DEPOSIT,
            amount=float(data["amount"]),
            currency=data["currency"],
            destination_account_name=accounts[account_to_update].account_name,
            description=data["description"],
        )
        TRANSACTIONS.append(new_transaction)
        accounts[account_to_update].process_transaction(new_transaction)
        save_data()
        return (
            jsonify(
                {
                    "message": "Transaction created successfully.",
                    "transaction": new_transaction.serialize_dict(),
                    "account": accounts[account_to_update].serialize_dict(),
                }
            ),
            201,
        )
    except KeyError:
        return jsonify({"error": "Invalid transaction_type"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@transactions_bp.route(
    "/api/v1/accounts/withdraw/<string:user_name>/<string:account_name>",
    methods=["POST"],
)
def withdraw(user_name: str, account_name: str) -> str:
    """Withdraw from a bank account.
    Args:
        user_name (str): The unique username of the user whose account to withdraw from.
        account_name (str): The name of the account to withdraw from.
    Returns:
        str: A JSON response containing the created transaction's information and the account modified.
    """
    accounts = ACCOUNTS.get(user_name, None)
    if not accounts:
        return jsonify({"error": "Account not found"}), 404

    account_to_update = -1
    for idx, account in enumerate(accounts):
        if account.account_name == account_name:
            account_to_update = idx
            break
    if account_to_update == -1:
        return jsonify({"error": "Account not found"}), 404

    data = request.get_json()
    required_fields = ["amount", "currency", "description"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required transaction fields"}), 400

    try:
        new_transaction = Transaction(
            type=TransactionType.WITHDRAWAL,
            amount=float(data["amount"]),
            currency=data["currency"],
            source_account_name=accounts[account_to_update].account_name,
            description=data["description"],
        )
        TRANSACTIONS.append(new_transaction)
        accounts[account_to_update].process_transaction(new_transaction)
        save_data()
        return (
            jsonify(
                {
                    "message": "Transaction created successfully.",
                    "transaction": new_transaction.serialize_dict(),
                    "account": accounts[account_to_update].serialize_dict(),
                }
            ),
            201,
        )
    except KeyError:
        return jsonify({"error": "Invalid transaction_type"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@transactions_bp.route("/api/v1/accounts/transfer", methods=["POST"])
def transfer() -> str:
    """Transfer between accounts.
    Returns:
        str: A JSON response containing the created transaction's information and the accounts modified.
    """
    data = request.get_json()
    required_fields = [
        "amount",
        "currency",
        "source_account_name",
        "destination_account_name",
        "description",
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required transaction fields"}), 400

    # Find the source and destination accounts
    source_user_name = ACCOUNT_NAME_TO_USERNAME[data["source_account_name"]]
    destination_user_name = ACCOUNT_NAME_TO_USERNAME[data["destination_account_name"]]

    source_accounts = ACCOUNTS.get(source_user_name, None)
    if not source_accounts:
        return jsonify({"error": "Source account not found"}), 404
    destination_accounts = ACCOUNTS.get(destination_user_name, None)
    if not destination_accounts:
        return jsonify({"error": "Destination account not found"}), 404

    source_account_to_update = -1
    for idx, account in enumerate(source_accounts):
        if account.account_name == data["source_account_name"]:
            source_account_to_update = idx
            break
    if source_account_to_update == -1:
        return jsonify({"error": "Source account not found"}), 404

    destination_account_to_update = -1
    for idx, account in enumerate(destination_accounts):
        if account.account_name == data["destination_account_name"]:
            destination_account_to_update = idx
            break
    if destination_account_to_update == -1:
        return jsonify({"error": "Destination account not found"}), 404

    try:
        out_transaction = Transaction(
            type=TransactionType.TRANSFER_OUT,
            amount=float(data["amount"]),
            currency=data["currency"],
            source_account_name=data["source_account_name"],
            destination_account_name=data["destination_account_name"],
            description=data["description"],
        )
        in_transaction = Transaction(
            type=TransactionType.TRANSFER_IN,
            amount=float(data["amount"]),
            currency=data["currency"],
            source_account_name=data["source_account_name"],
            destination_account_name=data["destination_account_name"],
            description=data["description"],
        )

        TRANSACTIONS.extend([out_transaction, in_transaction])
        source_accounts[source_account_to_update].process_transaction(out_transaction)
        destination_accounts[destination_account_to_update].process_transaction(
            in_transaction
        )
        save_data()
        return (
            jsonify(
                {
                    "message": "Transfer Transactions created successfully.",
                    "transfer out transaction": out_transaction.serialize_dict(),
                    "transfer in transaction": in_transaction.serialize_dict(),
                    "source account": source_accounts[
                        source_account_to_update
                    ].serialize_dict(),
                    "destination account": destination_accounts[
                        destination_account_to_update
                    ].serialize_dict(),
                }
            ),
            201,
        )
    except KeyError:
        return jsonify({"error": "Invalid transaction_type"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@transactions_bp.route(
    "/api/v1/accounts/history/<string:account_name>", methods=["GET"]
)
def get_balance_and_transaction_history(account_name: str) -> str:
    """Get the balance of a bank account.
    Args:
        account_name (str): The name of the account to retrieve the balance for.
    Returns:
        str: A JSON response containing the account's balance.
    """
    user_name = ACCOUNT_NAME_TO_USERNAME.get(account_name, None)
    if not user_name:
        return jsonify({"error": "Account not found"}), 404

    accounts = ACCOUNTS.get(user_name, None)
    if not accounts:
        return jsonify({"error": "Account not found"}), 404

    show_balance = parse_boolean_query_param(request.args.get("balance", "false"))
    show_transactions = parse_boolean_query_param(
        request.args.get("transactions", "false")
    )

    for account in accounts:
        if account.account_name == account_name:
            ret = {
                "account_name": account_name,
                "username": user_name,
            }
            if show_transactions:
                ret["transactions"] = [
                    transaction.serialize_dict()
                    for transaction in account.transaction_history
                ]
            if show_balance:
                ret["balance"] = account.balance

            return (
                jsonify(ret),
                200,
            )

    return jsonify({"error": "Account not found"}), 404


@transactions_bp.route("/api/v1/accounts/history/all_transactions", methods=["GET"])
def get_all_transactions() -> str:
    """Get all transactions.
    Returns:
        str: A JSON response containing all transactions.
    """

    return (
        jsonify(
            {
                "count": len(TRANSACTIONS),
                "transactions": [
                    transaction.serialize_dict() for transaction in TRANSACTIONS
                ],
            }
        ),
        200,
    )
