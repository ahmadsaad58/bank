from enum import Enum


class AccountType(Enum):
    """Represents the type of bank account.

    - SAVINGS: A standard savings account.
    - CHECKING: A standard checking account.
    - CREDIT: A credit account, which may have a credit limit and interest rates.
    - LOAN: A loan account, which may have a principal amount and interest rates.
    """

    SAVINGS = "SAVINGS"
    CHECKING = "CHECKING"
    CREDIT = "CREDIT"
    LOAN = "LOAN"
    # TODO: Add more acount types


class AccountStatus(Enum):
    """Represents the status of a bank account.

    - ACTIVE: The account is active and can be used for transactions.
    - CLOSED: The account has been closed and cannot be used for transactions.
    - FROZEN: The account is frozen and cannot be used for transactions.
    - PENDING: The account is pending verification or approval.
    """

    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    FROZEN = "FROZEN"
    PENDING = "PENDING"
    # TODO: Add more account statuses


class TransactionType(Enum):
    """Represents the type of financial transaction.

    - DEPOSIT: Money deposited into the account.
    - WITHDRAWAL: Money withdrawn from the account.
    - TRANSFER_IN: Money transferred into the account from another account.
    - TRANSFER_OUT: Money transferred out of the account to another account.
    - FEE: A fee charged to the account.
    - INTEREST: Interest earned or paid on the account.
    """

    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    FEE = "FEE"
    INTEREST = "INTEREST"
    # TODO: Add more transaction types


class TransactionStatus(Enum):
    """Represents the status of a transaction.

    - PENDING: The transaction is pending and has not yet been completed.
    - COMPLETED: The transaction has been completed successfully.
    - FAILED: The transaction has failed and was not completed.
    - REVERSED: The transaction has been reversed.
    - CANCELLED: The transaction has been cancelled.
    """

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"
    CANCELLED = "CANCELLED"
    # TODO: Add more transaction statuses
