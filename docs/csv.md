# CSV Outputs

## 1. `component_dataset.csv`

**One row = One CAD body/component**

| Column                | Description                           |
| --------------------- | ------------------------------------- |
| Body                  | Unique body name                      |
| Category              | Seat, Backrest, Armrest, Spring, etc. |
| Appearance            | CAD appearance/material               |
| Visibility            | Internal / External                   |
| Measurement_Type      | Continuous / Discrete                 |
| Length, Width, Height | Bounding box dimensions               |
| Volume                | Component volume                      |
| Min/Max Coordinates   | Bounding box limits                   |
| Center Coordinates    | Component center position             |

---

## 2. `sofa_metadata.csv`

**One row = One sofa template**

| Column                  | Description                     |
| ----------------------- | ------------------------------- |
| Template_ID             | Unique sofa template ID         |
| Template_Name           | Template name                   |
| Sofa_Type               | Straight, L-shape, Chaise, etc. |
| Seat_Count              | Number of seats                 |
| Overall_Length          | Sofa length                     |
| Overall_Depth           | Sofa depth                      |
| Overall_Height          | Sofa height                     |
| Seat_Width              | Overall seat width              |
| Seat_Depth              | Seat depth                      |
| Seat_Height             | Seat height                     |
| Backrest_Height         | Backrest height                 |
| Armrest_Height          | Armrest height                  |
| Seat_Configuration      | Jointed / Separate              |
| Armrest_Frame_Material  | Wood / Metal                    |
| Backrest_Frame_Material | Wood / Metal                    |
| Fabric_Material         | Fabric type                     |
| Leg_Count               | Number of legs                  |
| Leg_Material            | Wood / Metal / Plastic          |

---
