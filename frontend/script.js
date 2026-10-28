const API_BASE_URL = "https://ai-governance-platform-5.onrender.com";
const form = document.getElementById("upload-form");
const fileInput = document.getElementById("csv-file");
const button = document.getElementById("analyze-button");
const statusText = document.getElementById("status");
const results = document.getElementById("results");
const downloadButton = document.getElementById("download-report");

let latestReport = null;
let latestDatasetReport = null;
let latestEvaluationReport = null;

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const file = fileInput.files[0];

    if (!file) {
        statusText.textContent = "Please select a CSV file.";
        return;
    }

    if (!file.name.toLowerCase().endsWith(".csv")) {
        statusText.textContent = "Please select a CSV file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    button.disabled = true;
    button.textContent = "Analyzing...";
    statusText.textContent = "Analyzing dataset. Please wait.";
    results.hidden = true;

    try {
        const response = await fetch(
            API_BASE_URL + "/analyze-dataset",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();
        latestDatasetReport = data.analysis;

        if (!response.ok) {
            throw new Error(data.detail || "Analysis failed.");
        }

        const report = data.analysis;
        latestReport = data;

        document.getElementById("filename").textContent =
            "File: " + data.filename;

        document.getElementById("rows").textContent =
            report.rows;

        document.getElementById("columns").textContent =
            report.columns;

        document.getElementById("duplicates").textContent =
            report.duplicate_rows;

        showObject("column-names", report.column_names);
        showObject("data-types", report.data_types);
        showObject("missing-values", report.missing_values);
        showObject("missing-percentages", report.missing_percentages);
        showObject("warnings", report.warnings);

        results.hidden = false;
        statusText.textContent = "Dataset analyzed successfully!";

    } catch (error) {
        statusText.textContent =
            "Error: " + error.message +
            " Check that the backend server is running.";

    } finally {
        button.disabled = false;
        button.textContent = "Analyze Dataset";
    }
});

function showObject(elementId, value) {
    const container = document.getElementById(elementId);

    if (Array.isArray(value)) {
        container.textContent = value.join(", ");
    } else {
        container.textContent = Object.entries(value)
            .map(([key, item]) => key + ": " + item)
            .join("\n");
    }
}
downloadButton.addEventListener("click", function () {
    if (!latestReport) {
        statusText.textContent = "Analyze a dataset first.";
        return;
    }

    const json = JSON.stringify(latestReport, null, 4);

    const blob = new Blob(
        [json],
        { type: "application/json" }
    );

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "governance-report.json";
    link.click();

    URL.revokeObjectURL(url);
});

const evaluationForm = document.getElementById("evaluation-form");
const evaluationFile = document.getElementById("evaluation-file");
const evaluateButton = document.getElementById("evaluate-button");
const evaluationStatus = document.getElementById("evaluation-status");
const evaluationResults = document.getElementById("evaluation-results");
const evaluationMetrics = document.getElementById("evaluation-metrics");
const confusionMatrix = document.getElementById("confusion-matrix");

evaluationForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const file = evaluationFile.files[0];

    if (!file) {
        evaluationStatus.textContent = "Please select a CSV file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    evaluateButton.disabled = true;
    evaluateButton.textContent = "Evaluating...";
    evaluationStatus.textContent = "Evaluating predictions...";
    evaluationResults.hidden = true;

    try {
        const response = await fetch(
            API_BASE_URL + "/evaluate-model",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();
        latestEvaluationReport = data.evaluation;

        if (!response.ok) {
            throw new Error(data.detail || "Evaluation failed.");
        }

        const report = data.evaluation;

        evaluationMetrics.replaceChildren();

        addMetric("Accuracy", report.accuracy);
        addMetric("Precision", report.precision);
        addMetric("Recall", report.recall);
        addMetric("F1-score", report.f1_score);

        
confusionMatrix.replaceChildren();

const matrix = report.confusion_matrix;

const table = document.createElement("table");
table.className = "confusion-table";

matrix.forEach(function (row, rowIndex) {
    const tr = document.createElement("tr");

    row.forEach(function (value) {
        const cell = document.createElement("td");
        cell.textContent = value;
        tr.appendChild(cell);
    });

    table.appendChild(tr);
});

confusionMatrix.appendChild(table);


        evaluationResults.hidden = false;
        evaluationStatus.textContent =
            "Evaluation completed for " + data.filename + ".";

    } catch (error) {
        evaluationStatus.textContent =
            "Error: " + error.message +
            " Check that the backend is running.";

    } finally {
        evaluateButton.disabled = false;
        evaluateButton.textContent = "Evaluate Model";
    }
});

