from ultralytics import YOLO
import cv2
import numpy as np
import json
import os


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "runs/segment/runs/segment_final/weights/best.pt"

OUTPUT_DIR = "runs/phase3_output"
JSON_PATH = "outputs/phase3.json"
MASK_PATH = "outputs/3seatersofa_mask.png"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("outputs", exist_ok=True)


# ============================================================
# LOAD MODEL
# ============================================================

model = YOLO(MODEL_PATH)

print("Loaded classes:")
print(model.names)


# ============================================================
# IMAGE PATH
# ============================================================

image_path = input("\nEnter the sofa image path: ").strip()

if not os.path.exists(image_path):
    print("\nERROR: Image does not exist.")
    print(image_path)
    exit()


# ============================================================
# LOAD IMAGE
# ============================================================

original = cv2.imread(image_path)

if original is None:
    print("\nERROR: Could not read image.")
    exit()

height, width = original.shape[:2]

print("\nOriginal image size:")
print("Width :", width)
print("Height:", height)


# ============================================================
# RUN YOLO
# ============================================================

results = model.predict(
    source=image_path,
    conf=0.25,
    imgsz=640,
    save=False,
    verbose=True
)

result = results[0]


# ============================================================
# CHECK MASKS
# ============================================================

if result.masks is None:
    print("\nERROR: Model did not return segmentation masks.")
    exit()

print("\nSegmentation masks found:", len(result.masks.xy))


# ============================================================
# STORE DETECTIONS
# ============================================================

detections = []

for i in range(len(result.boxes)):

    class_id = int(result.boxes.cls[i])
    confidence = float(result.boxes.conf[i])
    class_name = model.names[class_id]

    bbox = (
        result.boxes.xyxy[i]
        .cpu()
        .numpy()
        .tolist()
    )

    polygon = result.masks.xy[i]

    if polygon is None or len(polygon) < 3:
        continue

    polygon = np.array(
        polygon,
        dtype=np.float32
    )

    center_x = (bbox[0] + bbox[2]) / 2
    center_y = (bbox[1] + bbox[3]) / 2

    detections.append({
        "index": i,
        "class_id": class_id,
        "class_name": class_name,
        "confidence": confidence,
        "bbox": bbox,
        "polygon": polygon,
        "center_x": center_x,
        "center_y": center_y
    })


# ============================================================
# FIND ARMRESTS
# ============================================================

armrests = []

for d in detections:

    if d["class_name"].lower() in [
        "leftarmrest",
        "rightarmrest"
    ]:
        armrests.append(d)

print("\nRaw armrest detections:", len(armrests))


# ============================================================
# ARMREST ASSIGNMENT
#
# IMPORTANT:
#
# Image LEFT  = person's RIGHT armrest
# Image RIGHT = person's LEFT armrest
#
# We completely ignore YOLO's armrest class name.
# Position decides the final name.
# ============================================================

left_side_candidates = []
right_side_candidates = []

for arm in armrests:

    if arm["center_x"] < width / 2:
        left_side_candidates.append(arm)
    else:
        right_side_candidates.append(arm)


# ============================================================
# SELECT BEST ARMREST FROM EACH SIDE
# ============================================================

best_image_left = None
best_image_right = None

if left_side_candidates:

    best_image_left = max(
        left_side_candidates,
        key=lambda x: x["confidence"]
    )

if right_side_candidates:

    best_image_right = max(
        right_side_candidates,
        key=lambda x: x["confidence"]
    )


final_armrests = []


# Image-left = person's RIGHT armrest
if best_image_left is not None:

    best_image_left["final_name"] = "rightarmrest"

    final_armrests.append(best_image_left)


# Image-right = person's LEFT armrest
if best_image_right is not None:

    best_image_right["final_name"] = "leftarmrest"

    final_armrests.append(best_image_right)


# ============================================================
# PRINT ARMREST RESULT
# ============================================================

print("\n========================================")
print("ARMREST ASSIGNMENT")
print("========================================")

