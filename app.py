
import json
import os
import subprocess
from pathlib import Path

import streamlit as st

from cad_parser import parse_cad_request
from cad_engine import validate_spec, save_spec


# ==================================================
# 1. PATH CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parent

CAD_DIR = ROOT / "cad"
OUTPUT_DIR = ROOT / "output"

SPEC_FILE = CAD_DIR / "current_spec.json"
MACRO_FILE = CAD_DIR / "universal_cad.FCMacro"

FREECAD_CMD = Path(
    r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"
)

CAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. STREAMLIT CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AutoDesign Copilot",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 AutoDesign Copilot")

st.subheader(
    "AI-powered CAD generation for automotive components"
)

st.markdown(
    """
    Describe your automotive component in natural language.

    AutoDesign Copilot converts your requirements into a
    structured engineering specification and generates
    a 3D CAD model using FreeCAD.
    """
)


# ==================================================
# 3. SESSION STATE INITIALIZATION
# ==================================================

if "cad_spec" not in st.session_state:
    st.session_state["cad_spec"] = None

if "cad_generated" not in st.session_state:
    st.session_state["cad_generated"] = False

if "freecad_log" not in st.session_state:
    st.session_state["freecad_log"] = ""

if "generated_files" not in st.session_state:
    st.session_state["generated_files"] = []

if "build_component" not in st.session_state:
    st.session_state["build_component"] = None


# ==================================================
# 4. SIDEBAR
# ==================================================

with st.sidebar:

    st.header("Project Information")

    st.write("**Application:** AutoDesign Copilot")
    st.write("**AI Engine:** Gemini")
    st.write("**CAD Engine:** FreeCAD 1.1")

    st.divider()

    st.write("### Supported Outputs")

    st.write("- FreeCAD (.FCStd)")
    st.write("- STEP (.step)")
    st.write("- STL (.stl)")

    st.divider()

    st.write("### Supported Components")

    st.write("- Pistons")
    st.write("- Flywheels")
    st.write("- Suspension components")
    st.write("- Automotive brackets")
    st.write("- Other supported CAD geometries")

    st.divider()

    st.caption("Conceptual CAD generation prototype")


# ==================================================
# 5. USER INPUT
# ==================================================

st.header("1. Describe Your Component")

prompt = st.text_area(
    "Enter your CAD requirements",
    height=180,
    placeholder=(
        "Example: Design an automotive piston with "
        "86 mm outer diameter, 75 mm total height, "
        "ring grooves, piston pin bore and skirt."
    )
)

generate_button = st.button(
    "Generate CAD Specification",
    type="primary",
    use_container_width=True
)


# ==================================================
# 6. HELPER FUNCTIONS
# ==================================================

def get_cad_files():
    """Return available CAD output files."""

    supported_extensions = {
        ".fcstd",
        ".step",
        ".stp",
        ".stl"
    }

    return sorted(
        [
            file_path
            for file_path in OUTPUT_DIR.iterdir()
            if file_path.is_file()
            and file_path.suffix.lower() in supported_extensions
        ],
        key=lambda p: p.name.lower()
    )


def clear_previous_outputs():
    """Remove old CAD files before a new build."""

    for file_path in get_cad_files():

        try:
            file_path.unlink()

        except OSError as error:
            raise RuntimeError(
                f"Could not remove old CAD file "
                f"{file_path.name}: {error}"
            )


def save_current_specification(spec):
    """Save the latest specification for FreeCAD."""

    SPEC_FILE.write_text(
        json.dumps(spec, indent=4),
        encoding="utf-8"
    )


def display_downloads(files):
    """Display download buttons for generated CAD files."""

    if not files:
        st.warning("No CAD files are available.")
        return

    st.header("4. Download CAD Files")

    cols = st.columns(3)

    for index, file_path in enumerate(files):

        with cols[index % 3]:

            with open(file_path, "rb") as file:
                file_data = file.read()

            st.download_button(
                label=f"Download {file_path.suffix.upper()}",
                data=file_data,
                file_name=file_path.name,
                key=f"download_{file_path.name}",
                use_container_width=True
            )


# ==================================================
# 7. GENERATE CAD SPECIFICATION
# ==================================================

if generate_button:

    if not prompt.strip():

        st.warning(
            "Please enter a component description."
        )

    else:

        try:

            with st.spinner(
                "AI is analysing your requirements..."
            ):

                # Generate a fresh specification
                spec = parse_cad_request(prompt)

                if not isinstance(spec, dict):
                    raise ValueError(
                        "AI did not return a valid JSON specification."
                    )

                # Validate specification
                validate_spec(spec)

                # Save latest specification
                save_spec(spec)

                save_current_specification(spec)

                # Reset previous CAD generation state
                st.session_state["cad_spec"] = spec

                st.session_state["cad_generated"] = False

                st.session_state["freecad_log"] = ""

                st.session_state["generated_files"] = []

                st.session_state["build_component"] = None

            component_name = spec.get(
                "component",
                "Unknown component"
            )

            st.success(
                f"CAD specification generated for: {component_name}"
            )

        except Exception as error:

            st.session_state["cad_generated"] = False

            st.error(
                f"Specification generation failed: {error}"
            )


