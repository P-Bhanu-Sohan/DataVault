FROM python:3.9

WORKDIR /app
ENV PYTHONPATH /app:/app/backend/generated

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Install grpcio-tools for protobuf generation
RUN pip install grpcio-tools

# Install net-tools for netstat
RUN apt-get update && apt-get install -y net-tools

COPY proto /app/proto

# Create the generated directory within backend
RUN mkdir -p /app/backend/generated
RUN touch /app/backend/generated/__init__.py

# Generate protobuf files directly into the backend/generated directory
RUN python -m grpc_tools.protoc -I/app/proto --python_out=/app/backend/generated --grpc_python_out=/app/backend/generated /app/proto/datavault.proto

COPY backend /app/backend
COPY simulations /app/simulations
COPY test.py /app/test.py

CMD ["python", "backend/main.py"]
