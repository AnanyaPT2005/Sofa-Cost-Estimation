from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone


def read_step(step_file):

    reader = STEPControl_Reader()

    status = reader.ReadFile(step_file)

    if status == IFSelect_RetDone:
        print("STEP file loaded successfully")
    else:
        print("STEP loading failed")

    if status != IFSelect_RetDone:
        raise RuntimeError("STEP reading failed")

    reader.TransferRoots()

    shape = reader.OneShape()

    return shape