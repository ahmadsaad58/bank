import time
import uuid
from dataclasses import dataclass, field

from bank.models.enums import TransactionStatus, TransactionType


@dataclass
class Transaction:
    """Represents a single financial transaction.

    This dataclass encapsulates the details of a transaction, including its type,
    amount, currency, source and destination account IDs, description, transaction ID,
    transaction timestamp, and status.
    Attributes:
        type (TransactionType): The type of the transaction (e.g., deposit, withdrawal).
        amount (float): The amount of money involved in the transaction.
        currency (str): The currency of the transaction (e.g., USD, EUR).
        source_account_id (str | None): The UUID of the source account. Defaults to None.
        destination_account_id (str | None): The UUID of the destination account. Defaults to None.
        description (str | None): A description of the transaction. Defaults to None.
        transaction_id (str): A unique identifier for the transaction. Generated automatically.
        transaction_timestamp (str): The timestamp when the transaction occurred. Generated automatically.
        status (TransactionStatus): The status of the transaction. Defaults to PENDING.
    """

    type: TransactionType
    amount: float
    currency: str
    # UUID of the source account
    source_account_id: str | None = None
    # UUID of the destination account
    destination_account_id: str | None = None
    description: str | None = None
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    # Based on unix timestamp
    transaction_timestamp: str = field(default_factory=lambda: time.time())
    # Default status is PENDING
    status: TransactionStatus = TransactionStatus.PENDING

    def __post_init__(self) -> None:
        """Post-initialization checks and setup for the Transaction instance.
        Raises:
            ValueError: If the amount is negative or zero, or if the transaction type requires a source or destination account ID that is not provided.
        """
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive.")
        if (
            self.type in [TransactionType.TRANSFER_OUT, TransactionType.WITHDRAWAL]
            and self.source_account_id is None
        ):
            raise ValueError(f"{self.type.value} must have a source_account_id.")
        if (
            self.type in [TransactionType.TRANSFER_IN, TransactionType.DEPOSIT]
            and self.destination_account_id is None
        ):
            raise ValueError(f"{self.type.value} must have a destination_account_id.")
        if self.type in [
            TransactionType.TRANSFER_IN,
            TransactionType.TRANSFER_OUT,
        ] and (self.source_account_id is None and self.destination_account_id is None):
            raise ValueError(
                "Transfers must have both source and destination account IDs."
            )

    def __str__(self) -> str:
        """Returns a string representation of the Transaction instance."""
        return (
            f"Transaction(type={self.type}, amount={self.amount:.2f}, "
            f"currency={self.currency}, source_account_id={self.source_account_id}, "
            f"destination_account_id={self.destination_account_id}, "
            f"description={self.description}, transaction_id={self.transaction_id}, "
            f"transaction_timestamp={self.transaction_timestamp}, status={self.status})"
        )

    def serialize_dict(self) -> dict:
        """Serializes the Transaction instance to a dictionary.
        Returns:
            dict: A dictionary representation of the Transaction instance.
        """
        return {
            "type": self.type.value,
            "amount": self.amount,
            "currency": self.currency,
            "source_account_id": self.source_account_id,
            "destination_account_id": self.destination_account_id,
            "description": self.description,
            "transaction_id": self.transaction_id,
            "transaction_timestamp": self.transaction_timestamp,
            "status": self.status.value,
        }


if __name__ == "__main__":
    # Example usage
    print("*** Printing Docstrings ***")
    print(Transaction.__doc__)

    from bank.models.user import ContactInfo, User

    # Creating a User
    user = User(
        username="john.doe",
        first_name="John",
        last_name="Doe",
        contact_info=ContactInfo(email="john.doe@example.com", phone="555-123-4567"),
    )

    from bank.models.bank_account import BankAccount
    from bank.models.enums import AccountType

    # Creating a BankAccount
    user_checking = BankAccount(
        account_type=AccountType.CHECKING,
        currency="USD",
        account_owner=user.username,
        initial_deposit=500.00,
    )
    user_savings = BankAccount(
        account_type=AccountType.SAVINGS,
        currency="USD",
        account_owner=user.username,
        initial_deposit=1000.00,
    )

    # Creating a Transaction
    print("*** Creating a Transaction ***")
    deposit_transaction = Transaction(
        type=TransactionType.DEPOSIT,
        amount=200.00,
        currency="USD",
        destination_account_id=user_checking.account_id,
        description="First deposit",
    )
    print(deposit_transaction)

    print()
    print("*** Depositing Money into User Checking Account ***")
    user_checking.process_transaction(deposit_transaction)

    print()
    print("*** Mismatch Currency Transaction ***")
    user_checking.process_transaction(
        Transaction(
            type=TransactionType.DEPOSIT,
            amount=200.00,
            currency="EUR",
            destination_account_id=user_checking.account_id,
            description="Deposit in different currency",
        )
    )

    print()
    print("*** Withdrawing Money from User Checking Account ***")
    user_checking.process_transaction(
        Transaction(
            type=TransactionType.WITHDRAWAL,
            amount=100.00,
            currency="USD",
            source_account_id=user_checking.account_id,
            description="First withdrawal",
        )
    )

    print()
    print(
        "*** Transferring Money from User Checking Account to User Savings Account ***"
    )
    print(
        "*** For every transfer, there should be 2 transactions created, one in and one out ***"
    )
    transfer_out = Transaction(
        type=TransactionType.TRANSFER_OUT,
        amount=100.00,
        currency="USD",
        source_account_id=user_checking.account_id,
        destination_account_id=user_savings.account_id,
        description="Transfer out of checking account",
    )

    transfer_in = Transaction(
        type=TransactionType.TRANSFER_IN,
        amount=100.00,
        currency="USD",
        source_account_id=user_checking.account_id,
        destination_account_id=user_savings.account_id,
        description="Transfer in to savings account",
    )

    user_checking.process_transaction(transfer_out)
    user_savings.process_transaction(transfer_in)

    print()
    print("*** Withdrawing Excess Money from User Checking Account ***")
    user_checking.process_transaction(
        Transaction(
            type=TransactionType.WITHDRAWAL,
            amount=1_000.00,
            currency="USD",
            source_account_id=user_checking.account_id,
            description="Withdrawal exceeding balance",
        )
    )

    print()
    print("*** Printing User Transaction History ***")
    print(user_checking.transaction_history)
    print(user_savings.transaction_history)
