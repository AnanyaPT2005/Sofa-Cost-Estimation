# phase 4 A – External Scaling Rules (Prototype v1)

## Purpose

Convert the ratios produced by Phase 3 into real-world dimensions for the external CAD components using:

- Phase 3 JSON
- component_dataset.csv (renamed_sofa_component.csv)
- updated_sofa_metadata.csv (see in data folder)
- User supplied Overall Length, Depth and Height

Output: scaled_external.json

## Example Phase 3 Output

{
"template_version":1,
"sofa_type":"Straight",
"seat_count":3,
"seat_configuration":"Jointed",
"components":{
"seat":{"bbox":{"width_ratio":0.78,"depth_ratio":0.44,"height_ratio":0.22}},
"backrest":{"bbox":{"width_ratio":0.79,"thickness_ratio":0.11,"height_ratio":0.51}},
"armrest":{"bbox":{"width_ratio":0.12,"depth_ratio":0.43,"height_ratio":0.61}}
},
"materials":{
"fabric":"Fabric",
"armrest_frame":"Wood",
"backrest_frame":"Wood",
"leg_material":"Unknown"
},
"leg_count":4
}

## External Components we will be scaling:

- Foam
- Handle Foam
- Fabric (later)

## Rules

1. Scale only components whose Visibility = External.
2. Ignore fabric in Version 1.
3. Never merge bodies using geometry alone.
4. Create logical component groups using body-name prefixes.

### Logical Component Groups

Seat:

- seat_top\*
- seat_front\*
- seat_back\*

Backrest:

- backrest_front\*
- backrest_top\*
- backrest_back\*

Right Armrest:

- right_armrest_top\*
- right_armrest_front\*
- right_armrest_back\*
- right_armrest_base\*

Left Armrest:

- left_armrest_top\*
- left_armrest_front\*
- left_armrest_back\*
- left_armrest_base\*

('\*' includes duplicate bodies such as (1), (2), ...)

5. Merge duplicate bodies ONLY inside the same logical component.

Example:

right_armrest_top
Length = 179.77

right_armrest_top (1)
Length = 38.40

Merged Length = 218.17

Use the common (or maximum) Width and Height if they differ only slightly.

Never merge Left and Right armrests.

6. Compute logical dimensions using Module 2 ratios.

Seat Width = seat.width_ratio × Overall Length
Seat Depth = seat.depth_ratio × Overall Depth
Seat Height = seat.height_ratio × Overall Height

Backrest Width = backrest.width_ratio × Overall Length
Backrest Height = backrest.height_ratio × Overall Height
Backrest Thickness = backrest.thickness_ratio × Overall Depth

Armrest Width = armrest.width_ratio × Overall Length
Armrest Depth = armrest.depth_ratio × Overall Depth
Armrest Height = armrest.height_ratio × Overall Height

7. Seat Configuration

Jointed:
Scale the seat as one component.

Separate:
Each Seat Width = Total Seat Width / Seat Count.

## Rule 8 – Validate Sofa Attributes Before Scaling

Before applying any scaling rules, verify the sofa metadata.

### Seat Configuration

If `Seat_Configuration = Jointed`

- Treat the entire seat as a single continuous component.
- Ignore the `seat_count` variable during seat scaling.
- Scale the seat directly using the user-provided Overall Length, Overall Depth and Overall Height together with the ratios obtained from Phase 3.

If `Seat_Configuration = Separate`

- Divide the scaled seat width equally among all seats.

9. Apply the scaled logical dimensions back to EVERY CAD body belonging to that logical group.

Example:
Seat -> seat_top, seat_front, seat_back
Right Armrest -> right_armrest_top, right_armrest_top (1), right_armrest_front, right_armrest_back, right_armrest_base

Output a body-level JSON (scaled_external.json).

## Future Improvements

- Similar template selection before scaling.
- Preserve curved armrest/backrest profiles instead of approximating them with bounding boxes.
- Fabric thickness compensation.
- Rules for asymmetric sofas.
