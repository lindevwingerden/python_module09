from pydantic import BaseModel, Field, ValidationError, model_validator
from enum import Enum
from datetime import datetime


class Rank(Enum):
    """The possible ranks of a crew member, from lowest to highest."""

    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    """Validated data of an individual crew member.

    Used as a nested model inside SpaceMission: every member in a
    mission's crew list is validated as a CrewMember.
    """

    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = Field(default=True)


class SpaceMission(BaseModel):
    """Validated space mission with a nested list of crew members.

    Field() constraints check each value on its own. The
    safety_requirements() model validator then checks
    rules that depend on the crew as a whole.
    """

    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode='after')
    def safety_requirements(self) -> "SpaceMission":
        """Check the mission safety rules after all fields are validated.

        Runs automatically when a SpaceMission is created. At this
        point every crew member has already been validated as a
        CrewMember, so their fields can be used safely.
        """
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")
        leader = False
        for member in self.crew:
            if member.rank == Rank.COMMANDER or member.rank == Rank.CAPTAIN:
                leader = True
        if not leader:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )
        if self.duration_days > 365:
            experienced = 0
            for member in self.crew:
                if member.years_experience > 4:
                    experienced += 1
            if (experienced / len(self.crew)) < 0.5:
                raise ValueError(
                    "Long missions (> 365 days) need"
                    "50% experienced crew (5+ years)"
                )
        for member in self.crew:
            if not member.is_active:
                raise ValueError("All crew members must be active")
        return self


def print_validation_errors(error: ValidationError) -> None:
    """Print a readable message for every error in a ValidationError.

    Errors raised in safety_requirements() have type "value_error" and
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
    """Demonstrate SpaceMission validation with a valid and invalid case.

    First creates the crew members, then a valid mission whose details
    are printed. Finally tries to create a mission without a Commander
    or Captain and prints the resulting validation error message.
    """
    print("Space Mission Crew Validation")
    print("========================================")
    try:
        sarah = CrewMember(
            member_id="SC12345",
            name="Sarah Connor",
            rank=Rank.COMMANDER,
            age=37,
            specialization="Mission Command",
            years_experience=15
        )
        john = CrewMember(
            member_id="JS23456",
            name="John Smith",
            rank=Rank.LIEUTENANT,
            age=33,
            specialization="Navigation",
            years_experience=7
        )
        alice = CrewMember(
            member_id="AJ34567",
            name="Alice Johnson",
            rank=Rank.OFFICER,
            age=62,
            specialization="Engineering",
            years_experience=38
        )
    except ValidationError as e:
        # Should not happen; shown in case the crew data is wrong
        print("Unexpected validation error:")
        print_validation_errors(e)
        return
    try:
        valid_mission = SpaceMission(
            mission_id="M2024_MARS2",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date=datetime(2027, 2, 14, 4, 0),
            duration_days=900,
            crew=[sarah, john, alice],
            budget_millions=2500.0
        )
        print("Valid mission created:")
        print(f"Mission: {valid_mission.mission_name}")
        print(f"ID: {valid_mission.mission_id}")
        print(f"Destination: {valid_mission.destination}")
        print(f"Duration: {valid_mission.duration_days} days")
        print(f"Budget: ${valid_mission.budget_millions}M")
        print(f"Crew size: {len(valid_mission.crew)}")
        print("Crew members:")
        for member in valid_mission.crew:
            print(f"- {member.name} ({member.rank.value})", end=" ")
            print(f"- {member.specialization}")
    except ValidationError as e:
        # Should not happen; shown in case the valid data is wrong
        print("Unexpected validation error:")
        print_validation_errors(e)
    print("\n========================================")
    # Invalid case: same space mission with only John and Alice
    try:
        invalid_mission = SpaceMission(
            mission_id="M2024_VENUS",
            mission_name="Venus Colony Establishment",
            destination="Venus",
            launch_date=datetime(2029, 2, 14, 4, 0),
            duration_days=900,
            crew=[john, alice],
            budget_millions=2500.0
        )
        print(f"Space mission {invalid_mission.mission_name}", end=" ")
        print("created without commander or captain.")
    except ValidationError as e:
        print("Expected validation error:")
        print_validation_errors(e)


if __name__ == "__main__":
    main()
