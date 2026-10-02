import ctypes
import platform
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

BUILD_DIR = (
    BASE_DIR
    / "cpp-engine"
    / "build"
)


def get_library_path() -> Path:

    system = platform.system()

    if system == "Windows":

        return BUILD_DIR / "parking_engine.dll"

    if system == "Linux":

        return BUILD_DIR / "libparking_engine.so"

    if system == "Darwin":

        return BUILD_DIR / "libparking_engine.dylib"

    raise RuntimeError(
        f"Unsupported operating system: {system}"
    )


class ParkingEngine:

    def __init__(self):

        self.library_path = get_library_path()

        if not self.library_path.exists():

            raise FileNotFoundError(
                "C++ engine library not found: "
                f"{self.library_path}"
            )

        self.library = ctypes.CDLL(
            str(self.library_path)
        )

        self.library.calculateParkingFee.argtypes = [
            ctypes.c_int,
            ctypes.c_double
        ]

        self.library.calculateParkingFee.restype = (
            ctypes.c_double
        )

    def calculate_fee(
        self,
        vehicle_type: str,
        duration_hours: float
    ) -> float:

        vehicle_type = vehicle_type.upper()

        if vehicle_type == "CAR":

            vehicle_type_code = 0

        elif vehicle_type == "EV":

            vehicle_type_code = 1

        else:

            raise ValueError(
                "Vehicle type must be CAR or EV."
            )

        fee = self.library.calculateParkingFee(
            vehicle_type_code,
            duration_hours
        )

        if fee < 0:

            raise ValueError(
                "C++ engine rejected the vehicle type."
            )

        return fee


parking_engine = ParkingEngine()