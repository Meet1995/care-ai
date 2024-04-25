from datetime import datetime
from firebase_admin import credentials, db
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
import firebase_admin
from typing import List, Union


def initiate_firebase_app(database_url, access_json):
    cred = credentials.Certificate(access_json)
    firebase_admin.initialize_app(cred, {"databaseURL": database_url})


class PatientTempInput(BaseModel):
    patient_id: Union[int, str] = Field(
        ...,
        description="""ID of the patient for which the temperature
        data is pulled for 10 timesteps.""",
    )


@tool(args_schema=PatientTempInput)
def get_patient_temperature(
    patient_id: Union[int, str]
) -> List[List[Union[str, float]]]:
    """Function to get patient temperature data for 10 timesteps.

    Args:
        patient_id (Union[int, str]): ID of the patient for which the
        temperature is pulled.

    Returns:
        list[list[str, float]]: List of lists containing timestamp and its
        corresponding temperature.
    """

    patient_ref = db.reference(f"/{patient_id}/temperature/")
    data = patient_ref.get()
    if data is not None:
        data = sorted(
            list(map(lambda value: [float(x) for x in value.split(":")], data)),
            key=lambda x: x[0],
        )
        data = [[str(datetime.fromtimestamp(x[0])), x[1]] for x in data]
    else:
        data = f"Database does not contain information for patient id: {patient_id}"
    return data


class PatientSpo2Input(BaseModel):
    patient_id: Union[int, str] = Field(
        ...,
        description="""ID of the patient for which the Blood Oxygen (SpO2)
        data is pulled for 10 timesteps.""",
    )


@tool(args_schema=PatientSpo2Input)
def get_patient_spo2(patient_id: Union[int, str]) -> list[list[str, float]]:
    """Function to get patient SPO2 data for 10 timesteps.

    Args:
        patient_id (Union[int, str]): ID of the patient for which the SPO2 is pulled.

    Returns:
        list[list[str, float]]: List of lists containing timestamp and its
        corresponding SPO2.
    """
    patient_ref = db.reference(f"/{patient_id}/spo2/")
    data = patient_ref.get()
    if data is not None:
        data = sorted(
            list(map(lambda value: [float(x) for x in value.split(":")], data)),
            key=lambda x: x[0],
        )
        data = [[str(datetime.fromtimestamp(x[0])), x[1]] for x in data]
    else:
        data = f"Database does not contain information for patient id: {patient_id}"
    return data


class PatientPulseInput(BaseModel):
    patient_id: Union[int, str] = Field(
        ...,
        description="""ID of the patient for which the pulse rate
        data is pulled for 10 timesteps.""",
    )


@tool(args_schema=PatientPulseInput)
def get_patient_pulse_or_pulse_rate(
    patient_id: Union[int, str]
) -> list[list[str, float]]:
    """Function to get patient pulse rate data for 10 timesteps.

    Args:
        patient_id (Union[int, str]): ID of the patient for which the
        pulse rate is pulled.

    Returns:
        list[list[str, float]]: List of lists containing timestamp and its
        corresponding pulse rate.
    """
    patient_ref = db.reference(f"/{patient_id}/pulse/")
    data = patient_ref.get()
    if data is not None:
        data = sorted(
            list(map(lambda value: [float(x) for x in value.split(":")], data)),
            key=lambda x: x[0],
        )
        data = [[str(datetime.fromtimestamp(x[0])), x[1]] for x in data]
    else:
        data = f"Database does not contain information for patient id: {patient_id}"
    return data
