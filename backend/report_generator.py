
import json
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


def generate_governance_report(
    dataset_report=None,
    evaluation_report=None,
    risk_report=None,
    filename="AI_Governance_Report"
):
    return {
        "report_title": "AI Governance Report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_analysis": dataset_report,
        "model_evaluation": evaluation_report,
        "risk_assessment": risk_report,
        "limitations": [
            "This report contains preliminary automated checks.",
            "Performance metrics alone do not establish model fairness.",
            "This report does not establish safety or regulatory compliance.",
            "Recommendations should be reviewed by a qualified person."
        ]
    }


def save_report(report, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)


def generate_pdf_report(report, output_path):
    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        leading=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1b2a49"),
        spaceAfter=12,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#2455d6"),
        spaceBefore=16,
        spaceAfter=8,
    ))

    story = []

    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph(
        "AI GOVERNANCE REPORT",
        styles["ReportTitle"]
    ))
    story.append(Paragraph(
        "Dataset Quality, Model Evaluation and Risk Assessment",
        styles["Normal"]
    ))
    story.append(Spacer(1, 1 * cm))

    generated_at = report.get("generated_at", "Not available")
    story.append(Paragraph(
        f"<b>Generated:</b> {escape(str(generated_at))}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph(
        "This report summarizes automated dataset checks, "
        "classification metrics and identified risks.",
        styles["BodyText"]
    ))
    story.append(PageBreak())

    dataset = report.get("dataset_analysis") or {}

    story.append(Paragraph("1. Dataset Quality", styles["SectionHeading"]))

    dataset_rows = [
        ["Measure", "Result"],
        ["Rows", str(dataset.get("rows", "Not provided"))],
        ["Columns", str(dataset.get("columns", "Not provided"))],
        ["Duplicate rows", str(dataset.get("duplicate_rows", "Not provided"))],
    ]

    dataset_table = Table(dataset_rows, colWidths=[7 * cm, 8 * cm])
    dataset_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b2a49")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d5dbea")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(dataset_table)

    missing = dataset.get("missing_values") or {}
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Missing values by column</b>", styles["Normal"]))

    missing_rows = [["Column", "Missing values"]]
    for column, count in missing.items():
        missing_rows.append([str(column), str(count)])

    if len(missing_rows) == 1:
        missing_rows.append(["No column data", "Not available"])

    missing_table = Table(missing_rows, colWidths=[7 * cm, 8 * cm])
    missing_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf0ff")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d5dbea")),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(missing_table)

    warnings = dataset.get("warnings") or []
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Data-quality warnings</b>", styles["Normal"]))

    if warnings:
        for warning in warnings:
            story.append(Paragraph(
                "• " + escape(str(warning)),
                styles["BodyText"]
            ))
    else:
        story.append(Paragraph("No warnings provided.", styles["BodyText"]))

    evaluation = report.get("model_evaluation") or {}

    story.append(Paragraph("2. Model Evaluation", styles["SectionHeading"]))

    metric_rows = [["Metric", "Score"]]
    for key, label in [
        ("accuracy", "Accuracy"),
        ("precision", "Precision"),
        ("recall", "Recall"),
        ("f1_score", "F1-score"),
    ]:
        value = evaluation.get(key)
        score = f"{value:.2%}" if isinstance(value, (int, float)) else "Not provided"
        metric_rows.append([label, score])

    metric_table = Table(metric_rows, colWidths=[7 * cm, 8 * cm])
    metric_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b2a49")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d5dbea")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(metric_table)

    matrix = evaluation.get("confusion_matrix")
    if matrix:
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Confusion Matrix</b>", styles["Normal"]))
        matrix_rows = [[""] + [f"Predicted {i + 1}" for i in range(len(matrix[0]))]]
        for index, row in enumerate(matrix):
            matrix_rows.append([f"Actual {index + 1}"] + [str(value) for value in row])

        matrix_table = Table(matrix_rows)
        matrix_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf0ff")),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eaf0ff")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d5dbea")),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ]))
        story.append(matrix_table)

    risk_report = report.get("risk_assessment") or {}
    risks = risk_report.get("risks") or []

    story.append(Paragraph("3. Risk Assessment", styles["SectionHeading"]))
    story.append(Paragraph(
        f"<b>Total risks identified:</b> "
        f"{risk_report.get('risk_count', len(risks))}",
        styles["BodyText"]
    ))
    story.append(Spacer(1, 8))

    if risks:
        risk_rows = [["Category", "Severity", "Issue", "Recommendation"]]
        for risk in risks:
            risk_rows.append([
                Paragraph(escape(str(risk.get("category", "N/A"))), styles["BodyText"]),
                Paragraph(escape(str(risk.get("severity", "N/A"))), styles["BodyText"]),
                Paragraph(escape(str(risk.get("issue", "N/A"))), styles["BodyText"]),
                Paragraph(escape(str(risk.get("recommendation", "N/A"))), styles["BodyText"]),
            ])

        risk_table = Table(
            risk_rows,
            colWidths=[3 * cm, 2 * cm, 5 * cm, 5 * cm],
            repeatRows=1
        )
        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b2a49")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d5dbea")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(risk_table)
    else:
        story.append(Paragraph(
            "No risk details were provided for this report.",
            styles["BodyText"]
        ))

    story.append(Paragraph("4. Limitations", styles["SectionHeading"]))
    for limitation in report.get("limitations", []):
        story.append(Paragraph(
            "• " + escape(str(limitation)),
            styles["BodyText"]
        ))
        story.append(Spacer(1, 4))

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(
            A4[0] / 2,
            1 * cm,
            f"AI Governance Report | Page {doc.page}"
        )
        canvas.restoreState()

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )



