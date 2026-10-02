import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./index.css";

const API_BASE_URL = "http://localhost:8000";
const TOKEN_KEY = "parking_access_token";
const USER_KEY = "parking_user";

function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getAuthHeaders() {
  const token = getStoredToken();

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    Boolean(getStoredToken())
  );

  const [currentUser, setCurrentUser] = useState(() => {
    const storedUser = localStorage.getItem(USER_KEY);

    if (!storedUser) {
      return null;
    }

    try {
      return JSON.parse(storedUser);
    } catch {
      return null;
    }
  });

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState("");

  const [slots, setSlots] = useState([]);
  const [activeParking, setActiveParking] = useState([]);
  const [parkingHistory, setParkingHistory] = useState([]);

  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [licensePlate, setLicensePlate] = useState("");
  const [vehicleType, setVehicleType] = useState("CAR");
  const [entryLoading, setEntryLoading] = useState(false);

  const [checkoutPlate, setCheckoutPlate] = useState("");
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  const [receipt, setReceipt] = useState(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [vehicleFilter, setVehicleFilter] = useState("ALL");

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);

    setIsAuthenticated(false);
    setCurrentUser(null);

    setSlots([]);
    setActiveParking([]);
    setParkingHistory([]);

    setUsername("");
    setPassword("");

    setError("");
    setSuccess("");
    setReceipt(null);
  };

  const handleUnauthorized = () => {
    logout();
    setError("Your session has expired. Please login again.");
  };

  const authenticatedRequest = async (request) => {
    try {
      return await request(getAuthHeaders());
    } catch (requestError) {
      if (requestError.response?.status === 401) {
        handleUnauthorized();
      }

      throw requestError;
    }
  };

  const handleLogin = async (event) => {
    event.preventDefault();

    setLoginError("");

    if (!username.trim() || !password.trim()) {
      setLoginError("Please enter username and password.");
      return;
    }

    setLoginLoading(true);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/auth/login`,
        {
          username: username.trim(),
          password,
        }
      );

      const token = response.data.access_token;
      const user = response.data.user;

      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));

      setCurrentUser(user);
      setIsAuthenticated(true);

      setPassword("");
      setLoginError("");
    } catch (requestError) {
      if (requestError.response?.data?.detail) {
        setLoginError(requestError.response.data.detail);
      } else {
        setLoginError(
          "Unable to connect to the authentication server."
        );
      }
    } finally {
      setLoginLoading(false);
    }
  };

  const fetchDashboardData = async () => {
    setLoading(true);
    setError("");

    try {
      const headers = getAuthHeaders();

      const [
        healthResponse,
        slotsResponse,
        activeResponse,
        historyResponse,
      ] = await Promise.all([
        axios.get(`${API_BASE_URL}/health`),

        axios.get(`${API_BASE_URL}/parking-slots`, {
          headers,
        }),

        axios.get(`${API_BASE_URL}/active-parking`, {
          headers,
        }),

        axios.get(`${API_BASE_URL}/parking-history`, {
          headers,
        }),
      ]);

      if (healthResponse.data.status === "healthy") {
        setBackendStatus("Online");
      } else {
        setBackendStatus("Unavailable");
      }

      setSlots(slotsResponse.data.slots || []);
      setActiveParking(activeResponse.data.vehicles || []);
      setParkingHistory(historyResponse.data.history || []);
    } catch (requestError) {
      if (requestError.response?.status === 401) {
        handleUnauthorized();
        return;
      }

      setBackendStatus("Offline");

      setError(
        "Unable to load parking data from the backend."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    const verifySession = async () => {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/auth/me`,
          {
            headers: getAuthHeaders(),
          }
        );

        const user = response.data.user;

        setCurrentUser(user);

        localStorage.setItem(
          USER_KEY,
          JSON.stringify(user)
        );

        await fetchDashboardData();
      } catch (requestError) {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);

        setIsAuthenticated(false);
        setCurrentUser(null);
        setLoading(false);
      }
    };

    verifySession();
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    const interval = setInterval(() => {
      fetchDashboardData();
    }, 5000);

    return () => {
      clearInterval(interval);
    };
  }, [isAuthenticated]);

  const handleVehicleEntry = async (event) => {
    event.preventDefault();

    setEntryLoading(true);
    setError("");
    setSuccess("");

    const normalizedPlate = licensePlate
      .trim()
      .toUpperCase();

    if (!normalizedPlate) {
      setError("Please enter a license plate.");
      setEntryLoading(false);
      return;
    }

    try {
      let vehicleAlreadyExists = false;

      try {
        await authenticatedRequest((headers) =>
          axios.post(
            `${API_BASE_URL}/vehicles`,
            {
              license_plate: normalizedPlate,
              vehicle_type: vehicleType,
            },
            {
              headers,
            }
          )
        );
      } catch (requestError) {
        if (requestError.response?.status === 409) {
          vehicleAlreadyExists = true;
        } else {
          throw requestError;
        }
      }

      await authenticatedRequest((headers) =>
        axios.post(
          `${API_BASE_URL}/parking`,
          {
            license_plate: normalizedPlate,
          },
          {
            headers,
          }
        )
      );

      setSuccess(
        vehicleAlreadyExists
          ? "Vehicle parked successfully."
          : "Vehicle registered and parked successfully."
      );

      setLicensePlate("");
      setVehicleType("CAR");

      await fetchDashboardData();
    } catch (requestError) {
      if (requestError.response?.status === 409) {
        setError(
          requestError.response.data.detail ||
            "Vehicle cannot be parked."
        );
      } else if (requestError.response?.data?.detail) {
        setError(requestError.response.data.detail);
      } else {
        setError(
          "Unable to park the vehicle."
        );
      }
    } finally {
      setEntryLoading(false);
    }
  };

  const handleCheckout = async (event) => {
    event.preventDefault();

    setCheckoutLoading(true);
    setError("");
    setSuccess("");
    setReceipt(null);

    const normalizedPlate = checkoutPlate
      .trim()
      .toUpperCase();

    if (!normalizedPlate) {
      setError("Please enter a license plate.");
      setCheckoutLoading(false);
      return;
    }

    try {
      const response = await authenticatedRequest(
        (headers) =>
          axios.post(
            `${API_BASE_URL}/checkout`,
            {
              license_plate: normalizedPlate,
            },
            {
              headers,
            }
          )
      );

      setReceipt(response.data.receipt);

      setSuccess(
        "Vehicle checked out successfully."
      );

      setCheckoutPlate("");

      await fetchDashboardData();
    } catch (requestError) {
      if (requestError.response?.data?.detail) {
        setError(requestError.response.data.detail);
      } else {
        setError(
          "Unable to complete vehicle checkout."
        );
      }
    } finally {
      setCheckoutLoading(false);
    }
  };

  const totalSlots = slots.length;

  const occupiedSlots = slots.filter(
    (slot) => slot.status === "OCCUPIED"
  ).length;

  const availableSlots =
    totalSlots - occupiedSlots;

  const occupancyPercentage =
    totalSlots > 0
      ? ((occupiedSlots / totalSlots) * 100).toFixed(1)
      : "0.0";

  const totalRevenue = parkingHistory.reduce(
    (total, record) =>
      total + Number(record.amount || 0),
    0
  );

  const averageRevenue =
    parkingHistory.length > 0
      ? totalRevenue / parkingHistory.length
      : 0;

  const activeCars = activeParking.filter(
    (vehicle) => vehicle.vehicle_type === "CAR"
  ).length;

  const activeEVs = activeParking.filter(
    (vehicle) => vehicle.vehicle_type === "EV"
  ).length;

  const filteredActiveParking = useMemo(() => {
    const search = searchTerm
      .trim()
      .toUpperCase();

    return activeParking.filter((vehicle) => {
      const matchesSearch =
        !search ||
        vehicle.license_plate
          .toUpperCase()
          .includes(search);

      const matchesType =
        vehicleFilter === "ALL" ||
        vehicle.vehicle_type === vehicleFilter;

      return matchesSearch && matchesType;
    });
  }, [
    activeParking,
    searchTerm,
    vehicleFilter,
  ]);

  const slotsByFloor = {};

  slots.forEach((slot) => {
    if (!slotsByFloor[slot.floor_id]) {
      slotsByFloor[slot.floor_id] = [];
    }

    slotsByFloor[slot.floor_id].push(slot);
  });

  const formatDateTime = (value) => {
    if (!value) {
      return "-";
    }

    const normalized = value.includes("T")
      ? value
      : value.replace(" ", "T");

    const date = new Date(
      `${normalized}Z`
    );

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleString();
  };

  if (!isAuthenticated) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="login-brand">
            <div className="login-icon">
              🅿️
            </div>

            <h1>Smart Parking</h1>

            <p>
              Parking Management System
            </p>
          </div>

          <form
            className="login-form"
            onSubmit={handleLogin}
          >
            <div className="form-group">
              <label htmlFor="username">
                Username
              </label>

              <input
                id="username"
                type="text"
                placeholder="Enter username"
                value={username}
                onChange={(event) =>
                  setUsername(event.target.value)
                }
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">
                Password
              </label>

              <input
                id="password"
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                autoComplete="current-password"
              />
            </div>

            {loginError && (
              <div className="alert error">
                {loginError}
              </div>
            )}

            <button
              type="submit"
              className="primary-button login-button"
              disabled={loginLoading}
            >
              {loginLoading
                ? "Signing in..."
                : "Sign In"}
            </button>
          </form>

          <div className="login-footer">
            <span>Smart Parking System</span>
            <span>Admin Portal</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>
            Smart Parking System
          </h1>

          <p>
            Real-time parking management dashboard
          </p>
        </div>

        <div className="topbar-right">
          <div className="user-info">
            <span className="user-avatar">
              {currentUser?.username
                ?.charAt(0)
                .toUpperCase()}
            </span>

            <div>
              <strong>
                {currentUser?.username}
              </strong>

              <small>
                {currentUser?.role}
              </small>
            </div>
          </div>

          <div className="backend-status">
            <span
              className={
                backendStatus === "Online"
                  ? "status-dot online"
                  : "status-dot offline"
              }
            />

            {backendStatus}
          </div>

          <button
            className="logout-button"
            onClick={logout}
          >
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard">
        {error && (
          <div className="alert error">
            {error}
          </div>
        )}

        {success && (
          <div className="alert success">
            {success}
          </div>
        )}

        <section className="analytics-grid">
          <div className="analytics-card">
            <span className="analytics-label">
              Overall Occupancy
            </span>

            <strong>
              {occupancyPercentage}%
            </strong>

            <small>
              {occupiedSlots} of {totalSlots} slots
            </small>
          </div>

          <div className="analytics-card">
            <span className="analytics-label">
              Available Capacity
            </span>

            <strong>
              {availableSlots}
            </strong>

            <small>
              parking slots available
            </small>
          </div>

          <div className="analytics-card">
            <span className="analytics-label">
              Active Vehicles
            </span>

            <strong>
              {activeParking.length}
            </strong>

            <small>
              {activeCars} cars · {activeEVs} EVs
            </small>
          </div>

          <div className="analytics-card">
            <span className="analytics-label">
              Total Revenue
            </span>

            <strong>
              ₹{totalRevenue.toFixed(2)}
            </strong>

            <small>
              {parkingHistory.length} completed sessions
            </small>
          </div>

          <div className="analytics-card">
            <span className="analytics-label">
              Average Revenue
            </span>

            <strong>
              ₹{averageRevenue.toFixed(2)}
            </strong>

            <small>
              per completed session
            </small>
          </div>
        </section>

        <section className="action-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h2>Vehicle Entry</h2>

                <p>
                  Register and park a vehicle
                </p>
              </div>

              <span className="panel-icon">
                🚗
              </span>
            </div>

            <form
              className="parking-form"
              onSubmit={handleVehicleEntry}
            >
              <div className="form-group">
                <label>
                  License Plate
                </label>

                <input
                  type="text"
                  placeholder="TN01AB1234"
                  value={licensePlate}
                  onChange={(event) =>
                    setLicensePlate(
                      event.target.value.toUpperCase()
                    )
                  }
                />
              </div>

              <div className="form-group">
                <label>
                  Vehicle Type
                </label>

                <select
                  value={vehicleType}
                  onChange={(event) =>
                    setVehicleType(
                      event.target.value
                    )
                  }
                >
                  <option value="CAR">
                    Regular Car
                  </option>

                  <option value="EV">
                    Electric Vehicle
                  </option>
                </select>
              </div>

              <button
                type="submit"
                className="primary-button"
                disabled={entryLoading}
              >
                {entryLoading
                  ? "Parking..."
                  : "Park Vehicle"}
              </button>
            </form>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h2>Vehicle Checkout</h2>

                <p>
                  Complete parking and generate bill
                </p>
              </div>

              <span className="panel-icon">
                💳
              </span>
            </div>

            <form
              className="parking-form"
              onSubmit={handleCheckout}
            >
              <div className="form-group">
                <label>
                  License Plate
                </label>

                <input
                  type="text"
                  placeholder="TN01AB1234"
                  value={checkoutPlate}
                  onChange={(event) =>
                    setCheckoutPlate(
                      event.target.value.toUpperCase()
                    )
                  }
                />
              </div>

              <button
                type="submit"
                className="primary-button checkout-button"
                disabled={checkoutLoading}
              >
                {checkoutLoading
                  ? "Processing..."
                  : "Checkout Vehicle"}
              </button>
            </form>
          </div>
        </section>

        {receipt && (
          <section className="receipt-card">
            <div className="receipt-header">
              <div>
                <h2>
                  Parking Receipt
                </h2>

                <p>
                  Payment completed
                </p>
              </div>

              <span className="paid-badge">
                PAID
              </span>
            </div>

            <div className="receipt-grid">
              <div>
                <span>License Plate</span>
                <strong>
                  {receipt.license_plate}
                </strong>
              </div>

              <div>
                <span>Vehicle Type</span>
                <strong>
                  {receipt.vehicle_type}
                </strong>
              </div>

              <div>
                <span>Floor</span>
                <strong>
                  {receipt.floor_id}
                </strong>
              </div>

              <div>
                <span>Slot</span>
                <strong>
                  {receipt.slot_number}
                </strong>
              </div>

              <div>
                <span>Duration</span>
                <strong>
                  {receipt.duration_hours} hours
                </strong>
              </div>

              <div>
                <span>Billable Hours</span>
                <strong>
                  {receipt.billable_hours}
                </strong>
              </div>

              <div>
                <span>Hourly Rate</span>
                <strong>
                  ₹{Number(
                    receipt.hourly_rate
                  ).toFixed(2)}
                </strong>
              </div>

              <div className="receipt-total">
                <span>Total Amount</span>
                <strong>
                  ₹{Number(
                    receipt.amount
                  ).toFixed(2)}
                </strong>
              </div>
            </div>
          </section>
        )}

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>
                Active Parking
              </h2>

              <p>
                Vehicles currently inside the parking facility
              </p>
            </div>

            <div className="search-controls">
              <input
                type="text"
                placeholder="Search plate..."
                value={searchTerm}
                onChange={(event) =>
                  setSearchTerm(event.target.value)
                }
              />

              <select
                value={vehicleFilter}
                onChange={(event) =>
                  setVehicleFilter(event.target.value)
                }
              >
                <option value="ALL">
                  All
                </option>

                <option value="CAR">
                  Cars
                </option>

                <option value="EV">
                  EVs
                </option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="empty-state">
              Loading parking data...
            </div>
          ) : filteredActiveParking.length === 0 ? (
            <div className="empty-state">
              No active vehicles found.
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>License Plate</th>
                    <th>Type</th>
                    <th>Floor</th>
                    <th>Slot</th>
                    <th>Entry Time</th>
                    <th>Action</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredActiveParking.map(
                    (vehicle) => (
                      <tr
                        key={vehicle.session_id}
                      >
                        <td>
                          <strong>
                            {vehicle.license_plate}
                          </strong>
                        </td>

                        <td>
                          <span
                            className={
                              vehicle.vehicle_type ===
                              "EV"
                                ? "vehicle-badge ev"
                                : "vehicle-badge car"
                            }
                          >
                            {vehicle.vehicle_type}
                          </span>
                        </td>

                        <td>
                          {vehicle.floor_id}
                        </td>

                        <td>
                          {vehicle.slot_number}
                        </td>

                        <td>
                          {formatDateTime(
                            vehicle.entry_time
                          )}
                        </td>

                        <td>
                          <button
                            className="small-button"
                            onClick={() => {
                              setCheckoutPlate(
                                vehicle.license_plate
                              );

                              window.scrollTo({
                                top: 0,
                                behavior: "smooth",
                              });
                            }}
                          >
                            Checkout
                          </button>
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>
                Parking Floors
              </h2>

              <p>
                Live parking slot availability
              </p>
            </div>
          </div>

          {Object.keys(slotsByFloor).length === 0 ? (
            <div className="empty-state">
              No parking slots available.
            </div>
          ) : (
            <div className="floors-container">
              {Object.entries(slotsByFloor).map(
                ([floorId, floorSlots]) => (
                  <div
                    className="floor-card"
                    key={floorId}
                  >
                    <div className="floor-header">
                      <h3>
                        Floor {floorId}
                      </h3>

                      <span>
                        {
                          floorSlots.filter(
                            (slot) =>
                              slot.status ===
                              "AVAILABLE"
                          ).length
                        }{" "}
                        available
                      </span>
                    </div>

                    <div className="slot-grid">
                      {floorSlots.map(
                        (slot) => (
                          <div
                            className={`slot ${
                              slot.status ===
                              "OCCUPIED"
                                ? "occupied"
                                : "available"
                            }`}
                            key={slot.slot_id}
                          >
                            <strong>
                              {slot.slot_number}
                            </strong>

                            <span>
                              {slot.slot_type}
                            </span>

                            <small>
                              {slot.status}
                            </small>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )
              )}
            </div>
          )}
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>
                Parking History
              </h2>

              <p>
                Completed parking transactions
              </p>
            </div>
          </div>

          {parkingHistory.length === 0 ? (
            <div className="empty-state">
              No completed parking transactions yet.
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>License Plate</th>
                    <th>Type</th>
                    <th>Floor</th>
                    <th>Slot</th>
                    <th>Duration</th>
                    <th>Amount</th>
                    <th>Payment</th>
                  </tr>
                </thead>

                <tbody>
                  {parkingHistory.map(
                    (record) => (
                      <tr
                        key={
                          record.session_id
                        }
                      >
                        <td>
                          <strong>
                            {record.license_plate}
                          </strong>
                        </td>

                        <td>
                          {record.vehicle_type}
                        </td>

                        <td>
                          {record.floor_id}
                        </td>

                        <td>
                          {record.slot_number}
                        </td>

                        <td>
                          {record.duration_hours
                            ? `${Number(
                                record.duration_hours
                              ).toFixed(2)} hrs`
                            : "-"}
                        </td>

                        <td>
                          ₹
                          {Number(
                            record.amount || 0
                          ).toFixed(2)}
                        </td>

                        <td>
                          <span className="paid-badge">
                            {record.payment_status ||
                              "PAID"}
                          </span>
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <span>
          Smart Parking System
        </span>

        <span>
          C++ Engine · FastAPI · SQLite · React
        </span>
      </footer>
    </div>
  );
}

export default App;