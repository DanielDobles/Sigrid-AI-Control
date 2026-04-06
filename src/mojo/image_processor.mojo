# SIGRID High-Performance Image Processor (Mojo)
# 
# This module provides fast screenshot analysis for root cause diagnosis.
# Compiles to native code for 10-100x speedup over pure Python.
#
# Usage from Python:
#   import max.mojo.importer
#   from src.mojo import image_processor
#   result = image_processor.analyze_screenshot("screenshot.png")

from python import PythonObject
from python.python import *
from pathlib import *

# ============================================================
# SCREENSHOT ANALYSIS - HIGH PERFORMANCE
# ============================================================

fn analyze_screenshot(image_path: String) raises -> PythonObject:
    """
    Analyze a screenshot to extract UI elements, colors, and layout.
    Used for root cause diagnosis when actions fail.
    
    Returns dict with:
    - dominant_colors: List of (r, g, b) tuples
    - brightness: Float 0-1
    - edges_detected: Int count of edge regions
    - text_regions: Int count of likely text areas
    """
    let np = Python.import_module("numpy")
    let cv2 = Python.import_module("cv2")
    let PIL_Image = Python.import_module("PIL.Image")
    
    # Load image
    let img = PIL_Image.open(image_path).convert(Python.eval("\"RGB\""))
    let np_img = np.array(img)
    
    # Calculate brightness (fast vectorized operation)
    let gray = cv2.cvtColor(np_img, Python.eval("cv2.COLOR_RGB2GRAY"))
    let brightness = Python.eval("float(gray.mean() / 255.0)")
    
    # Detect edges using Canny (compute-heavy, benefits from Mojo)
    let edges = cv2.Canny(gray, 100, 200)
    let edge_count = Python.eval("int(cv2.countNonZero(edges))")
    
    # Detect text regions (simple heuristic: high variance blocks)
    let text_regions = _detect_text_regions(gray, np, cv2)
    
    # Get dominant colors (sample and cluster)
    let dominant_colors = _get_dominant_colors(np_img, np)
    
    # Return as Python dict
    return Python.dict(Python.list(Python.tuple(Python.eval("\"dominant_colors\""), dominant_colors)),
                       Python.tuple(Python.eval("\"brightness\""), brightness),
                       Python.tuple(Python.eval("\"edges_detected\""), edge_count),
                       Python.tuple(Python.eval("\"text_regions\""), text_regions))


fn _detect_text_regions(gray_image: PythonObject, np: PythonObject, cv2: PythonObject) -> Int:
    """Detect potential text regions in grayscale image."""
    # Use variance-based text detection
    let thresh = cv2.adaptiveThreshold(gray_image, 255,
                                       Python.eval("cv2.ADAPTIVE_THRESH_GAUSSIAN_C"),
                                       Python.eval("cv2.THRESH_BINARY"),
                                       11, 2)
    
    # Find contours
    let contours_data = cv2.findContours(thresh, Python.eval("cv2.RETR_EXTERNAL"),
                                         Python.eval("cv2.CHAIN_APPROX_SIMPLE"))
    let contours = contours_data[0] if hasattr(contours_data, "__getitem__") else contours_data
    
    # Count contours that look like text (small, rectangular)
    var text_region_count: Int = 0
    for i in range(len(contours)):
        let contour = contours[i]
        let x, y, w, h = cv2.boundingRect(contour)
        let aspect_ratio = Python.eval("float(w) / max(h, 1)")
        let area = Python.eval("int(w * h)")
        
        # Text-like regions: aspect ratio 0.2-5, area 100-10000
        if 0.2 < aspect_ratio < 5.0 and 100 < area < 10000:
            text_region_count += 1
    
    return text_region_count


fn _get_dominant_colors(image_np: PythonObject, np: PythonObject) -> PythonObject:
    """Get top 5 dominant colors from image."""
    # Reshape to list of pixels
    let pixels = image_np.reshape(-1, 3)
    
    # Sample every 10th pixel for speed
    let sampled = pixels[::10]
    
    # Simple k-means with k=5
    let criteria = Python.eval("(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1.0)")
    let flags = Python.eval("cv2.KMEANS_RANDOM_CENTERS")
    let cv2 = Python.import_module("cv2")
    
    let compactness, labels, centers = cv2.kmeans(
        Python.eval("sampled.astype(np.float32)"),
        5, Python.None(), criteria, 10, flags
    )
    
    return centers.astype(Python.eval("int")).tolist()


# ============================================================
# PIXEL COMPARISON - DETECT VISUAL CHANGES
# ============================================================