for arm in final_armrests:

    print(
        arm["final_name"],
        "| confidence:",
        round(arm["confidence"], 4),
        "| center_x:",
        round(arm["center_x"], 2)
    )


# ============================================================
# REMOVE ARMRESTS FROM NORMAL COMPONENTS
# ============================================================

normal_detections = []

for d in detections:

    if d in armrests:
        continue

    normal_detections.append(d)


# ============================================================
# REMOVE DUPLICATES
#
# Keep only the strongest detection for components that
# should normally appear once.
#
# Legs and pillows can have multiple instances.
# ============================================================

SINGLE_COMPONENTS = [
    "backrest",
    "seat",
    "base"
]

filtered_components = []

for class_name in SINGLE_COMPONENTS:

    same_class = [
        d for d in normal_detections
        if d["class_name"].lower() == class_name
    ]

    if len(same_class) > 0:

        strongest = max(
            same_class,
            key=lambda x: x["confidence"]
        )

        filtered_components.append(strongest)


# ============================================================
# KEEP MULTIPLE-INSTANCE COMPONENTS
# ============================================================

MULTIPLE_COMPONENTS = [
    "leg",
    "pillow"
]

for d in normal_detections:

    if d["class_name"].lower() in MULTIPLE_COMPONENTS:
        filtered_components.append(d)


# ============================================================
# FIND 3SEATERSOFA
# ============================================================

sofa_detections = [
    d for d in detections
    if d["class_name"].lower() == "3seatersofa"
]

best_sofa = None

if sofa_detections:

    best_sofa = max(
        sofa_detections,
        key=lambda x: x["confidence"]
    )

    print("\n3seatersofa directly detected.")
    print(
        "Confidence:",
        round(best_sofa["confidence"], 4)
    )

else:

    print("\n3seatersofa was NOT directly detected.")
    print("Building sofa boundary from detected components...")


# ============================================================
# CREATE SOFA MASK
# ============================================================

sofa_mask = np.zeros(
    (height, width),
    dtype=np.uint8
)


# ============================================================
# IF 3SEATERSOFA MASK EXISTS, USE IT
# ============================================================

if best_sofa is not None:

    polygon = np.round(
        best_sofa["polygon"]
    ).astype(np.int32)

    polygon[:, 0] = np.clip(
        polygon[:, 0],
        0,
        width - 1
    )

    polygon[:, 1] = np.clip(
        polygon[:, 1],
        0,
        height - 1
    )

    cv2.fillPoly(
        sofa_mask,
        [polygon],
        255
    )


# ============================================================
# OTHERWISE BUILD SOFA MASK FROM COMPONENTS
# ============================================================

else:

    # Add normal components
    for d in filtered_components:

        polygon = np.round(
            d["polygon"]
        ).astype(np.int32)

        polygon[:, 0] = np.clip(
            polygon[:, 0],
            0,
            width - 1
        )

        polygon[:, 1] = np.clip(
            polygon[:, 1],
            0,
            height - 1
        )

        cv2.fillPoly(
            sofa_mask,
            [polygon],
            255
        )

    # Add selected armrests
    for arm in final_armrests:

        polygon = np.round(
            arm["polygon"]
        ).astype(np.int32)

        polygon[:, 0] = np.clip(
            polygon[:, 0],
            0,
            width - 1
        )

        polygon[:, 1] = np.clip(
            polygon[:, 1],
            0,
            height - 1
        )

        cv2.fillPoly(
            sofa_mask,
            [polygon],
            255
        )


# ============================================================
# MORPHOLOGICAL CLEANING
# ============================================================

kernel = np.ones(
    (15, 15),
    np.uint8
)

sofa_mask = cv2.morphologyEx(
    sofa_mask,
    cv2.MORPH_CLOSE,
    kernel
)


# ============================================================
# FIND SOFA BOUNDARY
# ============================================================

