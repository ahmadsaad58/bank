import time
import uuid
from dataclasses import dataclass, field
from typing import List

from bank.models.enums import AccountStatus, AccountType


@dataclass
class BankAccount:
    """Represents a single bank account.

    This dataclass encapsulates the details of a bank account, including its type,
    currency, owners, initial deposit, account ID, account number, balance,
    creation timestamp, and status.
    Attributes:
        account_type (AccountType): The type of the bank account (e.g., savings, checking).
        currency (str): The currency of the account (e.g., USD, EUR).
        owners (List[str]): A list of user IDs who own this account.
        initial_deposit (float): The initial deposit amount. Defaults to 0.0.
        account_id (str): A unique identifier for the account. Generated automatically.
        account_number (str): A unique number for the account. Generated automatically.
        account_name (str): A name for the account, generated from the account type and number.
        balance (float): The current balance of the account. Managed dynamically.
        created_at (str): The timestamp when the account was created. Generated automatically.
        status (AccountStatus): The status of the account. Defaults to ACTIVE.
    """

    account_type: AccountType
    currency: str
    # List of user_ids who own this account
    owners: List[str]
    initial_deposit: float = 0.0
    account_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    account_number: str = field(init=False)
    account_name: str = field(init=False)
    # Balance is not set at initialization, but managed
    balance: float = field(init=False)
    created_at: str = field(default_factory=lambda: time.time())
    # Default status is ACTIVE
    status: AccountStatus = AccountStatus.ACTIVE

    def __post_init__(self):
        if not self.owners:
            raise ValueError("An account must have at least one owner.")
        if self.initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative.")

        self.account_number = self.account_id[:5]
        self.account_name = f"{self.account_type.value.lower()}_{self.account_number}"
        self.balance = self.initial_deposit

    def deposit(self, amount: float):
        """Simulates a deposit into the account.
        Args:
            amount (float): The amount to deposit.
        Raises:
            ValueError: If the deposit amount is not positive.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount

    def withdraw(self, amount: float) -> bool:
        """Simulates a withdrawal from the account.
        Args:
            amount (float): The amount to withdraw.
        Returns:
            bool: True if the withdrawal was successful, False if insufficient funds.
        Raises:
            ValueError: If the withdrawal amount is not positive.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.balance < amount:
            # Insufficient funds
            return False
        self.balance -= amount
        return True
    
    def __str__(self):
        return (
            f"BankAccount(account_type={self.account_type}, currency={self.currency}, "
            f"owners={self.owners}, initial_deposit={self.initial_deposit:.2f}, "
            f"account_id={self.account_id}, account_number={self.account_number}, "
            f"account_name={self.account_name}, balance={self.balance:.2f}, "
            f"created_at={self.created_at}, status={self.status})"
        )

if __name__ == "__main__":
    # Example usage
    print("*** Printing Docstrings ***")
    print(BankAccount.__doc__)

    from bank.models.user import User, ContactInfo
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
            owners=[user.user_id],
            initial_deposit=500.00
        )
    print(f"Created Checking Account: {user_checking}")

    print()
    user_savings = BankAccount(
            account_type=AccountType.SAVINGS,
            currency="USD",
            owners=[user.user_id],
            initial_deposit=1000.00
        )
    print(f"Created Savings Account: {user_savings}")