# ==================================================
# 8. DISPLAY SPECIFICATION
# ==================================================

spec = st.session_state.get("cad_spec")

if spec:

    st.divider()

    st.header("2. Review CAD Specification")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Component**")

        st.success(
            str(spec.get("component", "Unknown"))
        )

    with col2:

        st.write("**Material**")

        st.info(
            str(spec.get("material", "Not specified"))
        )

    with st.expander(
        "View Complete JSON Specification"
    ):

        st.json(spec)

    st.divider()

    # ==================================================
    # 9. BUILD 3D CAD MODEL
    # ==================================================

    st.header("3. Generate 3D CAD Model")

    build_button = st.button(
        "Build 3D Model in FreeCAD",
        type="primary",
        use_container_width=True
    )

    if build_button:

        if not spec:

            st.error(
                "Generate a CAD specification first."
            )

        elif not FREECAD_CMD.exists():

            st.error(
                f"FreeCAD executable not found: {FREECAD_CMD}"
            )

        elif not MACRO_FILE.exists():

            st.error(
                f"FreeCAD macro not found: {MACRO_FILE}"
            )

        else:

            try:

                with st.spinner(
                    "FreeCAD is building your component..."
                ):

                    # Get the latest specification
                    current_spec = st.session_state["cad_spec"]

                    component_name = str(
                        current_spec.get(
                            "component",
                            "unknown"
                        )
                    )

                    # Make sure the latest JSON is saved
                    save_current_specification(
                        current_spec
                    )

                    # Remove previous component files
                    clear_previous_outputs()

                    # Prepare environment variables
                    env = os.environ.copy()

                    env["AUTODESIGN_SPEC_FILE"] = str(
                        SPEC_FILE.resolve()
                    )

                    env["AUTODESIGN_OUTPUT_DIR"] = str(
                        OUTPUT_DIR.resolve()
                    )

                    env["AUTODESIGN_COMPONENT"] = component_name

                    # Execute FreeCAD macro
                    result = subprocess.run(
                        [
                            str(FREECAD_CMD),
                            str(MACRO_FILE)
                        ],
                        cwd=str(ROOT),
                        capture_output=True,
                        text=True,
                        timeout=300,
                        env=env
                    )

                    # Save FreeCAD logs
                    log = (
                        (result.stdout or "")
                        + "\n"
                        + (result.stderr or "")
                    )

                    st.session_state["freecad_log"] = log

                    # Find files generated by this build
                    generated_files = get_cad_files()

                    if (
                        result.returncode == 0
                        and generated_files
                    ):

                        st.session_state["cad_generated"] = True

                        st.session_state["generated_files"] = [
                            str(file_path)
                            for file_path in generated_files
                        ]

                        st.session_state["build_component"] = (
                            component_name
                        )

                        st.success(
                            f"Successfully generated CAD model "
                            f"for {component_name}!"
                        )

                    else:

                        st.session_state["cad_generated"] = False

                        st.session_state["generated_files"] = []

                        st.error(
                            "CAD generation failed or no output "
                            "files were created. Check the FreeCAD log."
                        )

            except subprocess.TimeoutExpired:

                st.session_state["cad_generated"] = False

                st.error(
                    "FreeCAD generation timed out after 300 seconds."
                )

            except Exception as error:

                st.session_state["cad_generated"] = False

                st.error(
                    f"FreeCAD generation error: {error}"
                )


    # ==================================================
    # 10. DOWNLOAD GENERATED CAD FILES
    # ==================================================

    if st.session_state.get("cad_generated"):

        st.divider()

        st.success(
            "Latest CAD generation completed."
        )

        st.write(
            f"**Generated component:** "
            f"{st.session_state.get('build_component')}"
        )

        generated_files = [
            Path(file_path)
            for file_path in st.session_state.get(
                "generated_files",
                []
            )
            if Path(file_path).exists()
        ]

        display_downloads(generated_files)


    # ==================================================
    # 11. FREECAD LOG
    # ==================================================

    if st.session_state.get("freecad_log"):

        with st.expander(
            "View FreeCAD Generation Log"
        ):

            st.code(
                st.session_state["freecad_log"],
                language="text"
            )


# ==================================================
# 12. FOOTER
# ==================================================

st.divider()

st.caption(
    "AutoDesign Copilot | AI-assisted conceptual CAD generation"
)
