#this is a loader.py

import json
from bbox_engine import compute_obb
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib


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
    
def get_template_frame(reference_shape):

    obb = compute_obb(reference_shape)

    return {
        "X": obb.XDirection(),
        "Y": obb.YDirection(),
        "Z": obb.ZDirection(),
    }

def get_assembly_dimensions(solids):

    box = Bnd_Box()

    for solid in solids:

        BRepBndLib.Add_s(
            solid,
            box,
        )

    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()

    return {
        "length": zmax - zmin,
        "width": ymax - ymin,
        "height": xmax - xmin,
    }