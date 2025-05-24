import time
import uuid
from dataclasses import dataclass, field


@dataclass
class ContactInfo:
    """Represents contact details for a user.

    This dataclass encapsulates the user's email and phone number.
    Attributes:
        email (str): The user's email address.
        phone (str | None): The user's phone number. Defaults to None.
    """

    email: str
    phone: str | None = None

    def __str__(self):
        return f"ContactInfo(Email={self.email}, Phone={self.phone})"


@dataclass
class User:
    """Represents a bank customer.

    This dataclass encapsulates the user's personal information and contact details.
    Attributes:
    - username (str): The username of the user.
    - first_name (str): The first name of the user.
    - last_name (str): The last name of the user.
    - contact_info (ContactInfo): The contact information of the user.
    - user_id (str): The unique UUID identifier for the user.
    - created_at (str): The timestamp when the user was created.
    """

    username: str
    first_name: str
    last_name: str
    contact_info: ContactInfo
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    # Based on unix timestamp
    created_at: str = field(default_factory=lambda: time.time())

    def __post_init__(self):
        if not self.username or not self.first_name or not self.last_name:
            raise ValueError("Username, first name, and last name cannot be empty.")
        # TODO: Add more validation

    def __str__(self):
        return (
            f"User(username={self.username}, first_name={self.first_name}, "
            f"last_name={self.last_name}, contact_info={self.contact_info}, "
            f"user_id={self.user_id}, created_at={self.created_at})"
        )


if __name__ == "__main__":
    # Example usage
    print("*** Printing Docstrings ***")
    print(ContactInfo.__doc__)
    print(User.__doc__)

    print("*** Creating ContactInfo Instance ***")
    user_contact = ContactInfo(email="john.doe@example.com", phone="555-123-4567")
    print(f"Created ContactInfo: {user_contact}")
    user_contact = ContactInfo(email="john.doe@example.com")
    print(f"Created ContactInfo: {user_contact}")

    print()
    print("*** Creating User Instance ***")
    user = User(
        username="john.doe",
        first_name="John",
        last_name="Doe",
        contact_info=user_contact,
    )
    print(f"Created User: {user}")