def generate_model_card(
    dataset_report=None,
    evaluation_report=None,
    risk_report=None,
    model_info=None
):
    dataset_report = dataset_report or {}
    evaluation_report = evaluation_report or {}
    risk_report = risk_report or {}
    model_info = model_info or {}

    return {
        "model_card_title": "Machine Learning Model Card",

        "model_name": model_info.get(
            "model_name", "Model Under Evaluation"
        ),
        "version": model_info.get(
            "version", "Not specified"
        ),

        "overview": {
            "purpose": (model_info or {}).get(
                "purpose",
                "Document the model's evaluation and governance information."),
            "intended_use": model_info.get(
                "intended_use",
                "Specify the intended use before deployment."
            ),
            "model_type": model_info.get(
                "model_type", "Not specified"
            ),
            "training_data": model_info.get(
                "training_data",
                "Training data details not provided."
            )
        },

        "dataset_summary": {
            "rows": dataset_report.get("rows"),
            "columns": dataset_report.get("columns"),
            "column_names": dataset_report.get(
                "column_names", []
            ),
            "missing_values": dataset_report.get(
                "missing_values", {}
            ),
            "duplicate_rows": dataset_report.get(
                "duplicate_rows"
            )
        },

        "evaluation_results": evaluation_report,
        "risk_assessment": risk_report,

        "limitations": [
            model_info.get(
                "limitations",
                "Model architecture and training details have not been provided."
            ),
            "Evaluation results depend on the supplied evaluation dataset.",
            "Performance metrics alone do not establish fairness or safety.",
            "Intended use and limitations require human review before deployment."
        ]
    }


