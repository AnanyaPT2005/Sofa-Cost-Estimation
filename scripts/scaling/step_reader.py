#this is a loader.py

import json

from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone


def read_step(step_file):

    reader = STEPControl_Reader()

    status = reader.ReadFile(step_file)

    if status != IFSelect_RetDone:
        raise RuntimeError("STEP reading failed")

    print("STEP file loaded successfully")

    reader.TransferRoots()

    return reader.OneShape()


def load_metadata(metadata_file):

    with open(metadata_file, "r") as f:
        return json.load(f)