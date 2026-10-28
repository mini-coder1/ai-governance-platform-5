
from io import BytesIO
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from data_analyzer import analyze_dataset
from model_evaluator import evaluate_model

from pydantic import BaseModel
from risk_checker import check_risks

from report_generator import (
    generate_governance_report,
    generate_model_card,
    generate_model_card_pdf,
    save_report,
    generate_pdf_report as build_pdf_report
)

from io import BytesIO
from fastapi.responses import StreamingResponse


class RiskRequest(BaseModel):
    dataset_report: dict | None = None
    evaluation_report: dict | None = None


class GovernanceReportRequest(BaseModel):
    dataset_report: dict | None = None
    evaluation_report: dict | None = None
    risk_report: dict | None = None
    model_info: Optional[dict] = None


app = FastAPI(
    title="AI Governance Documentation Platform",
    description="Analyze datasets and generate governance reports.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
        "https://ai-governance-platform-frontend.onrender.com",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "AI Governance Platform is running!"
    }


@app.post("/analyze-dataset")
async def analyze_uploaded_dataset(
    file: UploadFile = File(...)
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file."
        )

    try:
        content = await file.read()

        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File size must not exceed 10 MB."
            )

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        
        first_line = content.decode("utf-8-sig").splitlines()

        if not first_line or not first_line[0].strip():
            raise HTTPException(
                status_code=400,
                detail="CSV column headers are missing."
            )

        df = pd.read_csv(BytesIO(content))

        report = analyze_dataset(df)

        return {
            "filename": file.filename,
            "analysis": report
        }

    except HTTPException:
        raise


    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=400,
            detail="The CSV file has no readable data or column names."
        )

    except (pd.errors.ParserError, UnicodeDecodeError):
        raise HTTPException(
            status_code=400,
            detail="Could not read this CSV file. Please check its format and encoding."
        )


    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    finally:
        await file.close()

@app.post("/evaluate-model")
async def evaluate_uploaded_model(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file."
        )

    try:
        content = await file.read()

        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File size must not exceed 10 MB."
            )

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        df = pd.read_csv(BytesIO(content))

        if "actual" not in df.columns or "predicted" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="CSV must contain 'actual' and 'predicted' columns."
            )

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="The CSV contains no data rows."
            )

        if df[["actual", "predicted"]].isnull().any().any():
            raise HTTPException(
                status_code=400,
                detail="Actual and predicted columns cannot contain missing values."
            )

        report = evaluate_model(
            df["actual"].tolist(),
            df["predicted"].tolist()
        )

        return {
            "filename": file.filename,
            "evaluation": report
        }

    except HTTPException:
        raise

    
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=400,
            detail="The CSV file has no readable data or column names."
        )

    except (pd.errors.ParserError, UnicodeDecodeError):
        raise HTTPException(
            status_code=400,
            detail="Could not read this CSV file. Please check its format and encoding."
        )


    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    finally:
        await file.close()

@app.post("/check-risks")
def check_risks_endpoint(request: RiskRequest):
    return check_risks(
        request.dataset_report,
        request.evaluation_report
    )


@app.post("/generate-report")
def generate_report_endpoint(request: GovernanceReportRequest):
    report = generate_governance_report(
        dataset_report=request.dataset_report,
        evaluation_report=request.evaluation_report,
        risk_report=request.risk_report
    )

    return report

@app.post("/generate-pdf-report")
def generate_pdf_report_endpoint(request: GovernanceReportRequest):
    report = generate_governance_report(
        request.dataset_report,
        request.evaluation_report,
        request.risk_report
    )

    pdf_buffer = BytesIO()

    build_pdf_report(report, pdf_buffer)

    pdf_buffer.seek(0)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="AI_Governance_Report.pdf"'
        }
    )

@app.post("/generate-model-card")
def generate_model_card_endpoint(request: GovernanceReportRequest):
    return generate_model_card(
        dataset_report=request.dataset_report,
        evaluation_report=request.evaluation_report,
        risk_report=request.risk_report,
        model_info=request.model_info
    )


from io import BytesIO
from fastapi.responses import StreamingResponse


@app.post("/generate-model-card-pdf")
def generate_model_card_pdf_endpoint(
    request: GovernanceReportRequest
):
    model_card = generate_model_card(
        dataset_report=request.dataset_report,
        evaluation_report=request.evaluation_report,
        risk_report=request.risk_report,
        model_info=request.model_info
    )

    pdf_buffer = BytesIO()

    generate_model_card_pdf(model_card, pdf_buffer)

    pdf_buffer.seek(0)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="AI_Model_Card.pdf"'
        }
    )
