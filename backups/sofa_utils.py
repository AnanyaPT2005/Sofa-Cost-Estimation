import numpy as np

def extract_mask_features(mask, img_w, img_h):
    x, y, w, h = mask["bbox"]

    cx = x + w/2
    cy = y + h/2

    return {
        "mask": mask,
        "area": mask["area"],
        "bbox": (x, y, w, h),

        "cx": cx,
        "cy": cy,

        "rel_x": cx / img_w,
        "rel_y": cy / img_h,

        "width": w,
        "height": h,
        "aspect": w / max(h, 1)
    }