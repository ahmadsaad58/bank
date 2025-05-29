import time
import uuid
from dataclasses import dataclass, field
from typing import List, Tuple

from bank.models.enums import (AccountStatus, AccountType, TransactionStatus,
                               TransactionType)
from bank.models.transaction import Transaction

BLOCKED_ACCOUNT_STATUSES = [
    AccountStatus.FROZEN,
    AccountStatus.CLOSED,
]


@dataclass
class BankAccount:
    """Represents a single bank account.

    This dataclass encapsulates the details of a bank account, including its type,
    currency, owners, initial deposit, account ID, account number, balance,
    creation timestamp, and status.
    Attributes:
        account_type (AccountType): The type of the bank account (e.g., savings, checking).
        currency (str): The currency of the account (e.g., USD, EUR).
        account_owner (str): The owner of the account. This should be a username.
        initial_deposit (float): The initial deposit amount. Defaults to 0.0.
        account_id (str): A unique identifier for the account. Generated automatically.
        account_name (str): A name for the account, generated from the account type and number.
        balance (float): The current balance of the account. Managed dynamically.
        transaction_history (List[Transaction]): A list of transactions associated with the account.
        created_at (str): The timestamp when the account was created. Generated automatically.
        status (AccountStatus): The status of the account. Defaults to ACTIVE.
    """

    account_type: AccountType
    currency: str
    account_owner: str
    initial_deposit: float = 0.0
    # TODO: can add something for joint owners of an account
    account_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    account_name: str = field(init=False)
    # Balance is not set at initialization, but managed

    transaction_history: List[Transaction] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: time.time())
    # Default status is ACTIVE
    status: AccountStatus = AccountStatus.ACTIVE

    def __post_init__(self) -> None:
        """Post-initialization checks and setup for the BankAccount instance.
        Raises:
            ValueError: If the initial deposit is negative or if there are no owners.
        """
        self.balance: float = 0.0
        if not self.account_owner:
            raise ValueError("An account must have at an owner.")
        # Can have 0 balance at the start, but not negative
        if self.initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative.")

        self.account_name = f"{self.account_type.value.lower()}_{self.account_id[:5]}"
        # If there is an inital deposit, process it as a deposit transaction
        if self.initial_deposit > 0:
            initial_deposit_txn = Transaction(
                type=TransactionType.DEPOSIT,
                amount=self.initial_deposit,
                currency=self.currency,
                destination_account_name=self.account_name,
                description="Initial deposit",
            )
            self.process_transaction(initial_deposit_txn)

    def _process_blocked_account_transaction(
        self, transaction: Transaction
    ) -> Tuple[bool, str, TransactionStatus]:
        """Internal method to processes a transaction for a blocked account.
        Args:
            transaction (Transaction): The transaction to process.
        Returns:
            Tuple[bool, str, TransactionStatus]: A tuple containing a boolean indicating success,
            a message, and the transaction status.
        """
        if self.status == AccountStatus.FROZEN:
            print(f"Error: Account {self.account_name} is frozen.")
            transaction.status = TransactionStatus.FAILED
            return False, "Account is frozen", transaction.status
        if self.status == AccountStatus.CLOSED:
            print(f"Error: Account {self.account_name} is closed.")
            transaction.status = TransactionStatus.FAILED
            return False, "Account is closed", transaction.status

    def _process_currency(
        self, transaction: Transaction
    ) -> Tuple[bool, str, TransactionStatus]:
        """Internal method to processes currencies in a transaction. Currently, this method returns a false if there are mismatching currencies.
        Args:
            transaction (Transaction): The transaction to process.
        Returns:
            Tuple[bool, str, TransactionStatus]: A tuple containing a boolean indicating success,
            a message, and the transaction status.
        """
        if self.status in BLOCKED_ACCOUNT_STATUSES:
            return self._process_blocked_account_transaction(transaction)

        if transaction.currency != self.currency:
            print(
                f"Error: Transaction currency ({transaction.currency}) does not match account currency ({self.currency})."
            )
            transaction.status = TransactionStatus.FAILED
            return False, "Currency mismatch", transaction.status

        # TODO: Add currency conversion logic

    def _process_deposit(
        self, transaction: Transaction
    ) -> Tuple[bool, str, TransactionStatus]:
        """Internal method to processes a deposit transaction.
        Args:
            transaction (Transaction): The transaction to process.
        Returns:
            Tuple[bool, str, TransactionStatus]: A tuple containing a boolean indicating success,
            a message, and the transaction status.
        """
        if self.status in BLOCKED_ACCOUNT_STATUSES:
            return self._process_blocked_account_transaction(transaction)

        if transaction.destination_account_name != self.account_name:
            print(f"Error: Deposit transaction destination account name mismatch.")
            transaction.status = TransactionStatus.FAILED
            return False, "Destination account ID mismatch", transaction.status
        if transaction.amount <= 0:
            print(f"Error: Deposit amount must be positive and greater than 0.")
            transaction.status = TransactionStatus.FAILED
            return (
                False,
                "Deposit amount must be positive and greater than 0",
                transaction.status,
            )
        self.balance += transaction.amount
        if self.balance < 0 and self.status == AccountStatus.FROZEN:
            self.status = AccountStatus.ACTIVE
        transaction.status = TransactionStatus.COMPLETED
        print(
            f"Processed DEPOSIT: Account {self.account_name} new balance: {self.balance:.2f}"
        )
        return True, "Deposit successful", transaction.status

    def _process_withdrawl(
        self, transaction: Transaction
    ) -> Tuple[bool, str, TransactionStatus]:
        """Internal method to processes a withdrawl transaction.
        Args:
            transaction (Transaction): The transaction to process.
        Returns:
            Tuple[bool, str, TransactionStatus]: A tuple containing a boolean indicating success,
            a message, and the transaction status.
        """
        if self.status in BLOCKED_ACCOUNT_STATUSES:
            return self._process_blocked_account_transaction(transaction)

        if transaction.source_account_name != self.account_name:
            print(f"Error: Withdrawal transaction source account name mismatch.")
            transaction.status = TransactionStatus.FAILED
            return False, "Source account ID mismatch", transaction.status
        if transaction.amount <= 0:
            print(f"Error: Withdrawal amount must be positive and greater than 0.")
            transaction.status = TransactionStatus.FAILED
            return (
                False,
                "Withdrawal amount must be positive and greater than 0",
                transaction.status,
            )
        if self.balance >= transaction.amount:
            self.balance -= transaction.amount
            transaction.status = TransactionStatus.COMPLETED
            print(
                f"Processed WITHDRAWAL: Account {self.account_name} new balance: {self.balance:.2f}"
            )
            return True, "Withdrawal successful", transaction.status
        else:
            print(
                f"Insufficient funds for withdrawal from account {self.account_name}."
            )
            transaction.status = TransactionStatus.FAILED
            return False, "Insufficient funds", transaction.status

    def _process_transfer_in(
        self, transaction: Transaction
    ) -> Tuple[bool, str, TransactionStatus]:
        """Internal method to processes a transfer in transaction.
        Args:
            transaction (Transaction): The transaction to process.
        Returns:
            Tuple[bool, str, TransactionStatus]: A tuple containing a boolean indicating success,
            a message, and the transaction status.
        """
        if self.status in BLOCKED_ACCOUNT_STATUSES:
            return self._process_blocked_account_transaction(transaction)

        if transaction.destination_account_name != self.account_name:
            print(f"Error: Transfer_IN transaction destination account name mismatch.")
            transaction.status = TransactionStatus.FAILED
            return False, "Destination account ID mismatch", transaction.status
        if transaction.amount <= 0:
            print(f"Error: Transfer_IN amount must be positive and greater than 0.")
            transaction.status = TransactionStatus.FAILED
            return (
                False,
                "Transfer_IN amount must be positive and greater than 0",
                transaction.status,
            )
        self.balance += transaction.amount
        if self.balance < 0 and self.status == AccountStatus.FROZEN:
            self.status = AccountStatus.ACTIVE
        transaction.status = TransactionStatus.COMPLETED
        print(
            f"Processed TRANSFER_IN: Account {self.account_name} new balance: {self.balance:.2f}"
        )
        return True, "Transfer_IN successful", transaction.status

    def _process_transfer_out(
        self, transaction: Transaction
    ) -> Tuple[bool, str, TransactionStatus]:
        """Internal method to processes a transfer out transaction.
        Args:
            transaction (Transaction): The transaction to process.
        Returns:
            Tuple[bool, str, TransactionStatus]: A tuple containing a boolean indicating success,
            a message, and the transaction status.
        """
        if self.status in BLOCKED_ACCOUNT_STATUSES:
            return self._process_blocked_account_transaction(transaction)

        if transaction.source_account_name != self.account_name:
            print(f"Error: Transfer_OUT transaction source account name mismatch.")
            transaction.status = TransactionStatus.FAILED
            return False, "Source account ID mismatch", transaction.status
        if transaction.destination_account_name is None:
            print(f"Error: Transfer_OUT transaction destination account ID is None.")
            transaction.status = TransactionStatus.FAILED
            return False, "Destination account ID is None", transaction.status
        if transaction.amount <= 0:
            print(f"Error: Transfer_OUT amount must be positive and greater than 0.")
            transaction.status = TransactionStatus.FAILED
            return (
                False,
                "Transfer_OUT amount must be positive and greater than 0",
                transaction.status,
            )
        if self.balance >= transaction.amount:
            self.balance -= transaction.amount
            transaction.status = TransactionStatus.COMPLETED
            print(
                f"Processed TRANSFER_OUT: Account {self.account_name} new balance: {self.balance:.2f}"
            )
            return True, "Transfer_OUT successful", transaction.status
        else:
            print(
                f"Insufficient funds for Transfer_OUT from account {self.account_name}."
            )
            transaction.status = TransactionStatus.FAILED
            return False, "Insufficient funds", transaction.status

    def _process_fee(
        self, transaction: Transaction
    ) -> Tuple[bool, str, TransactionStatus]:
        """Internal method to processes a fee transaction.
        Args:
            transaction (Transaction): The transaction to process.
        Returns:
            Tuple[bool, str, TransactionStatus]: A tuple containing a boolean indicating success,
            a message, and the transaction status.
        """
        if self.status in BLOCKED_ACCOUNT_STATUSES:
            return self._process_blocked_account_transaction(transaction)

        if transaction.source_account_name != self.account_name:
            print(f"Error: Fee transaction source account name mismatch.")
            transaction.status = TransactionStatus.FAILED
            return False
        if self.balance >= transaction.amount:
            self.balance -= transaction.amount
            transaction.status = TransactionStatus.COMPLETED
            print(
                f"Processed FEE: Account {self.account_name} new balance: {self.balance:.2f}"
            )
            return True
        else:
            print(f"Insufficient funds to deduct fee from account {self.account_name}.")
            self.status = AccountStatus.FROZEN
            transaction.status = TransactionStatus.FAILED
            return False

    def process_transaction(
        self, transaction: Transaction
    ) -> Tuple[bool, str, TransactionStatus]:
        """
        Processes a given transaction, updating the account balance accordingly.
        Returns True if the transaction was successfully processed, False otherwise.
        Note: For transfers between different accounts, this method would be called
              on both the source and destination accounts.
        """
        # All transactions will go in history even the failed ones
        self.transaction_history.append(transaction)

        if transaction.currency != self.currency:
            return self._process_currency(transaction)
        if transaction.type == TransactionType.DEPOSIT:
            return self._process_deposit(transaction)
        elif transaction.type == TransactionType.WITHDRAWAL:
            return self._process_withdrawl(transaction)
        elif transaction.type == TransactionType.TRANSFER_IN:
            return self._process_transfer_in(transaction)
        elif transaction.type == TransactionType.TRANSFER_OUT:
            return self._process_transfer_out(transaction)
        elif transaction.type == TransactionType.FEE:
            return self._process_fee(transaction)
        elif transaction.type == TransactionType.INTEREST:
            return self._process_deposit(transaction)
        else:
            print(f"Warning: Unhandled transaction type: {transaction.type}")
            transaction.status = TransactionStatus.FAILED
            return False, "Unhandled transaction type", transaction.status

    def __str__(self) -> str:
        """Returns a string representation of the BankAccount instance.
        Returns:
            str: A string representation of the BankAccount instance.
        """
        return (
            f"BankAccount(account_type={self.account_type}, currency={self.currency}, "
            f"account_owner={self.account_owner}, initial_deposit={self.initial_deposit:.2f}, "
            f"account_id={self.account_id}, account_name={self.account_name}, "
            f"balance={self.balance:.2f}, "
            f"created_at={self.created_at}, status={self.status}, "
            f"transaction_history={self.transaction_history})"
        )

    def serialize_dict(self) -> dict:
        """Serializes the BankAccount instance to a dictionary.
        Returns:
            dict: A dictionary representation of the BankAccount instance.
        """
        return {
            "account_type": self.account_type.value,
            "currency": self.currency,
            "account_owner": self.account_owner,
            "account_id": self.account_id,
            "account_name": self.account_name,
            "balance": self.balance,
            "created_at": self.created_at,
            "status": self.status.value,
            "transaction_history": [
                txn.serialize_dict() for txn in self.transaction_history
            ],
        }


if __name__ == "__main__":
    # Example usage
    print("*** Printing Docstrings ***")
    print(BankAccount.__doc__)

    from bank.models.user import ContactInfo, User

    # Creating a User
    user = User(
        username="john.doe",
        first_name="John",
        last_name="Doe",
        contact_info=ContactInfo(email="john.doe@example.com", phone="555-123-4567"),
    )

    # Creating a BankAccount
    print("*** Creating Bank Account Instance ***")
    user_checking = BankAccount(
        account_type=AccountType.CHECKING,
        currency="USD",
        account_owner=user.username,
        initial_deposit=500.00,
    )
    print(f"Created Checking Account: {user_checking}")

    print()
    user_savings = BankAccount(
        account_type=AccountType.SAVINGS,
        currency="USD",
        account_owner=user.username,
        initial_deposit=1000.00,
    )
    print(f"Created Savings Account: {user_savings}")
