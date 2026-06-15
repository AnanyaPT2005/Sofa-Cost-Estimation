# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

# # ---- CONFIG ----
# IMAGE_PATH = "images/sofa2.jpg"   # put your sofa image here
# MODEL_PATH = "models/sam_vit_b_01ec64.pth"
# OUTPUT_PATH = "outputs/segmented.png"
# # ----------------

# def show_masks(image, masks):
#     """Draw coloured masks over image"""
#     overlay = image.copy()
#     colours = [
#         [255, 0, 0],    # red
#         [0, 255, 0],    # green
#         [0, 0, 255],    # blue
#         [255, 165, 0],  # orange
#         [128, 0, 128],  # purple
#         [0, 255, 255],  # cyan
#     ]
#     for i, mask in enumerate(masks):
#         colour = colours[i % len(colours)]
#         overlay[mask["segmentation"]] = colour

#     blended = cv2.addWeighted(image, 0.4, overlay, 0.6, 0)
#     return blended

# def get_bounding_boxes(masks):
#     """Extract bounding boxes from masks"""
#     boxes = []
#     for mask in masks:
#         # bbox format from SAM: [x, y, width, height]
#         x, y, w, h = mask["bbox"]
#         area = mask["area"]
#         boxes.append({
#             "bbox": (int(x), int(y), int(w), int(h)),
#             "area": area
#         })
#     return boxes

# def compute_ratios(boxes, image_shape):
#     """Compute what % of image area each segment takes"""
#     img_area = image_shape[0] * image_shape[1]
#     ratios = []
#     for box in boxes:
#         ratio = round(box["area"] / img_area * 100, 2)
#         ratios.append({
#             "bbox": box["bbox"],
#             "area_px": box["area"],
#             "area_percent": ratio
#         })
#     # sort largest to smallest
#     ratios.sort(key=lambda x: x["area_percent"], reverse=True)
#     return ratios

# def main():
#     # load image
#     print("Loading image...")
#     image = cv2.imread(IMAGE_PATH)
#     if image is None:
#         print(f"ERROR: Could not load image at {IMAGE_PATH}")
#         return
#     image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     print(f"Image size: {image.shape[1]}x{image.shape[0]} px")

#     # load SAM model
#     print("Loading SAM model (this takes ~30 seconds)...")
#     sam = sam_model_registry["vit_b"](checkpoint=MODEL_PATH)
#     sam.eval()
#     print("Model loaded.")

#     # run segmentation
#     print("Running segmentation...")
#     mask_generator = SamAutomaticMaskGenerator(
#         model=sam,
#         points_per_side=16,          # lower = faster, fewer segments
#         pred_iou_thresh=0.88,        # confidence threshold
#         stability_score_thresh=0.95,
#         min_mask_region_area=5000    # ignore tiny segments
#     )
#     masks = mask_generator.generate(image_rgb)
#     print(f"Found {len(masks)} segments")

#     # draw masks on image
#     result = show_masks(image_rgb, masks)

#     # compute ratios
#     boxes = get_bounding_boxes(masks)
#     ratios = compute_ratios(boxes, image.shape)

#     # print results
#     print("\n--- Segment Ratios (largest first) ---")
#     for i, r in enumerate(ratios):
#         print(f"Segment {i+1}: {r['area_percent']}% of image | bbox: {r['bbox']}")

#     # draw bounding boxes on result
#     fig, axes = plt.subplots(1, 2, figsize=(14, 6))
#     axes[0].imshow(image_rgb)
#     axes[0].set_title("Original")
#     axes[0].axis("off")

#     axes[1].imshow(result)
#     axes[1].set_title(f"Segmented — {len(masks)} regions found")
#     axes[1].axis("off")

#     # draw bboxes
#     for r in ratios:
#         x, y, w, h = r["bbox"]
#         rect = patches.Rectangle((x, y), w, h,
#                                   linewidth=1, edgecolor='white', facecolor='none')
#         axes[1].add_patch(rect)
#         axes[1].text(x, y - 5, f"{r['area_percent']}%",
#                     color='white', fontsize=7)

#     plt.tight_layout()
#     plt.savefig(OUTPUT_PATH, dpi=150)
#     print(f"\nSaved output to {OUTPUT_PATH}")
#     plt.show()

# if __name__ == "__main__":
#     main()

import cv2
import numpy as np
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import pickle

IMAGE_PATH = "images/sofa2.jpg"
MODEL_PATH = "models/sam_vit_b_01ec64.pth"
MASKS_SAVE_PATH = "outputs/masks.pkl"

image = cv2.imread(IMAGE_PATH)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

print("Loading model...")
sam = sam_model_registry["vit_b"](checkpoint=MODEL_PATH)
mask_generator = SamAutomaticMaskGenerator(
    model=sam,
    points_per_side=16,
    pred_iou_thresh=0.88,
    stability_score_thresh=0.95,
    min_mask_region_area=5000
)

print("Segmenting (this runs only once)...")
masks = mask_generator.generate(image_rgb)
print(f"Found {len(masks)} segments")

# save masks to disk
with open(MASKS_SAVE_PATH, "wb") as f:
    pickle.dump(masks, f)

print(f"Masks saved to {MASKS_SAVE_PATH}")