import grpc
import json
import time
from backend.generated import datavault_pb2, datavault_pb2_grpc

def ingest_data(records, data_type):
    """
    Ingests a list of records into the DataVault via gRPC.
    """
    with grpc.insecure_channel('backend:50051') as channel:
        stub = datavault_pb2_grpc.DataVaultServiceStub(channel)
        for record in records:
            response = stub.Ingest(datavault_pb2.DataRecord(data_type=data_type, data=json.dumps(record).encode()))
            print(f"{data_type.capitalize()} record ingested with ID: {response.id}, Status: {response.status}")

def run():
    """
    Reads data from JSON files and ingests it into the DataVault via gRPC.
    """
    # Wait for the gRPC server to be ready
    time.sleep(15)

    # Ingest healthcare data
    with open('/app/simulations/datasets/healthcare.json', 'r') as f:
        healthcare_data = json.load(f)
        ingest_data(healthcare_data, 'healthcare')

    # Ingest finance data
    with open('/app/simulations/datasets/finance.json', 'r') as f:
        finance_data = json.load(f)
        ingest_data(finance_data, 'finance')

if __name__ == '__main__':
    run()