function addMetric(label, value) {
    const card = document.createElement("div");
    card.className = "stat";

    const heading = document.createElement("span");
    heading.textContent = label;

    const number = document.createElement("strong");
    number.textContent = (value * 100).toFixed(2) + "%";

    card.append(heading, number);
    evaluationMetrics.appendChild(card);
}


const riskButton = document.getElementById("risk-button");
const riskStatus = document.getElementById("risk-status");
const riskResults = document.getElementById("risk-results");
const riskCount = document.getElementById("risk-count");
const riskList = document.getElementById("risk-list");
const riskNote = document.getElementById("risk-note");

riskButton.addEventListener("click", async function () {
    riskStatus.textContent = "Checking for risks...";
    riskResults.hidden = true;
    riskButton.disabled = true;

    try {
        const response = await fetch(
            API_URL_BASE + "/check-risks",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                
            body: JSON.stringify({
                dataset_report: latestDatasetReport,
                evaluation_report: latestEvaluationReport
})

            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Risk assessment failed.");
        }

        riskCount.textContent = data.risk_count;
        riskList.replaceChildren();

        if (data.risks.length === 0) {
            const message = document.createElement("p");
            message.textContent =
                "No risks were identified from the reports provided.";
            riskList.appendChild(message);
        }

        data.risks.forEach(function (risk) {
            const card = document.createElement("div");
            card.className = "result-box";

            const title = document.createElement("h4");
            title.textContent = risk.category + " — " + risk.severity;

            const issue = document.createElement("p");
            issue.textContent = risk.issue;

            const recommendation = document.createElement("p");
            recommendation.textContent =
                "Recommendation: " + risk.recommendation;

            card.append(title, issue, recommendation);
            riskList.appendChild(card);
        });

        riskNote.textContent = data.note;
        riskResults.hidden = false;
        riskStatus.textContent = "Risk assessment completed.";

    } catch (error) {
        riskStatus.textContent =
            "Error: " + error.message +
            " Check that your backend is running.";

    } finally {
        riskButton.disabled = false;
    }
});


const generateReportButton = document.getElementById(
    "generate-report-button"
);
const reportStatus = document.getElementById("report-status");

generateReportButton.addEventListener("click", async function () {
    if (!latestDatasetReport &&
        !latestEvaluationReport) {
        reportStatus.textContent =
            "Please analyze a dataset or evaluate a model first.";
        return;
    }

    generateReportButton.disabled = true;
    generateReportButton.textContent = "Generating Report...";
    reportStatus.textContent = "Preparing your governance report...";

    try {
        let riskReport = null;

        const riskResponse = await fetch(
            API_BASE_URL + "/check-risks",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    dataset_report: latestDatasetReport,
                    evaluation_report: latestEvaluationReport
                })
            }
        );

        const riskData = await riskResponse.json();

        if (!riskResponse.ok) {
            throw new Error(
                riskData.detail || "Could not assess risks."
            );
        }

        riskReport = riskData;

        const reportResponse = await fetch(
            API_BASE_URL + "/generate-report",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    dataset_report: latestDatasetReport,
                    evaluation_report: latestEvaluationReport,
                    risk_report: riskReport
                })
            }
        );

        const reportData = await reportResponse.json();

        if (!reportResponse.ok) {
            throw new Error(
                reportData.detail || "Could not generate report."
            );
        }

        const blob = new Blob(
            [JSON.stringify(reportData, null, 2)],
            { type: "application/json" }
        );

        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = "AI_Governance_Report.json";
        document.body.appendChild(link);
        link.click();
        link.remove();

        URL.revokeObjectURL(url);

        reportStatus.textContent =
            "Report generated and downloaded successfully!";

    } catch (error) {
        reportStatus.textContent =
            "Error: " + error.message +
            " Check that the backend is running.";

    } finally {
        generateReportButton.disabled = false;
        generateReportButton.textContent =
            "Generate Governance Report";
    }
});


const pdfDownloadButton = document.getElementById("download-pdf-button");

if (pdfDownloadButton) {
    pdfDownloadButton.addEventListener("click", async function () {
        const status = document.getElementById("report-status");

        try {
            if (!latestDatasetReport || !latestEvaluationReport) {
                status.textContent =
                    "Please analyze a dataset and evaluate a model first.";
                return;
            }

            status.textContent = "Generating PDF report...";
            pdfDownloadButton.disabled = true;

            const riskResponse = await fetch(
                API_BASE_URL + "/check-risks",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        dataset_report: latestDatasetReport,
                        evaluation_report: latestEvaluationReport
                    })
                }
            );

            if (!riskResponse.ok) {
                throw new Error("Failed to generate risk assessment.");
            }

            const riskReport = await riskResponse.json();

            const pdfResponse = await fetch(
                API_BASE_URL + "/generate-pdf-report",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        dataset_report: latestDatasetReport,
                        evaluation_report: latestEvaluationReport,
                        risk_report: riskReport
                    })
                }
            );

            if (!pdfResponse.ok) {
                throw new Error("Failed to generate PDF.");
            }

            const pdfBlob = await pdfResponse.blob();

            const downloadUrl = URL.createObjectURL(pdfBlob);
            const link = document.createElement("a");

            link.href = downloadUrl;
            link.download = "AI_Governance_Report.pdf";

            document.body.appendChild(link);
            link.click();
            link.remove();

            URL.revokeObjectURL(downloadUrl);

            status.textContent = "PDF report downloaded successfully!";
        } catch (error) {
            console.error("PDF download error:", error);
            status.textContent =
                "Could not download PDF. Check the backend and try again.";
        } finally {
            pdfDownloadButton.disabled = false;
        }
    });
}

