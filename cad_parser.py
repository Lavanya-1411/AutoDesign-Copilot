
import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES AND GEMINI API KEY
# ============================================================

load_dotenv()


def get_gemini_api_key():
    """
    Read the API key from:
    1. Local .env / environment variables
    2. Streamlit Cloud Secrets
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        return api_key

    try:
        import streamlit as st

        api_key = st.secrets.get("GEMINI_API_KEY")

        if api_key:
            return api_key

    except Exception:
        pass

    raise RuntimeError(
        "GEMINI_API_KEY not found. "
        "Add it to your local .env file or Streamlit Cloud Secrets."
    )


GEMINI_API_KEY = get_gemini_api_key()

client = genai.Client(api_key=GEMINI_API_KEY)

GEMINI_MODEL = "gemini-3.5-flash-lite"


# ============================================================
# 2. GEMINI REQUEST WITH RETRIES
# ============================================================

def generate_with_retry(prompt, max_attempts=4):

    for attempt in range(max_attempts):

        try:

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            if not response or not response.text:

                raise ValueError(
                    "Gemini returned an empty response."
                )

            return response.text.strip()

        except Exception as error:

            error_message = str(error).lower()

            temporary_errors = [
                "503",
                "unavailable",
                "429",
                "resource_exhausted",
                "500",
                "internal",
                "deadline",
                "timeout"
            ]

            is_temporary = any(
                message in error_message
                for message in temporary_errors
            )

            if not is_temporary:

                raise RuntimeError(
                    f"Gemini API error: {error}"
                ) from error

            if attempt == max_attempts - 1:

                raise RuntimeError(
                    "Gemini is temporarily unavailable or "
                    "the API quota has been reached. "
                    "Please wait and try again."
                ) from error

            wait_time = 3 * (2 ** attempt)

            print(
                f"Gemini temporarily unavailable. "
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)


# ============================================================
# 3. CAD REQUEST PARSER
# ============================================================

def parse_cad_request(user_request):

    if (
        not isinstance(user_request, str)
        or not user_request.strip()
    ):

        raise ValueError(
            "Please enter a valid CAD request."
        )

    prompt = f"""
You are an expert automotive mechanical CAD design planner.

Convert the user's natural-language CAD request into a
structured JSON specification for a generic FreeCAD engine.

USER REQUEST:
{user_request}

Return ONLY valid JSON. Do not use Markdown.

Use this exact structure:

{{
    "component": "component name",
    "units": "mm",
    "operations": [],
    "dimensions": {{}},
    "features": [],
    "material": null,
    "missing_parameters": [],
    "assumptions": []
}}

GENERAL RULES:

1. Identify the component and its geometry.
2. Extract dimensions explicitly provided by the user.
3. Convert all dimensions to millimeters.
4. Never invent unspecified dimensions.
5. Use positive values for physical sizes.
6. Coordinates may be positive, negative, or zero.
7. Store component dimensions in the dimensions object.
8. Store geometric features as objects in the features list.
9. List essential missing dimensions in missing_parameters.
10. List assumptions in assumptions.
11. Do not generate Python code or FreeCAD commands.
12. Use only the supported feature types listed below.
13. Use null for unknown values.
14. Do not create geometry when essential dimensions are missing.
15. Use feature positions as [x, y, z] coordinates in mm.
16. Use axis as [x, y, z] direction vectors where applicable.
17. Keep the JSON valid.

SUPPORTED BASE GEOMETRIES:

Cylinder:
{{
    "type": "cylinder",
    "name": "main_body",
    "diameter": 80,
    "height": 65,
    "axis": "Z"
}}

Box:
{{
    "type": "box",
    "length": 100,
    "width": 50,
    "thickness": 20
}}

Y-shaped control arm:
{{
    "type": "y_control_arm",
    "branch_width": 35,
    "thickness": 25
}}

SUPPORTED ADDITIVE FEATURES:

Boss:
{{
    "type": "boss",
    "name": "mounting_boss",
    "diameter": 35,
    "height": 25,
    "position": [25, 40, 0]
}}

Add cylinder:
{{
    "type": "add_cylinder",
    "diameter": 20,
    "height": 30,
    "position": [0, 0, 0]
}}

Add box:
{{
    "type": "add_box",
    "length": 30,
    "width": 20,
    "height": 10,
    "position": [0, 0, 0]
}}

SUPPORTED HOLE FEATURES:

Through hole:
{{
    "type": "through_hole",
    "name": "mounting_hole",
    "diameter": 18,
    "position": [25, 40, 0],
    "axis": [0, 0, 1]
}}

