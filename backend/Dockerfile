FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY cpp-engine ./cpp-engine

RUN mkdir -p cpp-engine/build

RUN g++ \
    -shared \
    -fPIC \
    -Icpp-engine/include \
    cpp-engine/src/ParkingEngineAPI.cpp \
    -o cpp-engine/build/libparking_engine.so

RUN mkdir -p database

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]