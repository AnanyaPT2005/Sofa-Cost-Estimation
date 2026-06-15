import cv2
import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

IMAGE_PATH = "images/sofa2.jpg"
MASKS_PATH = "outputs/masks.pkl"
OUTPUT_PATH = "outputs/auto_labelled.png"

# --------------------------------------------------
# LOAD IMAGE + MASKS
# --------------------------------------------------

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise FileNotFoundError(f"Could not load {IMAGE_PATH}")

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

img_h, img_w = image.shape[:2]
img_area = img_h * img_w

with open(MASKS_PATH, "rb") as f:
    masks = pickle.load(f)

print(f"Loaded {len(masks)} masks")

# --------------------------------------------------
# EXTRACT FEATURES
# --------------------------------------------------

features = []

for mask in masks:

    x, y, w, h = mask["bbox"]

    cx = x + w / 2
    cy = y + h / 2

    aspect_ratio = w / max(h, 1)

    features.append({
        "mask": mask,
        "area": mask["area"],
        "area_pct": mask["area"] / img_area * 100,
        "bbox": (x, y, w, h),

        "cx": cx,
        "cy": cy,

        "rel_x": cx / img_w,
        "rel_y": cy / img_h,

        "width": w,
        "height": h,

        "aspect_ratio": aspect_ratio,
        "bottom": y + h,
        "right": x + w
    })

# --------------------------------------------------
# SORT LARGEST FIRST
# --------------------------------------------------

features.sort(
    key=lambda x: x["area"],
    reverse=True
)

print("\nDetected Segments")
print("-" * 70)

for idx, f in enumerate(features):

    print(
        f"ID {idx:2d} | "
        f"{f['area_pct']:6.2f}% | "
        f"center=({f['rel_x']:.2f}, {f['rel_y']:.2f}) | "
        f"aspect={f['aspect_ratio']:.2f}"
    )

# --------------------------------------------------
# REMOVE OBVIOUS BACKGROUND
# --------------------------------------------------

sofa_parts = []

for f in features:

    # ignore huge wall/floor masks

    if f["area_pct"] > 15:
        continue

    sofa_parts.append(f)

print(f"\nRemaining sofa segments: {len(sofa_parts)}")

# --------------------------------------------------
# LABEL ASSIGNMENT HELPERS
# --------------------------------------------------

labels = {}
used_masks = set()

def available_masks():
    return [
        m for m in sofa_parts
        if id(m) not in used_masks
    ]

def assign_label(name, score_fn):

    candidates = available_masks()

    if not candidates:
        return

    best = max(
        candidates,
        key=score_fn
    )

    labels[name] = best
    used_masks.add(id(best))

# --------------------------------------------------
# SEAT
# --------------------------------------------------

def seat_score(f):

    center_score = 1 - abs(f["rel_x"] - 0.5)

    vertical_score = 1 - abs(f["rel_y"] - 0.60)

    area_score = min(
        f["area_pct"] / 8,
        1
    )

    width_score = min(
        f["aspect_ratio"] / 3,
        1
    )

    return (
        center_score * 5 +
        vertical_score * 5 +
        area_score * 3 +
        width_score * 2
    )

assign_label("seat", seat_score)

# --------------------------------------------------
# LEFT ARMREST
# --------------------------------------------------

def left_arm_score(f):

    return (
        (1 - f["rel_x"]) * 6 +
        (1 - abs(f["rel_y"] - 0.55)) * 2
    )

assign_label("left_armrest", left_arm_score)

# --------------------------------------------------
# RIGHT ARMREST
# --------------------------------------------------

def right_arm_score(f):

    return (
        f["rel_x"] * 6 +
        (1 - abs(f["rel_y"] - 0.55)) * 2
    )

assign_label("right_armrest", right_arm_score)

# --------------------------------------------------
# BACKREST LEFT
# --------------------------------------------------

def backrest_left_score(f):

    return (
        (1 - f["rel_y"]) * 5 +
        (1 - abs(f["rel_x"] - 0.35)) * 3 +
        min(f["area_pct"] / 8, 1) * 2
    )

assign_label(
    "backrest_left",
    backrest_left_score
)

# --------------------------------------------------
# BACKREST RIGHT
# --------------------------------------------------

def backrest_right_score(f):

    return (
        (1 - f["rel_y"]) * 5 +
        (1 - abs(f["rel_x"] - 0.65)) * 3 +
        min(f["area_pct"] / 8, 1) * 2
    )

assign_label(
    "backrest_right",
    backrest_right_score
)

# --------------------------------------------------
# LEGS
# --------------------------------------------------

remaining = available_masks()

leg_candidates = [
    m for m in remaining
    if m["rel_y"] > 0.70
]

leg_candidates.sort(
    key=lambda x: x["rel_x"]
)

if len(leg_candidates) >= 1:
    labels["leg_left"] = leg_candidates[0]

if len(leg_candidates) >= 2:
    labels["leg_right"] = leg_candidates[-1]

# --------------------------------------------------
# VISUALISE SEGMENTS + LABELS
# --------------------------------------------------

overlay = image_rgb.copy()

np.random.seed(42)

for idx, f in enumerate(features):

    colour = np.random.randint(
        50,
        255,
        3
    )

    overlay[
        f["mask"]["segmentation"]
    ] = colour

result = cv2.addWeighted(
    image_rgb,
    0.4,
    overlay,
    0.6,
    0
)

fig, ax = plt.subplots(
    figsize=(14, 10)
)

ax.imshow(result)

# --------------------------------------------------
# DRAW SEGMENT IDS
# --------------------------------------------------

for idx, f in enumerate(features):

    x, y, w, h = f["bbox"]

    ax.text(
        x + w / 2,
        y + h / 2,
        f"ID {idx}",
        color="white",
        fontsize=9,
        ha="center",
        va="center",
        bbox=dict(
            facecolor="black",
            alpha=0.8
        )
    )

# --------------------------------------------------
# DRAW LABELS
# --------------------------------------------------

for label, part in labels.items():

    x, y, w, h = part["bbox"]

    rect = patches.Rectangle(
        (x, y),
        w,
        h,
        linewidth=2,
        edgecolor="white",
        facecolor="none"
    )

    ax.add_patch(rect)

    ax.text(
        x,
        y - 8,
        label,
        color="yellow",
        fontsize=10,
        bbox=dict(
            facecolor="black",
            alpha=0.9
        )
    )

ax.set_title(
    "SAM Segments + Auto Labels"
)

ax.axis("off")

plt.tight_layout()

plt.savefig(
    OUTPUT_PATH,
    dpi=150
)

print(f"\nSaved image to {OUTPUT_PATH}")

plt.show()

# --------------------------------------------------
# FINAL LABELS
# --------------------------------------------------

print("\nFinal Labels")
print("-" * 40)

for label, part in labels.items():

    print(
        f"{label:15s} "
        f"ID={features.index(part):2d} "
        f"Area={part['area_pct']:.2f}%"
    )