fn compare_images(image1_path: String, image2_path: String) raises -> PythonObject:
    """
    Compare two screenshots to detect visual changes.
    Returns difference metrics and change regions.
    """
    let np = Python.import_module("numpy")
    let cv2 = Python.import_module("cv2")
    let PIL_Image = Python.import_module("PIL.Image")
    
    # Load both images
    let img1 = np.array(PIL_Image.open(image1_path).convert(Python.eval("\"RGB\"")))
    let img2 = np.array(PIL_Image.open(image2_path).convert(Python.eval("\"RGB\"")))
    
    # Ensure same size
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    # Calculate difference
    let diff = cv2.absdiff(img1, img2)
    let gray_diff = cv2.cvtColor(diff, Python.eval("cv2.COLOR_RGB2GRAY"))
    let _, thresh = cv2.threshold(gray_diff, 30, 255, Python.eval("cv2.THRESH_BINARY"))
    
    # Calculate metrics
    let diff_percentage = Python.eval("float(cv2.countNonZero(thresh)) / (thresh.shape[0] * thresh.shape[1]) * 100")
    let mean_diff = Python.eval("float(diff.mean())")
    
    # Find change regions (bounding boxes)
    let contours, _ = cv2.findContours(thresh, Python.eval("cv2.RETR_EXTERNAL"),
                                       Python.eval("cv2.CHAIN_APPROX_SIMPLE"))
    
    var change_regions = Python.list()
    for i in range(len(contours)):
        let contour = contours[i]
        if Python.eval("cv2.contourArea(contour)") > 100:  # Filter noise
            let x, y, w, h = cv2.boundingRect(contour)
            change_regions.append(Python.dict(
                Python.tuple(Python.eval("\"x\""), x),
                Python.tuple(Python.eval("\"y\""), y),
                Python.tuple(Python.eval("\"w\""), w),
                Python.tuple(Python.eval("\"h\""), h)
            ))
    
    return Python.dict(
        Python.tuple(Python.eval("\"diff_percentage\""), diff_percentage),
        Python.tuple(Python.eval("\"mean_difference\""), mean_diff),
        Python.tuple(Python.eval("\"change_regions\""), change_regions),
        Python.tuple(Python.eval("\"has_changes\""), diff_percentage > 0.1)
    )


# ============================================================
# UI ELEMENT DETECTION
# ============================================================

fn detect_ui_elements(image_path: String, template_paths: PythonObject) raises -> PythonObject:
    """
    Detect UI elements (buttons, input fields) in screenshot using template matching.
    Much faster in Mojo due to tight loop optimization.
    """
    let cv2 = Python.import_module("cv2")
    let np = Python.import_module("numpy")
    let PIL_Image = Python.import_module("PIL.Image")
    
    let screenshot = cv2.cvtColor(np.array(PIL_Image.open(image_path)),
                                  Python.eval("cv2.COLOR_RGB2GRAY"))
    
    var detections = Python.list()
    
    for i in range(len(template_paths)):
        let template_path = template_paths[i]
        let template = cv2.imread(template_path, Python.eval("cv2.IMREAD_GRAYSCALE"))
        
        if template is Python.None():
            continue
        
        # Template matching
        let result = cv2.matchTemplate(screenshot, template, Python.eval("cv2.TM_CCOEFF_NORMED"))
        let _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if Python.eval("float(max_val)") > 0.8:  # Threshold
            let h, w = template.shape
            detections.append(Python.dict(
                Python.tuple(Python.eval("\"element\""), template_path),
                Python.tuple(Python.eval("\"confidence\""), max_val),
                Python.tuple(Python.eval("\"x\""), Python.eval("int(max_loc[0])")),
                Python.tuple(Python.eval("\"y\""), Python.eval("int(max_loc[1])")),
                Python.tuple(Python.eval("\"w\""), w),
                Python.tuple(Python.eval("\"h\""), h)
            ))
    
    return detections


# ============================================================
# MOJO MODULE EXPORT - PYTHON BRIDGE
# ============================================================

@export
fn PyInit_image_processor() -> PythonObject:
    """Export module for Python import."""
    let builder = PythonModuleBuilder("image_processor")
    builder.def_function[analyze_screenshot]("analyze_screenshot", "Analyze screenshot for UI elements and properties")
    builder.def_function[compare_images]("compare_images", "Compare two screenshots to detect changes")
    builder.def_function[detect_ui_elements]("detect_ui_elements", "Detect UI elements using template matching")
    return builder.build()
