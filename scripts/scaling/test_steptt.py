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
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.TDF import TDF_Label
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from scale_step2 import scale_seat
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf
import inspect
import re   
from OCP.TopAbs import TopAbs_FACE
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepTools import BRepTools
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.Bnd import Bnd_OBB
from OCP.BRepBndLib import BRepBndLib
from position_engine2 import move_body
from position_engine2 import get_overlap
from position_engine2 import vector_between
from position_engine2 import get_obb
from position_engine2 import projection_on_axis
from position_engine2 import classify_attachment
from scale_step2 import get_logical_dimension

STEP_FILE = r"C:\Users\DEEPIKA.S\Desktop\sofa_cost\Sofa-Cost-Estimation\scripts\scaling\test_workfloe.step"
OUTPUT_STEP = r"C:\Users\DEEPIKA.S\Desktop\sofa_cost\Sofa-Cost-Estimation\scripts\scaling\scaled_step.step"

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
            # -----------------------------------
            # Component placement
            # -----------------------------------

            location = shape_tool.GetShape_s(child).Location()

            print("\nLocation:")
            trsf = location.Transformation()

            print("\nTransformation:")
            vec_x = trsf.VectorialPart().Column(1)
            vec_y = trsf.VectorialPart().Column(2)
            vec_z = trsf.VectorialPart().Column(3)

            print("\nLocal Axes")

            print(
                "X:",
                vec_x.X(),
                vec_x.Y(),
                vec_x.Z(),
            )

            print(
                "Y:",
                vec_y.X(),
                vec_y.Y(),
                vec_y.Z(),
            )

            print(
                "Z:",
                vec_z.X(),
                vec_z.Y(),
                vec_z.Z(),
            )

            print("\nEnumerating solids...")

            explorer = TopExp_Explorer(shape, TopAbs_SOLID)

            count = 0
            
        
            scaled_seat = None
            right_arm = None
            seat_scale_info = None
            processed_solids = []
            all_bodies = []

            while explorer.More():

                count += 1

                solid = TopoDS.Solid_s(explorer.Current())
                if count <= len(step_body_names):
                    body_name = step_body_names[count - 1]
                else:
                    body_name = "<Unknown>"

                print("\n" + "=" * 60)
                print(f"Solid {count} : {body_name}")
                

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

                print("\nComputing Oriented Bounding Box...")

                obb = Bnd_OBB()

                BRepBndLib.AddOBB_s(
                    solid,
                    obb,
                    True,   # use triangulation
                    True,   # optimal
                    True    # shape tolerance
                )

                # ----------------------------------
                # Call scaling function for seat only
                # ----------------------------------

                if body_name == "seat":

                    
                    solid, scale_info = scale_seat(
                        solid,
                        obb,
                        body_name="seat",
                        logical_dimension="length",
                        factor=2.0,    
                    )
                    scaled_seat = solid
                    seat_scale_info = scale_info
                    print("\nScale Info")

                    for key, value in scale_info.items():
                        print(f"{key} : {value}")

                if body_name == "right_arm":
                    right_arm = solid

                if body_name == "left_arm":
                    left_arm = solid        

                print("OBB computed.")

                center = obb.Center()

                print("\n" + "=" * 60)
                print(f"OBB for {body_name}")

                center = obb.Center()

                print(
                    f"Center : ({center.X():.2f}, "
                    f"{center.Y():.2f}, "
                    f"{center.Z():.2f})"
                )

                xdir = obb.XDirection()
                ydir = obb.YDirection()
                zdir = obb.ZDirection()

                print(
                    f"Local X : ({xdir.X():.3f}, "
                    f"{xdir.Y():.3f}, "
                    f"{xdir.Z():.3f})"
                )

                print(
                    f"Local Y : ({ydir.X():.3f}, "
                    f"{ydir.Y():.3f}, "
                    f"{ydir.Z():.3f})"
                )

                print(
                    f"Local Z : ({zdir.X():.3f}, "
                    f"{zdir.Y():.3f}, "
                    f"{zdir.Z():.3f})"
                )

                print(
                    f"OBB X Size : {2*obb.XHSize():.2f}"
                )

                print(
                    f"OBB Y Size : {2*obb.YHSize():.2f}"
                )

                print(
                    f"OBB Z Size : {2*obb.ZHSize():.2f}"
                )                # ----------------------------------------
                # Test: Print face normals of seat only
                # ----------------------------------------

                if body_name == "seat":

                    print("\nFace normals:")

                    face_explorer = TopExp_Explorer(
                        solid,
                        TopAbs_FACE
                    )

                    face_count = 0

                    while face_explorer.More():

                        face_count += 1

                        face = TopoDS.Face_s(face_explorer.Current())

                        surface = BRepAdaptor_Surface(face)

                        if surface.GetType() == GeomAbs_Plane:

                            u1, u2, v1, v2 = BRepTools.UVBounds_s(face)

                            u = (u1 + u2) / 2
                            v = (v1 + v2) / 2

                            props = BRepLProp_SLProps(
                                surface,
                                u,
                                v,
                                1,
                                1e-6
                            )

                            if props.IsNormalDefined():

                                n = props.Normal()

                                print(
                                    f"Face {face_count}: "
                                    f"({n.X():.3f}, {n.Y():.3f}, {n.Z():.3f})"
                                )

                        face_explorer.Next()

                all_bodies.append(
                    {
                        "name": body_name,
                        "shape": solid,
                    }
                )
                processed_solids.append(solid)

                explorer.Next()
                # explorer loop ends here

            print("\nDEBUG")
            print("scaled_seat:", scaled_seat is None)
            print("right_arm:", right_arm is None)
            print("seat_scale_info:", seat_scale_info is None)
            overlap = get_overlap(
                scaled_seat,
                right_arm,
                seat_scale_info,
            )

            print("\nOverlap:", overlap)

            print(f"\nTotal solids found: {count}")
            print(f"Processed solids: {len(processed_solids)}")
            attachment_map = []
            for body in all_bodies:

                if body["name"] == "seat":
                    continue

                vec = vector_between(
                    scaled_seat,
                    body["shape"],
                )
                seat_obb = get_obb(scaled_seat)

                x_axis = seat_obb.XDirection()
                y_axis = seat_obb.YDirection()
                z_axis = seat_obb.ZDirection()

                px = projection_on_axis(
                    vec,
                    x_axis,
                )

                py = projection_on_axis(
                    vec,
                    y_axis,
                )

                pz = projection_on_axis(
                    vec,
                    z_axis,
                )
                sign, axis = classify_attachment(
                    px,
                    py,
                    pz,
                )
                logical = get_logical_dimension(
                    "seat",
                    axis,
                )

                attachment_map.append(
                {
                    "name": body["name"],
                    "shape": body["shape"],
                    "attachment": f"{sign}{logical}",
                }
                )
            print("\nAttachment Map")

            for item in attachment_map:

                print(
                    item["name"],
                    "->",
                    item["attachment"],
                ) 

            print("\nMoving Bodies")

            for item in attachment_map:

                attachment = item["attachment"]

                sign = attachment[0]
                logical_dimension = attachment[1:]

                if logical_dimension != seat_scale_info["logical_dimension"]:
                    continue

                if sign == "+":

                    item["shape"] = move_body(
                        item["shape"],
                        seat_scale_info["direction"],
                        overlap,
                    )

                    print(item["name"], "moved", attachment)

                elif sign == "-":

                    item["shape"] = move_body(
                        item["shape"],
                        seat_scale_info["direction"],
                        -overlap,
                    )

                    print(item["name"], "moved", attachment)
            for i, solid in enumerate(processed_solids):

                if step_body_names[i] == "seat":
                    processed_solids[i] = scaled_seat

                else:

                    for item in attachment_map:

                        if item["name"] == step_body_names[i]:
                            processed_solids[i] = item["shape"]
                            break
            # ----------------------------------
            # Build a new compound
            # ----------------------------------
            print("\nProcessed bodies:")

            for s in processed_solids:
                print(s)

            builder = BRep_Builder()

            compound = TopoDS_Compound()

            builder.MakeCompound(compound)

            for solid in processed_solids:
                builder.Add(compound, solid)

            print("\nNew compound created successfully.")
            print(f"Contains {len(processed_solids)} solids.")
            # ----------------------------------
            # Export STEP
            # ----------------------------------

            writer = STEPControl_Writer()

            writer.Transfer(
                compound,
                STEPControl_AsIs,
            )

            status = writer.Write(OUTPUT_STEP)

            if status == IFSelect_RetDone:
                print("\nSTEP exported successfully!")
                print(OUTPUT_STEP)
            else:
                print("\nSTEP export failed!")