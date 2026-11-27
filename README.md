# AutoDesign Copilot
### AI-Powered Automotive CAD Design & Automation Platform

**Transforming Natural Language Engineering Requirements into 3D CAD Models using Generative AI.**

AutoDesign Copilot is an AI-powered automotive engineering application designed to simplify and automate the CAD modeling process. It uses Generative AI to interpret natural-language design requirements, generate structured engineering specifications, validate component parameters, and translate them into 3D CAD geometry through FreeCAD.

The platform aims to bridge the gap between engineering intent and CAD implementation by making component modeling more intuitive, accessible, and efficient.

---

## Overview

Traditional CAD modeling often requires manual geometry creation, detailed parameter entry, and familiarity with specialized CAD software.

AutoDesign Copilot introduces an AI-assisted workflow in which users describe the automotive component they want to design in natural language. The application processes the request, generates a structured CAD specification, validates the parameters, and passes the specification to a FreeCAD automation macro for 3D model generation.

## Key Features

- **Natural Language Design Input:** Describe automotive components using text-based engineering requirements.
- **Generative AI Integration:** Interpret user requests and convert them into structured CAD specifications.
- **Automated Specification Generation:** Generate component parameters and geometric design instructions.
- **Engineering Parameter Validation:** Validate required dimensions and identify missing or incomplete design information.
- **Parametric CAD Automation:** Use FreeCAD macros to construct 3D component geometry from generated specifications.
- **CAD Export Support:** Support model export into formats such as STEP and STL, depending on the generated model and application configuration.
- **Interactive Interface:** Provide a user-friendly interface through Streamlit.

## System Architecture

```text
User Design Requirements
          |
          v
   Streamlit Interface
          |
          v
   Generative AI Engine
          |
          v
    CAD Specification
          |
          v
   Specification Parser
          |
          v
   Parameter Validation
          |
          v
    FreeCAD Automation
          |
          v
     3D CAD Model
          |
          v
    CAD File Export
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Google Gemini API | Generative AI integration |
| Streamlit | Interactive web interface |
| FreeCAD | 3D CAD modeling and automation |
| JSON | Structured CAD specifications |
| Python Automation | CAD workflow execution |

## Project Structure

```text
AutoDesign-Copilot/
│
├── app.py
├── cad_parser.py
├── cad_engine.py
│
├── cad/
│   ├── universal_cad.FCMacro
│   └── current_spec.json
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Application Workflow

1. The user enters an automotive component design request.
2. The Generative AI engine interprets the engineering requirements.
3. The application converts the request into a structured JSON specification.
4. The CAD parser processes the generated specification.
5. The validation engine checks the availability and consistency of required parameters.
6. The FreeCAD macro interprets the specification and generates the corresponding 3D geometry.
7. The resulting CAD model can be exported in supported formats.

## Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version supported by the dependencies
- FreeCAD installed locally
- Google Gemini API key
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Lavanya-1411/AutoDesign-Copilot.git

cd AutoDesign-Copilot
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Never commit API keys or secret credentials to GitHub.

### 5. Configure FreeCAD

Ensure FreeCAD is installed and configure the executable path in the application according to your system.

### 6. Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal to access the application.

## Engineering Applications

The platform is designed with potential applications in automotive component development, including:

- Suspension and control-arm components
- Flywheel and rotating components
- Pistons and cylindrical automotive components
- Other mechanical components supported by the CAD generation engine

Actual component support depends on the implemented geometry builders and specification schema.

## Future Development

- Expand support for complex automotive component geometries.
- Improve automatic geometric constraint generation.
- Introduce advanced parametric modeling capabilities.
- Integrate CAD model validation and simulation workflows.
- Develop cloud-based CAD generation capabilities.
- Explore integration with automotive CAE tools.

## Project Significance

AutoDesign Copilot explores how Generative AI can connect natural-language engineering requirements with automated CAD modeling.

By combining AI-based requirement interpretation, structured parameter validation, and CAD automation, the project demonstrates a practical approach to reducing repetitive modeling tasks and improving engineering workflow accessibility.

## Author

**Lavanya B.**

Automobile Engineering | Generative AI | CAD Automation | Python

GitHub: [Lavanya-1411](https://github.com/Lavanya-1411)

---

**AutoDesign Copilot — From Engineering Requirements to Intelligent 3D Design.**
