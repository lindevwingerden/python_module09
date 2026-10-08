from pydantic import BaseModel, Field, ValidationError, model_validator
from enum import Enum
from datetime import datetime


class ContactType(Enum):
    """Ways in which alien contact can take place.

    Pydantic converts a matching string (e.g. "radio") into the
    corresponding member; any other value raises a ValidationError.
    """

    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    """Validated report of an alien contact.

    Field() constraints check each value on its own. The
    check_rules() model validator then checks business rules that
    depend on combinations of fields.
    """

    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: str | None = Field(default=None, max_length=500)
    is_verified: bool = Field(default=False)

    @model_validator(mode='after')
    def check_rules(self) -> "AlienContact":
        """Check the business rules after all fields are validated.

        Runs automatically when an AlienContact is created. Raising a
        ValueError makes Pydantic wrap it in a ValidationError. The
        returned instance is the object the caller receives.
        """
        if not self.contact_id.startswith("AC"):
            raise ValueError(
                "Contact ID must start with 'AC' (Alien Contact)"
            )
        if self.contact_type == ContactType.PHYSICAL and not self.is_verified:
            raise ValueError(
                "Physical contact reports must be verified"
            )
        if (
            self.contact_type == ContactType.TELEPATHIC
            and self.witness_count < 3
        ):
            raise ValueError(
                "Telepathic contact requires at least 3 witnesses"
            )
        if self.signal_strength > 7.0 and self.message_received is None:
            raise ValueError(
                "Strong signals (> 7.0) should include received messages"
            )
        return self


def print_validation_errors(error: ValidationError) -> None:
    """Print a readable message for every error in a ValidationError.

    Errors raised in check_rules() have type "value_error" and
    keep the original exception in ctx. Printing that avoids the
    "Value error, " prefix that err["msg"] adds. Other errors
    (e.g. Field constraints) have no "error" key, so use msg.
    """
    for err in error.errors():
        if err["type"] == "value_error":
            print(err["ctx"]["error"])
        else:
            print(err["msg"])


def main() -> None:
    """Demonstrate AlienContact validation with a valid and invalid case.

    First creates a valid contact report and prints its details, then
    tries to create a report that breaks a business rule and prints
    the resulting validation error message.
    """
    print("Alien Contact Log Validation")
    print("========================================")
    try:
        valid_contact = AlienContact(
            contact_id="AC_2024_001",
            timestamp=datetime(2024, 2, 14, 3, 4),
            location="Area 51, Nevada",
            contact_type=ContactType.RADIO,
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=5,
            message_received="Greetings from Zeta Reticuli"
        )
        print("Valid contact report:")
        print(f"ID: {valid_contact.contact_id}")
        # .value gives "radio" instead of "ContactType.RADIO"
        print(f"Type: {valid_contact.contact_type.value}")
        print(f"Location: {valid_contact.location}")
        print(f"Signal: {valid_contact.signal_strength}/10")
        print(f"Duration: {valid_contact.duration_minutes} minutes")
        print(f"Witnesses: {valid_contact.witness_count}")
        print(f"Message: '{valid_contact.message_received}'")
    except ValidationError as e:
        # Should not happen; shown in case the valid data is wrong
        print("Unexpected validation error:")
        print_validation_errors(e)
    print("\n========================================")
    # Invalid case: telepathic contact with less than 3 witnesses
    try:
        invalid_contact = AlienContact(
            contact_id="AC_2024_001",
            timestamp=datetime(2024, 2, 14, 3, 4),
            location="Area 51, Nevada",
            contact_type=ContactType.TELEPATHIC,
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=2,
            message_received="Greetings from Zeta Reticuli"
        )
        print("Contact report:")
        print(f"Type: {invalid_contact.contact_type.value}")
        print(f"Witnesses: {invalid_contact.witness_count}")
    except ValidationError as e:
        print("Expected validation error:")
        print_validation_errors(e)


if __name__ == "__main__":
    main()