def generate_model_card_pdf(model_card, output_path):
    from xml.sax.saxutils import escape

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        KeepTogether
    )

    model_card = model_card or {}

    # output_path can be a filename or an in-memory BytesIO object.
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="AI Model Card",
        author="AI Governance Platform"
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CardTitle",
        parent=styles["Title"],
        fontSize=23,
        leading=29,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="CardSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#526579"),
        spaceAfter=18
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=12,
        spaceAfter=7,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name="CardBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        spaceAfter=5,
        wordWrap="CJK"
    ))

    styles.add(ParagraphStyle(
        name="SmallCell",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        wordWrap="CJK"
    ))

    story = []

    def display_value(value):
        if value is None or value == "":
            return "Not provided"
        if isinstance(value, (dict, list)):
            import json
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def safe_paragraph(value):
        return Paragraph(
            escape(display_value(value)),
            styles["SmallCell"]
        )

    def add_section(title):
        story.append(Paragraph(escape(title), styles["SectionHeading"]))

    def add_paragraph(label, value):
        content = (
            f"<b>{escape(str(label))}:</b> "
            f"{escape(display_value(value))}"
        )
        story.append(Paragraph(content, styles["CardBody"]))

    def add_table(headers, rows, widths=None):
        table_data = [
            [safe_paragraph(item) for item in headers]
        ]

        for row in rows:
            table_data.append([
                safe_paragraph(item) for item in row
            ])

        table = Table(
            table_data,
            colWidths=widths,
            repeatRows=1,
            hAlign="LEFT"
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
            colors.HexColor("#17365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4,
            colors.HexColor("#D5DDE5")),
            ("BACKGROUND", (0, 1), (-1, -1),
            colors.HexColor("#F7F9FC")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ]))

        story.append(table)
        story.append(Spacer(1, 7))

    def add_bullets(items):
        if not items:
            items = ["No details provided."]

        for item in items:
            story.append(Paragraph(
                "&#8226; " + escape(display_value(item)),
                styles["CardBody"]
            ))

    # Title
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        escape(model_card.get(
            "model_card_title", "Machine Learning Model Card"
        )),
        styles["CardTitle"]
    ))
    story.append(Paragraph(
        "AI Governance Documentation",
        styles["CardSubtitle"]
    ))

    story.append(Paragraph(
        "This document summarizes the available model information, "
        "evaluation results, and governance considerations.",
        styles["CardBody"]
    ))

    # Model overview
    add_section("1. Model Overview")

    overview = model_card.get("overview") or {}

    add_paragraph("Model name", model_card.get("model_name"))
    add_paragraph("Version", model_card.get("version"))
    add_paragraph("Purpose", overview.get("purpose"))
    add_paragraph("Intended use", overview.get("intended_use"))
    add_paragraph("Model type", overview.get("model_type"))
    add_paragraph("Training data", overview.get("training_data"))

    # Dataset summary
    add_section("2. Dataset Summary")

    dataset = model_card.get("dataset_summary") or {}

    add_table(
        ["Property", "Value"],
        [
            ["Rows", display_value(dataset.get("rows"))],
            ["Columns", display_value(dataset.get("columns"))],
            ["Column names", display_value(
                dataset.get("column_names", [])
            )],
            ["Duplicate rows", display_value(
                dataset.get("duplicate_rows")
            )]
        ],
        widths=[5 * cm, 11 * cm]
    )

    missing_values = dataset.get("missing_values") or {}

    if missing_values:
        add_section("Missing Values by Column")
        add_table(
            ["Column", "Missing values"],
            list(missing_values.items()),
            widths=[8 * cm, 8 * cm]
        )

    # Evaluation
    add_section("3. Model Evaluation")

    evaluation = model_card.get("evaluation_results") or {}

    metric_labels = {
        "accuracy": "Accuracy",
        "precision": "Precision",
        "recall": "Recall",
        "f1_score": "F1 Score",
        "f1": "F1 Score"
    }

    metric_rows = []

    for key, label in metric_labels.items():
        if key in evaluation and not any(
            row[0] == label for row in metric_rows
        ):
            metric_rows.append([label, evaluation[key]])

    if metric_rows:
        add_table(
            ["Metric", "Value"],
            metric_rows,
            widths=[8 * cm, 8 * cm]
        )
    else:
        story.append(Paragraph(
            "No evaluation metrics were provided.",
            styles["CardBody"]
        ))

    confusion_matrix = evaluation.get("confusion_matrix")

    if confusion_matrix is not None:
        add_section("Confusion Matrix")

        if isinstance(confusion_matrix, list) and confusion_matrix:
            matrix_rows = []

            for index, row in enumerate(confusion_matrix):
                if isinstance(row, list):
                    matrix_rows.append(
                        [f"Row {index + 1}"] + row
                    )

            if matrix_rows:
                matrix_headers = (
                    ["Actual / Row"] +
                    [f"Column {i + 1}"
                    for i in range(len(matrix_rows[0]) - 1)]
                )

                add_table(matrix_headers, matrix_rows)

        else:
            add_paragraph("Confusion matrix", confusion_matrix)

    # Risks
    add_section("4. Risk Assessment")

    risk_report = model_card.get("risk_assessment") or {}
    risks = risk_report.get("risks") or []

    add_paragraph("Total identified risks", risk_report.get("risk_count"))

    if risks:
        risk_rows = []

        for risk in risks:
            if isinstance(risk, dict):
                risk_rows.append([
                    risk.get("risk", risk.get("description", "Not specified")),
                    risk.get("severity", "Not specified"),
                    risk.get("recommendation", "Not specified")
                ])
            else:
                risk_rows.append([risk, "Not specified", "Review manually"])

        add_table(
            ["Risk", "Severity", "Recommendation"],
            risk_rows,
            widths=[5 * cm, 2.5 * cm, 8.5 * cm]
        )
    else:
        story.append(Paragraph(
            "No risk details were provided. This does not prove that "
            "the model is risk-free.",
            styles["CardBody"]
        ))

    # Limitations
    add_section("5. Limitations and Review")

    limitations = model_card.get("limitations") or [
        "Model architecture and training details may be incomplete.",
        "Evaluation results depend on the supplied evaluation dataset.",
        "Performance metrics alone do not establish fairness or safety.",
        "Human review is required before deployment decisions."
    ]

    add_bullets(limitations)

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Governance notice:</b> This document is generated from "
        "available inputs. It does not independently establish model "
        "fairness, safety, or regulatory compliance.",
        styles["CardBody"]
    ))

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#526579"))
        canvas.drawString(
            1.8 * cm, 1.0 * cm, "AI Governance Platform"
        )
        canvas.drawRightString(
            A4[0] - 1.8 * cm,
            1.0 * cm,
            f"Page {document.page}"
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )
