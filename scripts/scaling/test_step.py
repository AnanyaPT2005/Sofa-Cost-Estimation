#this is a test file to read step file, resolve reference and try to enumerate bodies.
# it enumerates the bodies.

from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence
from pathlib import Path
from OCP.TDataStd import TDataStd_Name
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopoDS import TopoDS
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.TDF import TDF_Label
from scale_step import scale_seat
import inspect
import re   

STEP_FILE = r"G:\My Drive\sofa cost estimation\sofa 3d models\test_workfloe.step"

def get_step_body_names(step_path):
    """
    Reads MANIFOLD_SOLID_BREP names from a STEP file
    in the order they appear.
    """

    names = []

    pattern = re.compile(
        r"MANIFOLD_SOLID_BREP\('([^']+)'",
        re.IGNORECASE
    )

    with open(step_path, "r", encoding="utf-8", errors="ignore") as f:

        for line in f:

            m = pattern.search(line)

            if m:
                names.append(m.group(1))

    return names

print(Path(STEP_FILE).exists())
print(Path(STEP_FILE).resolve())
step_body_names = get_step_body_names(STEP_FILE)

print("\nBodies found in STEP:")

for i, name in enumerate(step_body_names, start=1):
    print(f"{i}. {name}")

doc = TDocStd_Document(TCollection_ExtendedString("doc"))

reader = STEPCAFControl_Reader()

status = reader.ReadFile(STEP_FILE)
print("Read status:", status)

if not reader.Transfer(doc):
    raise RuntimeError("Failed to transfer STEP into XDE document")

shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())

free_shapes = TDF_LabelSequence()
shape_tool.GetFreeShapes(free_shapes)

print("Free shapes:", free_shapes.Length())
print("\nFree shapes:", free_shapes.Length())

for i in range(1, free_shapes.Length() + 1):

    free_shape = free_shapes.Value(i)

    free_name = TDataStd_Name()

    if free_shape.FindAttribute(TDataStd_Name.GetID_s(), free_name):
        print("\nAssembly:", free_name.Get().ToExtString())
    else:
        print("\nAssembly: <No Name>")

    # -----------------------------------
    # Components
    # -----------------------------------

    children = TDF_LabelSequence()
    shape_tool.GetComponents_s(free_shape, children)

    print("Components:", children.Length())

    for j in range(1, children.Length() + 1):

        child = children.Value(j)

        child_name = TDataStd_Name()

        if child.FindAttribute(TDataStd_Name.GetID_s(), child_name):
            print(f"  Component {j}: {child_name.Get().ToExtString()}")
            print("    Is Assembly   :", shape_tool.IsAssembly_s(child))
            print("    Is Component  :", shape_tool.IsComponent_s(child))
            print("    Is Compound   :", shape_tool.IsCompound_s(child))
            print("    Is SimpleShape:", shape_tool.IsSimpleShape_s(child))
            print("    Is Reference  :", shape_tool.IsReference_s(child))
            
            
        else:
            print(f"  Component {j}: <No Name>")
        

        # -----------------------------------
        # Resolve reference
        # -----------------------------------

        if shape_tool.IsReference_s(child):

            from OCP.TDF import TDF_Label

            referred = TDF_Label()

            ok = shape_tool.GetReferredShape_s(
                child,
                referred,
            )

            print("Resolved:", ok)
            # methods = [m for m in dir(shape_tool) if "Search" in m or "Label" in m or "Shape" in m]
            # for m in sorted(methods):
            #     print(m)
            referred_name = TDataStd_Name()

            if referred.FindAttribute(TDataStd_Name.GetID_s(), referred_name):
                print("    Refers to :", referred_name.Get().ToExtString())
            else:
                print("    Refers to : <No Name>")

            print("    Is SimpleShape :", shape_tool.IsSimpleShape_s(referred))
            print("    Is Assembly    :", shape_tool.IsAssembly_s(referred))
            print("    Is Component  :", shape_tool.IsComponent_s(referred))
            shape = shape_tool.GetShape_s(referred)

            print(shape)
            print("\nEnumerating solids...")

            explorer = TopExp_Explorer(shape, TopAbs_SOLID)

            count = 0
            processed_solids = []

            while explorer.More():

                count += 1

                solid = TopoDS.Solid_s(explorer.Current())
                if count <= len(step_body_names):
                    body_name = step_body_names[count - 1]
                else:
                    body_name = "<Unknown>"

                print("\n" + "=" * 60)
                print(f"Solid {count} : {body_name}")
                # ----------------------------------
                # Call scaling function for seat only
                # ----------------------------------

                if body_name == "seat":

                    print("Calling scale_seat()...")

                    solid = scale_seat(solid)

                # ----------------------------
                # Bounding Box
                # ----------------------------

                box = Bnd_Box()

                BRepBndLib.Add_s(
                    solid,
                    box,
                )

                xmin, ymin, zmin, xmax, ymax, zmax = box.Get()

                print(f"X : {xmin:.2f} -> {xmax:.2f}")
                print(f"Y : {ymin:.2f} -> {ymax:.2f}")
                print(f"Z : {zmin:.2f} -> {zmax:.2f}")

                print(f"L = {xmax - xmin:.2f}")
                print(f"W = {ymax - ymin:.2f}")
                print(f"H = {zmax - zmin:.2f}")
                processed_solids.append(solid)

                explorer.Next()

            print(f"\nTotal solids found: {count}")
            print(f"Processed solids: {len(processed_solids)}")