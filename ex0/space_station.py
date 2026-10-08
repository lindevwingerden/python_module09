from pydantic import BaseModel, Field, ValidationError
from datetime import datetime


class SpaceStation(BaseModel):
    """Validated data model for a space station's vital statistics.

    Each field uses Field() constraints, so Pydantic automatically
    checks the values when an instance is created. If any value
    falls outside its constraints, a ValidationError is raised.
    """

    station_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=1, max_length=50)
    # ge = greater than or equal, le = less than or equal
    crew_size: int = Field(ge=1, le=20)
    power_level: float = Field(ge=0.0, le=100.0)
    oxygen_level: float = Field(ge=0.0, le=100.0)
    # Pydantic can also convert e.g. an ISO string into a datetime
    last_maintenance: datetime
    # Fields with a default value are not required when creating a station
    is_operational: bool = Field(default=True)
    notes: str | None = Field(default=None, max_length=200)


def main() -> None:
    """Demonstrate SpaceStation validation with a valid and invalid case.

    First creates a station with valid data and prints its details,
    then tries to create a station that breaks a constraint and
    prints the resulting validation error message.
    """
    print("Space Station Data Validation")
    print("========================================")
    try:
        valid_station = SpaceStation(
            station_id="ISS001",
            name="International Space Station",
            crew_size=6,
            power_level=85.5,
            oxygen_level=92.3,
            last_maintenance=datetime(2026, 10, 8, 15, 15)
        )
        print("Valid station created:")
        print(f"ID: {valid_station.station_id}")
        print(f"Name: {valid_station.name}")
        print(f"Crew: {valid_station.crew_size} people")
        print(f"Power: {valid_station.power_level}%")
        print(f"Oxygen: {valid_station.oxygen_level}%")
        print("Status: ", end="")
        if valid_station.is_operational:
            print("Operational")
        else:
            print("Non-operational")
    except ValidationError as e:
        # Should not happen; shown in case the valid data is wrong
        print("Unexpected validation error:")
        for err in e.errors():
            print(err["msg"])
    print("\n========================================")
    # Invalid case: crew_size=26 is deliberately above the maximum of 20
    try:
        invalid_station = SpaceStation(
            station_id="ISS002",
            name="International Space Station",
            crew_size=26,
            power_level=85.5,
            oxygen_level=92.3,
            last_maintenance=datetime(2026, 10, 8, 15, 15)
        )
        print("Space station with crew of", end=" ")
        print(f"{invalid_station.crew_size} people created.")
    except ValidationError as e:
        print("Expected validation error:")
        for err in e.errors():
            print(err["msg"])


if __name__ == "__main__":
    main()
