from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):

    username: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    password: str = Field(
        ...,
        min_length=4,
        max_length=100
    )


class VehicleCreate(BaseModel):

    license_plate: str = Field(
        ...,
        min_length=2,
        max_length=20
    )

    vehicle_type: str

    @field_validator("license_plate")
    @classmethod
    def validate_license_plate(
        cls,
        value: str
    ) -> str:

        value = value.strip().upper()

        if not value:
            raise ValueError(
                "License plate cannot be empty."
            )

        return value

    @field_validator("vehicle_type")
    @classmethod
    def validate_vehicle_type(
        cls,
        value: str
    ) -> str:

        value = value.strip().upper()

        if value not in {"CAR", "EV"}:
            raise ValueError(
                "Vehicle type must be CAR or EV."
            )

        return value


class ParkingRequest(BaseModel):

    license_plate: str = Field(
        ...,
        min_length=2,
        max_length=20
    )

    @field_validator("license_plate")
    @classmethod
    def validate_license_plate(
        cls,
        value: str
    ) -> str:

        value = value.strip().upper()

        if not value:
            raise ValueError(
                "License plate cannot be empty."
            )

        return value


class CheckoutRequest(BaseModel):

    license_plate: str = Field(
        ...,
        min_length=2,
        max_length=20
    )

    @field_validator("license_plate")
    @classmethod
    def validate_license_plate(
        cls,
        value: str
    ) -> str:

        value = value.strip().upper()

        if not value:
            raise ValueError(
                "License plate cannot be empty."
            )

        return value