contours, _ = cv2.findContours(
    sofa_mask,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

if len(contours) == 0:

    print("\nERROR: Could not create sofa mask.")
    exit()


# ============================================================
# FINAL MASK
# ============================================================

contours = sorted(
    contours,
    key=cv2.contourArea,
    reverse=True
)

final_mask = np.zeros(
    (height, width),
    dtype=np.uint8
)

for contour in contours:

    area = cv2.contourArea(contour)

    if area > 100:

        cv2.drawContours(
            final_mask,
            [contour],
            -1,
            255,
            -1
        )


# ============================================================
# SAVE MASK
# ============================================================

cv2.imwrite(
    MASK_PATH,
    final_mask
)


# ============================================================
# GET SOFA BBOX
# ============================================================

ys, xs = np.where(
    final_mask > 0
)

if len(xs) == 0:

    print("\nERROR: Empty sofa mask.")
    exit()

x1 = float(xs.min())
y1 = float(ys.min())
x2 = float(xs.max())
y2 = float(ys.max())

sofa_bbox = [
    round(x1, 2),
    round(y1, 2),
    round(x2, 2),
    round(y2, 2)
]


# ============================================================
# CREATE COMPONENT JSON
# ============================================================

components = []

# Normal components
for d in filtered_components:

    components.append({
        "component": d["class_name"],
        "confidence": round(
            d["confidence"],
            4
        ),
        "bbox": [
            round(v, 2)
            for v in d["bbox"]
        ]
    })


# Corrected armrests
for arm in final_armrests:

    components.append({
        "component": arm["final_name"],
        "confidence": round(
            arm["confidence"],
            4
        ),
        "bbox": [
            round(v, 2)
            for v in arm["bbox"]
        ]
    })


# ============================================================
# SOFA CONFIDENCE
# ============================================================

sofa_confidence = None

if best_sofa is not None:

    sofa_confidence = round(
        best_sofa["confidence"],
        4
    )


# ============================================================
# PHASE 3 JSON
# ============================================================

output = {

    "detected_object": "sofa",

    "predicted_type": "3_seater",

    "image_width": width,

    "image_height": height,

    "bbox": sofa_bbox,

    "mask_path": MASK_PATH,

    "sofa_confidence": sofa_confidence,

    "components": components
}


# ============================================================
# SAVE JSON
# ============================================================

with open(
    JSON_PATH,
    "w"
) as f:

    json.dump(
        output,
        f,
        indent=4
    )


# ============================================================
# CREATE OUTPUT IMAGE
# ============================================================

output_image = original.copy()


# ============================================================
# DRAW NORMAL COMPONENTS
# ============================================================

for d in filtered_components:

    polygon = np.round(
        d["polygon"]
    ).astype(np.int32)

    polygon[:, 0] = np.clip(
        polygon[:, 0],
        0,
        width - 1
    )

    polygon[:, 1] = np.clip(
        polygon[:, 1],
        0,
        height - 1
    )

    cv2.polylines(
        output_image,
        [polygon],
        True,
        (0, 255, 255),
        3
    )

    x = int(
        max(
            0,
            d["bbox"][0]
        )
    )

    y = int(
        max(
            30,
            d["bbox"][1]
        )
    )

    label = (
        f'{d["class_name"]} '
        f'{d["confidence"]:.2f}'
    )

    cv2.putText(
        output_image,
        label,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
        cv2.LINE_AA
    )


# ============================================================
# DRAW CORRECTED ARMRESTS
# ============================================================

for arm in final_armrests:

    polygon = np.round(
        arm["polygon"]
    ).astype(np.int32)

    polygon[:, 0] = np.clip(
        polygon[:, 0],
        0,
        width - 1
    )

    polygon[:, 1] = np.clip(
        polygon[:, 1],
        0,
        height - 1
    )

    cv2.polylines(
        output_image,
        [polygon],
        True,
        (0, 255, 0),
        4
    )

    x = int(
        max(
            0,
            arm["bbox"][0]
        )
    )

    y = int(
        max(
            35,
            arm["bbox"][1]
        )
    )

    label = (
        f'{arm["final_name"]} '
        f'{arm["confidence"]:.2f}'
    )

    cv2.putText(
        output_image,
        label,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        3,
        cv2.LINE_AA
    )


# ============================================================
# DRAW OVERALL SOFA OUTLINE
# ============================================================

final_contours, _ = cv2.findContours(
    final_mask,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

largest_contour = None
largest_area = 0

for contour in final_contours:

    area = cv2.contourArea(contour)

    if area > 100:

        cv2.drawContours(
            output_image,
            [contour],
            -1,
            (255, 0, 0),
            4
        )

        if area > largest_area:

            largest_area = area
            largest_contour = contour


# ============================================================
# WRITE 3SEATERSOFA LABEL
#
# IMPORTANT CHANGE:
#
# If YOLO directly detected 3seatersofa,
# use its own bounding box for the label.
#
# Otherwise use the generated sofa boundary.
# ============================================================

if best_sofa is not None:

    # Use actual YOLO 3seatersofa bounding box
    sofa_x1 = int(
        max(
            5,
            best_sofa["bbox"][0]
        )
    )

    sofa_y1 = int(
        max(
            35,
            best_sofa["bbox"][1]
        )
    )

    sofa_label = (
        f'3seatersofa '
        f'{best_sofa["confidence"]:.2f}'
    )

    # Draw a small background rectangle
    # so the label is clearly visible
    (text_w, text_h), baseline = cv2.getTextSize(
        sofa_label,
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        3
    )

    rect_x1 = sofa_x1
    rect_y1 = max(
        0,
        sofa_y1 - text_h - baseline - 5
    )

    rect_x2 = min(
        width - 1,
        sofa_x1 + text_w + 8
    )

    rect_y2 = min(
        height - 1,
        sofa_y1 + 5
    )

    cv2.rectangle(
        output_image,
        (rect_x1, rect_y1),
        (rect_x2, rect_y2),
        (255, 255, 255),
        -1
    )

    cv2.putText(
        output_image,
        sofa_label,
        (sofa_x1 + 3, sofa_y1),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 0, 0),
        3,
        cv2.LINE_AA
    )


elif largest_contour is not None:

    # Fallback when 3seatersofa is NOT directly detected
    x, y, w, h = cv2.boundingRect(
        largest_contour
    )

    label = "3seatersofa"

    label_x = max(
        5,
        x
    )

    label_y = max(
        35,
        y
    )

    (text_w, text_h), baseline = cv2.getTextSize(
        label,
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        3
    )

    rect_x1 = label_x
    rect_y1 = max(
        0,
        label_y - text_h - baseline - 5
    )

    rect_x2 = min(
        width - 1,
        label_x + text_w + 8
    )

    rect_y2 = min(
        height - 1,
        label_y + 5
    )

    cv2.rectangle(
        output_image,
        (rect_x1, rect_y1),
        (rect_x2, rect_y2),
        (255, 255, 255),
        -1
    )

    cv2.putText(
        output_image,
        label,
        (label_x + 3, label_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 0, 0),
        3,
        cv2.LINE_AA
    )


# ============================================================
# SAVE OUTPUT IMAGE
# ============================================================

output_image_path = os.path.join(
    OUTPUT_DIR,
    os.path.basename(image_path)
)

cv2.imwrite(
    output_image_path,
    output_image
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n========================================")
print("PHASE 3 OUTPUT")
print("========================================")

print(
    json.dumps(
        output,
        indent=4
    )
)


print("\n========================================")
print("FILES CREATED")
print("========================================")

print("\nCorrected prediction image:")
print(output_image_path)

print("\nSofa segmentation mask:")
print(MASK_PATH)

print("\nJSON:")
print(JSON_PATH)


print("\n========================================")
print("ARMREST RESULT")
print("========================================")

for arm in final_armrests:

    print(
        f'{arm["final_name"]} '
        f'confidence={arm["confidence"]:.4f}'
    )