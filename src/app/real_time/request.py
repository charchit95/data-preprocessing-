""" RealTimeRequest class definition. """

from pydantic import BaseModel
import re
import json


class KPIStreamingRequest(BaseModel):
    kpis: list[str]  # lis of all kpis
    machines: list[str]  # list of all machines
    operations: list[str]  # list of all operations
    special: bool


class KPIValidator:
    def __init__(self, kpis: list[str], machines: list[str], operations: list[str]):
        split_kpis = [re.split(r"_(?=[^_]*$)", kpi) for kpi in kpis]
        self.kpis = [item[0] for item in split_kpis]
        self.aggregations = [item[1] for item in split_kpis]
        self.machines = machines
        self.operations = operations
        self.kpi_count = len(kpis)
        self.machine_count = len(machines)

    @classmethod
    def from_streaming_request(cls, kpi_streaming_request: KPIStreamingRequest):
        return cls(
            kpis=kpi_streaming_request.kpis,
            machines=kpi_streaming_request.machines,
            operations=kpi_streaming_request.operations,
        )

    def check_special_request_validity(self):
        return self.kpi_count == len(self.operations)

    def validate(self, cleaned_data: dict):
        kpi = cleaned_data.get("kpi", None)
        machine = cleaned_data.get("name", None)
        operation = cleaned_data.get("operation", None)

        if kpi is None or machine is None or operation is None:
            print("The sensor didn't send the correct data.")
            return False

        return (
            kpi in self.kpis
            and machine in self.machines
            and operation in self.operations
            and cleaned_data[self.get_aggregation_from_kpi(kpi)] is not None
        )

    def get_aggregation_from_kpi(self, kpi: str):
        return self.aggregations[self.kpis.index(kpi)]

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
