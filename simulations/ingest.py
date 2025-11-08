import grpc
import json
import time
from backend.generated import datavault_pb2
from backend.generated import datavault_pb2_grpc

def run():
    time.sleep(15)
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = datavault_pb2_grpc.DataVaultServiceStub(channel)
        
        # Ingest healthcare data
        with open('/app/simulations/datasets/healthcare.json', 'r') as f:
            healthcare_data = json.load(f)
            for record in healthcare_data:
                response = stub.Ingest(datavault_pb2.DataRecord(data_type='healthcare', data=json.dumps(record).encode()))
                print(f"Healthcare record ingested with ID: {response.id}, Status: {response.status}")
                
                # Verify decryption
                if response.status == "OK":
                    retrieve_response = stub.Retrieve(datavault_pb2.IngestResponse(id=response.id))
                    decrypted_data = json.loads(retrieve_response.data.decode('utf-8'))
                    print(f"  Decrypted Healthcare Data (ID: {response.id}): {decrypted_data}")

        # Ingest finance data
        with open('/app/simulations/datasets/finance.json', 'r') as f:
            finance_data = json.load(f)
            for record in finance_data:
                response = stub.Ingest(datavault_pb2.DataRecord(data_type='finance', data=json.dumps(record).encode()))
                print(f"Finance record ingested with ID: {response.id}, Status: {response.status}")

                # Verify decryption
                if response.status == "OK":
                    retrieve_response = stub.Retrieve(datavault_pb2.IngestResponse(id=response.id))
                    decrypted_data = json.loads(retrieve_response.data.decode('utf-8'))
                    print(f"  Decrypted Finance Data (ID: {response.id}): {decrypted_data}")

if __name__ == '__main__':
    run()
