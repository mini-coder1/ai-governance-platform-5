# AI Governance Documentation & Model Card Generation Platform

A web-based project for analyzing datasets, evaluating model
predictions, identifying basic data-quality and governance risks, and
generating governance reports and model cards in JSON and PDF formats.

> **Project status:** The backend test suite most recently reported **34
> passed, 1 warning**. The warning is a deprecation warning related to
> Starlette's `TestClient` integration with `httpx`; it did not cause a
> test failure.

## Table of Contents

-   [Overview](#overview)
-   [Features](#features)
-   [Technology Stack](#technology-stack)
-   [Project Structure](#project-structure)
-   [Requirements](#requirements)
-   [Setup](#setup)
-   [Running the Application](#running-the-application)
-   [API Endpoints](#api-endpoints)
-   [Testing](#testing)
-   [Example Dataset](#example-dataset)
-   [Limitations and Responsible Use](#limitations-and-responsible-use)
-   [Details to Confirm](#details-to-confirm)

## Overview

The platform brings several AI governance documentation tasks into one
application:

1.  Inspect an uploaded CSV dataset and summarize its structure and
    basic data-quality issues.
2.  Evaluate actual and predicted labels using common classification
    metrics.
3.  Run basic automated risk checks against available dataset and
    evaluation reports.
4.  Generate governance reports and model cards, with JSON and PDF
    output options.

The project is intended as a practical documentation and
preliminary-checking tool. Automated checks are not a substitute for a
full fairness, privacy, security, safety, legal, or regulatory
assessment.

## Features

### Dataset analysis

The dataset analyzer reports:

-   Number of rows and columns
-   Column names and inferred data types
-   Missing-value counts and percentages
-   Number of duplicate rows
-   Basic data-quality warnings

The dataset-analysis API accepts CSV uploads and includes checks for
file extension, empty uploads, file size, CSV parsing/encoding errors,
and blank first-line headers.

### Model evaluation

The model-evaluation endpoint evaluates a CSV containing actual and
predicted labels. The current implementation reports:

-   Accuracy
-   Weighted precision
-   Weighted recall
-   Weighted F1 score
-   Confusion matrix

Metrics are rounded to four decimal places. The endpoint validates
required columns and missing labels.

### Risk checks

The risk checker performs basic automated checks using the supplied
dataset and evaluation reports. Current checks include:

-   Missing values
-   Duplicate rows
-   Evaluation metrics below `0.80`

These checks are preliminary indicators, not proof that a model is fair,
safe, robust, or compliant.

### Governance reports

The platform can generate a governance report and export it as JSON or
PDF.

### Model cards

The platform can generate model cards in JSON and PDF formats. The
model-card request supports custom information fields:

-   `model_name`
-   `purpose`
-   `version`
-   `intended_use`
-   `model_type`
-   `training_data`
-   `limitations`

### Web interface

The frontend uses HTML, CSS, and JavaScript to interact with the backend
API. The project's current manual checks indicate that the interface
buttons and JSON/PDF generation flows work.

## Technology Stack

  Area               Technologies
  ------------------ ----------------------------
  Backend API        Python, FastAPI
  Data handling      pandas, NumPy
  Model evaluation   scikit-learn
  PDF generation     ReportLab
  Frontend           HTML, CSS, JavaScript
  Automated tests    pytest, FastAPI TestClient

Exact versions used in the current development environment are listed in
`backend/requirements.txt`.

## Project Structure

The following reflects the project structure established during
development. Some files may be added or changed as the project evolves.

``` text
ai_governance_platform/
├── .venv/
├── backend/
│   ├── data_analyzer.py
│   ├── main.py
│   ├── model_evaluator.py
│   ├── report_generator.py
│   ├── risk_checker.py
│   ├── sample.csv
│   ├── evaluation_sample.csv
│   ├── test_analyzer.py
│   ├── test_evaluator.py
│   ├── test_risk_checker.py
│   ├── test_report_generator.py
│   ├── test_api.py
│   ├── governance_report.json
│   ├── AI_Governance_Report.pdf
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── style.css
    ├── script.js
    └── requirements.txt  # currently empty; not required for a plain HTML/CSS/JS frontend
```

The `.venv` directory is a local Python virtual environment and should
generally not be committed to Git.

## Requirements

-   Python 3.13 was used in the current development environment.
-   A terminal such as PowerShell.
-   A modern web browser.
-   The Python packages listed in `backend/requirements.txt`.

## Setup

Open PowerShell in the project root directory.

### 1. Create a virtual environment

If you do not already have one:

``` powershell
python -m venv .venv
```

### 2. Activate the virtual environment

``` powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, use your environment's approved
activation method or activate it from the VS Code terminal settings.

### 3. Install backend dependencies

``` powershell
python -m pip install -r backend\requirements.txt
```

### 4. Check installed dependencies

``` powershell
python -m pip check
```

A healthy environment should report that no broken requirements were
found.

## Running the Application

### 1. Start the backend

In PowerShell, change into the backend directory:

``` powershell
cd backend
```

Start the FastAPI development server:

``` powershell
python -m uvicorn main:app --reload
```

The API base URL is expected to be:

``` text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is normally available at:

``` text
http://127.0.0.1:8000/docs
```

Keep this terminal running while using the frontend.

### 2. Open the frontend

Open `frontend/index.html` in a browser, or use the VS Code Live Server
extension if that is how the frontend is configured in your environment.

**Configuration note:** The frontend's exact launch method and API
base-URL configuration should be confirmed before publishing this
README. The backend CORS configuration currently allows local origins on
ports `5500` and `5501`.

## API Endpoints

The application currently defines these endpoints:

  ----------------------------------------------------------------------------
  Method                  Endpoint                     Purpose
  ----------------------- ---------------------------- -----------------------
  `GET`                   `/`                          Root/home endpoint

  `POST`                  `/analyze-dataset`           Upload and analyze a
                                                       CSV dataset

  `POST`                  `/evaluate-model`            Evaluate actual and
                                                       predicted labels from a
                                                       CSV

  `POST`                  `/check-risks`               Run basic risk checks
                                                       using supplied reports

  `POST`                  `/generate-report`           Generate a governance
                                                       report

  `POST`                  `/generate-pdf-report`       Generate a governance
                                                       PDF report

  `POST`                  `/generate-model-card`       Generate a model card

  `POST`                  `/generate-model-card-pdf`   Generate a model-card
                                                       PDF
  ----------------------------------------------------------------------------

For exact request fields, response formats, and examples, run the
backend and visit `/docs`.

### CSV upload checks

The dataset-analysis and model-evaluation endpoints include CSV upload
validation. The maximum accepted upload size is 10 MB. Invalid file
types, empty uploads, unreadable CSVs, and relevant invalid input cases
are rejected with HTTP errors.

## Testing

Run tests from the `backend` directory with the virtual environment
activated:

``` powershell
python -m pytest -v
```

To run only the API tests:

``` powershell
python -m pytest test_api.py -v
```

To run a specific test module:

``` powershell
python -m pytest test_analyzer.py -v
python -m pytest test_evaluator.py -v
python -m pytest test_risk_checker.py -v
python -m pytest test_report_generator.py -v
```

**Latest confirmed result:** the complete test suite reported
`34 passed, 1 warning`. Test results can change when the code or
dependencies change, so rerun the suite before submitting or releasing
the project.

## Example Dataset

The repository includes `backend/sample.csv` for dataset analysis and
`backend/evaluation_sample.csv` for model evaluation. Inspect these
files to confirm their exact columns and sample values before using them
in a demonstration.

For model evaluation, the uploaded CSV must contain the required
actual-label and predicted-label columns expected by the implementation.
Consult the code or `/docs` for the exact field names.

## Limitations and Responsible Use

-   The platform provides basic data-quality and evaluation summaries;
    it does not independently validate the quality or representativeness
    of a dataset.
-   A metric threshold or missing-value warning is not a complete risk
    assessment.
-   The current risk checks do not establish fairness across demographic
    groups, explainability, privacy protection, security, robustness,
    safety, or legal/regulatory compliance.
-   Evaluation metrics depend on the supplied labels and data. Results
    should be interpreted in the context of the model's intended use and
    evaluation design.
-   Do not upload confidential, personal, or otherwise sensitive data
    unless you have authorization and the deployment has suitable
    privacy and security controls.
-   Before production use, add an appropriate security review,
    deployment configuration, access controls, logging policy, and
    data-retention policy.

## Details to Confirm

Before publishing or submitting the project, verify these items and
update this README if necessary:

-   [ ] The final project title and author/contributor details.
-   [ ] The frontend's exact launch instructions and the API base URL
    configured in `frontend/script.js`.
-   [ ] The precise required CSV column names for model evaluation.
-   [ ] Whether generated JSON/PDF files are saved to disk, returned
    directly to the browser, or both for each endpoint.
-   [ ] Whether generated reports contain any additional fields not
    listed here.
-   [ ] Whether `frontend/requirements.txt` should be deleted; a plain
    HTML/CSS/JavaScript frontend does not need a Python requirements
    file.
-   [ ] Whether generated reports and the local `.venv` should be
    excluded from version control.
-   [ ] The exact dependency-warning resolution, if the warning is to be
    addressed before release.

## License

No license has been confirmed for this project. Add a `LICENSE` file and
update this section if you intend to distribute the project publicly.

------------------------------------------------------------------------

**Built as an AI governance documentation project** to make dataset
inspection, model evaluation, preliminary risk checks, and
model-card/report generation accessible through one web interface.