Wrist pin hole:
{{
    "type": "wrist_pin_hole",
    "diameter": 22,
    "axis": [1, 0, 0],
    "center_height": 32.5
}}

SUPPORTED CUT FEATURES:

Pocket:
{{
    "type": "pocket",
    "length": 180,
    "width": 45,
    "depth": 12,
    "position": [150, 0, 0]
}}

Hollow:
{{
    "type": "hollow",
    "wall_thickness": 5,
    "depth": 50
}}

Ring grooves:
{{
    "type": "ring_grooves",
    "count": 3,
    "depth": 0.5,
    "width": 2,
    "positions": [5, 8, 11]
}}

SUPPORTED EDGE FEATURES:

Fillet:
{{
    "type": "fillet",
    "radius": 5
}}

Chamfer:
{{
    "type": "chamfer",
    "distance": 2
}}

SUPPORTED OPERATIONS:

- cylinder
- box
- y_control_arm
- boss
- through_hole
- wrist_pin_hole
- pocket
- hollow
- ring_grooves
- add_cylinder
- add_box
- fillet
- chamfer
- fuse
- cut

IMPORTANT CONTROL ARM RULES:

For a Y-shaped control arm, store these dimensions when provided:

- chassis_mounting_hole_1_position: [x, y, z]
- chassis_mounting_hole_2_position: [x, y, z]
- ball_joint_hole_position: [x, y, z]
- branch_width
- thickness

Use boss features for mounting bosses and through_hole
features for mounting holes.

Do not assume the overall geometry if the mounting
positions are not supplied.

IMPORTANT:

- Do not invent dimensions or coordinates.
- Do not guess hole positions.
- Do not guess pocket positions.
- Do not claim a feature is fully defined when dimensions are missing.
- Keep component dimensions separate from feature dimensions.
- Return one JSON object only.
- No explanations outside JSON.

Return the JSON specification now.
"""

    # ========================================================
    # 4. SEND REQUEST TO GEMINI
    # ========================================================

    response_text = generate_with_retry(prompt)

    # ========================================================
    # 5. CLEAN GEMINI JSON RESPONSE
    # ========================================================

    response_text = response_text.strip()

    response_text = re.sub(
        r"^```(?:json)?\s*",
        "",
        response_text,
        flags=re.IGNORECASE
    )

    response_text = re.sub(
        r"\s*```$",
        "",
        response_text
    )

    response_text = response_text.strip()

    # ========================================================
    # 6. CONVERT JSON TO PYTHON DICTIONARY
    # ========================================================

    try:

        specification = json.loads(response_text)

    except json.JSONDecodeError as error:

        raise ValueError(
            "Gemini returned invalid JSON:\n"
            + response_text
        ) from error

    # ========================================================
    # 7. VALIDATE JSON STRUCTURE
    # ========================================================

    if not isinstance(specification, dict):

        raise ValueError(
            "CAD specification must be a JSON object."
        )

    required_keys = [
        "component",
        "units",
        "operations",
        "dimensions",
        "features",
        "material",
        "missing_parameters",
        "assumptions"
    ]

    for key in required_keys:

        if key not in specification:

            raise ValueError(
                f"Missing required JSON field: {key}"
            )

    if not isinstance(specification["component"], str):

        raise ValueError(
            "Component must be a string."
        )

    if specification["units"] != "mm":

        raise ValueError(
            "CAD units must be mm."
        )

    if not isinstance(specification["operations"], list):

        raise ValueError(
            "Operations must be a list."
        )

    if not isinstance(specification["dimensions"], dict):

        raise ValueError(
            "Dimensions must be an object."
        )

    if not isinstance(specification["features"], list):

        raise ValueError(
            "Features must be a list."
        )

    if not isinstance(specification["missing_parameters"], list):

        raise ValueError(
            "Missing parameters must be a list."
        )

    if not isinstance(specification["assumptions"], list):

        raise ValueError(
            "Assumptions must be a list."
        )

    for index, feature in enumerate(specification["features"]):

        if not isinstance(feature, dict):

            raise ValueError(
                f"Feature {index + 1} must be an object."
            )

        if "type" not in feature:

            raise ValueError(
                f"Feature {index + 1} has no type."
            )

    # ========================================================
    # 8. CHECK MISSING PARAMETERS
    # ========================================================

    if specification["missing_parameters"]:

        missing = ", ".join(
            str(item)
            for item in specification["missing_parameters"]
        )

        raise ValueError(
            "The CAD request is missing essential parameters: "
            + missing
        )

    # ========================================================
    # 9. RETURN FINAL SPECIFICATION
    # ========================================================

    return specification
