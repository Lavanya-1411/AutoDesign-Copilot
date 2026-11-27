
import json
import os
import math


# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CAD_DIR = os.path.join(BASE_DIR, "cad")

SPEC_FILE = os.path.join(
    CAD_DIR,
    "current_spec.json"
)

os.makedirs(CAD_DIR, exist_ok=True)


# ==========================================
# 2. COORDINATE DETECTION
# ==========================================

def is_coordinate(name):

    name = str(name).lower()

    coordinate_keywords = (
        "position",
        "coordinate",
        "centre",
        "center",
        "location",
        "origin",
        "point",
        "offset",
        "axis",
        "direction",
        "vector",
    )

    return (
        any(word in name for word in coordinate_keywords)
        or name.endswith(("_x", "_y", "_z"))
    )


# ==========================================
# 3. NUMERIC VALIDATION
# ==========================================

def validate_numeric_value(value, key, coordinate=False):

    if value is None:
        return

    if isinstance(value, bool):
        raise ValueError(
            f"Invalid numeric value for: {key}"
        )

    if isinstance(value, (int, float)):

        if not math.isfinite(value):
            raise ValueError(
                f"Invalid non-finite value: {key}"
            )

        if not coordinate and value <= 0:
            raise ValueError(
                f"Dimension must be positive: {key}"
            )

        return

    if isinstance(value, list):

        for item in value:

            validate_numeric_value(
                item,
                key,
                coordinate=True
            )

        return

    if isinstance(value, dict):

        for sub_key, sub_value in value.items():

            validate_numeric_value(
                sub_value,
                sub_key,
                coordinate=is_coordinate(sub_key)
            )

        return

    raise ValueError(
        f"Invalid dimension value for {key}: {value}"
    )


# ==========================================
# 4. DIMENSION VALIDATION
# ==========================================

def validate_dimensions(dimensions):

    if not isinstance(dimensions, dict):
        raise ValueError(
            "Dimensions must be a dictionary."
        )

    for key, value in dimensions.items():

        validate_numeric_value(
            value,
            key,
            coordinate=is_coordinate(key)
        )


# ==========================================
# 5. FEATURE VALIDATION
# ==========================================

def validate_features(features):

    if not isinstance(features, list):
        raise ValueError(
            "Features must be a list."
        )

    for index, feature in enumerate(features):

        if not isinstance(feature, dict):
            raise ValueError(
                f"Feature {index + 1} must be an object."
            )

        if "type" not in feature:
            raise ValueError(
                f"Feature {index + 1} is missing its type."
            )

        for key, value in feature.items():

            if key == "type" or key == "name":
                continue

            if isinstance(value, (int, float, list, dict)):

                validate_numeric_value(
                    value,
                    key,
                    coordinate=is_coordinate(key)
                )


# ==========================================
# 6. MAIN SPECIFICATION VALIDATION
# ==========================================

def validate_spec(spec):

    if not isinstance(spec, dict):
        raise ValueError(
            "CAD specification must be a dictionary."
        )

    required_keys = [
        "component",
        "units",
        "operations",
        "dimensions",
        "features",
        "material",
        "missing_parameters",
        "assumptions",
    ]

    for key in required_keys:

        if key not in spec:
            raise ValueError(
                f"Missing required field: {key}"
            )

    if not isinstance(spec["component"], str):
        raise ValueError(
            "Component name must be a string."
        )

    if not spec["component"].strip():
        raise ValueError(
            "Component name cannot be empty."
        )

    if spec["units"] != "mm":
        raise ValueError(
            "Only millimeter (mm) units are supported."
        )

    if not isinstance(spec["operations"], list):
        raise ValueError(
            "Operations must be a list."
        )

    if not isinstance(spec["missing_parameters"], list):
        raise ValueError(
            "Missing parameters must be a list."
        )

    if not isinstance(spec["assumptions"], list):
        raise ValueError(
            "Assumptions must be a list."
        )

    # Validate dimensions
    validate_dimensions(
        spec["dimensions"]
    )

    # Validate features
    validate_features(
        spec["features"]
    )

    # Check missing parameters
    if spec["missing_parameters"]:

        missing = ", ".join(
            str(item)
            for item in spec["missing_parameters"]
        )

        raise ValueError(
            f"Missing essential CAD parameters: {missing}"
        )

    return True


# ==========================================
# 7. SAVE CAD SPECIFICATION
# ==========================================

def save_spec(spec):

    try:

        with open(
            SPEC_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                spec,
                file,
                indent=4,
                ensure_ascii=False
            )

    except Exception as error:

        raise RuntimeError(
            f"Could not save CAD specification: {error}"
        ) from error


# ==========================================
# 8. GENERATE CAD SPECIFICATION
# ==========================================

def generate_cad(spec):

    # Validate specification
    validate_spec(spec)

    # Save JSON for FreeCAD macro
    save_spec(spec)

    return (
        "CAD specification validated and saved successfully."
    )


# ==========================================
# 9. TEST
# ==========================================

if __name__ == "__main__":

    test_spec = {
        "component": "Y-shaped control arm",
        "units": "mm",
        "operations": [
            "y_control_arm",
            "boss",
            "through_hole",
            "pocket",
            "fillet"
        ],
        "dimensions": {
            "branch_width": 35,
            "thickness": 25,
            "pocket_centre": [150, 0, 0],
            "chassis_mounting_hole_1_position": [25, -40, 0],
            "chassis_mounting_hole_2_position": [25, 40, 0],
            "ball_joint_hole_position": [325, 0, 0]
        },
        "features": [],
        "material": "Aluminium 6061",
        "missing_parameters": [],
        "assumptions": []
    }

    try:

        result = generate_cad(test_spec)

        print(result)
        print(f"Saved specification: {SPEC_FILE}")

    except Exception as error:

        print(f"CAD validation error: {error}")
