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

    def __post_init__(self):
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
        ] and (self.source_account_id is None or self.destination_account_id is None):
            raise ValueError(
                "Transfers must have both source and destination account IDs."
            )
        
    def __str__(self):
        return (
            f"Transaction(type={self.type}, amount={self.amount}, "
            f"currency={self.currency}, source_account_id={self.source_account_id}, "
            f"destination_account_id={self.destination_account_id}, "
            f"description={self.description}, transaction_id={self.transaction_id}, "
            f"transaction_timestamp={self.transaction_timestamp}, status={self.status})"
        )

if __name__ == "__main__":
    # Example usage
    print("*** Printing Docstrings ***")
    print(Transaction.__doc__)