function getModelInfo() {
    return {
        model_name: document.getElementById("model-name").value.trim(),
        purpose: document.getElementById("model-purpose").value.trim(),
        version: document.getElementById("model-version").value.trim(),
        intended_use: document.getElementById("model-intended-use").value.trim(),
        model_type: document.getElementById("model-type").value.trim(),
        training_data: document.getElementById("model-training-data").value.trim(),
        limitations: document.getElementById("model-limitations").value.trim()
    };
}


const modelCardButton = document.getElementById(
    "generate-model-card-button"
);

if (modelCardButton) {
    modelCardButton.addEventListener("click", async function () {
        const status = document.getElementById("model-card-status");

        try {
            if (!latestDatasetReport || !latestEvaluationReport) {
                status.textContent =
                    "Analyze a dataset and evaluate a model first.";
                return;
            }

            modelCardButton.disabled = true;
            status.textContent = "Generating model card...";

            const riskResponse = await fetch(
                API_BASE_URL + "/check-risks",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        dataset_report: latestDatasetReport,
                        evaluation_report: latestEvaluationReport
                    })
                }
            );

            if (!riskResponse.ok) {
                throw new Error("Risk assessment failed.");
            }

            const riskReport = await riskResponse.json();

            const response = await fetch(
                API_BASE_URL + "/generate-model-card",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        dataset_report: latestDatasetReport,
                        evaluation_report: latestEvaluationReport,
                        risk_report: riskReport,
                        model_info: getModelInfo()
                    })
                }
            );

            if (!response.ok) {
                throw new Error("Model card generation failed.");
            }

            const modelCard = await response.json();

            const blob = new Blob(
                [JSON.stringify(modelCard, null, 4)],
                { type: "application/json" }
            );

            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = url;
            link.download = "AI_Model_Card.json";

            document.body.appendChild(link);
            link.click();
            link.remove();

            URL.revokeObjectURL(url);

            status.textContent =
                "Model card downloaded successfully!";
        } catch (error) {
            console.error("Model card error:", error);
            status.textContent =
                "Could not generate model card. Check the backend.";
        } finally {
            modelCardButton.disabled = false;
        }
    });
}

const modelCardPdfButton = document.getElementById(
    "download-model-card-pdf-button"
);

if (modelCardPdfButton) {
    modelCardPdfButton.addEventListener("click", async function () {
        const status = document.getElementById("model-card-pdf-status");

        try {
            if (!latestDatasetReport || !latestEvaluationReport) {
                status.textContent =
                    "Analyze a dataset and evaluate a model first.";
                return;
            }

            modelCardPdfButton.disabled = true;
            status.textContent = "Generating PDF Model Card...";

            const riskResponse = await fetch(
                API_BASE_URL + "/check-risks",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        dataset_report: latestDatasetReport,
                        evaluation_report: latestEvaluationReport
                    })
                }
            );

            if (!riskResponse.ok) {
                throw new Error("Risk assessment failed.");
            }

            const riskReport = await riskResponse.json();

            const response = await fetch(
                API_BASE_URL + "/generate-model-card-pdf",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        dataset_report: latestDatasetReport,
                        evaluation_report: latestEvaluationReport,
                        risk_report: riskReport,
                        model_info: getModelInfo()
                    })
                }
            );

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(
                    "PDF generation failed: " + errorText
                );
            }

            const pdfBlob = await response.blob();

            if (pdfBlob.size === 0) {
                throw new Error("The generated PDF is empty.");
            }

            const url = URL.createObjectURL(pdfBlob);
            const link = document.createElement("a");

            link.href = url;
            link.download = "AI_Model_Card.pdf";

            document.body.appendChild(link);
            link.click();
            link.remove();

            URL.revokeObjectURL(url);

            status.textContent =
                "PDF Model Card downloaded successfully!";
        } catch (error) {
            console.error("PDF Model Card error:", error);
            status.textContent =
                "PDF download failed. Check the browser console.";
        } finally {
            modelCardPdfButton.disabled = false;
        }
    });
}
