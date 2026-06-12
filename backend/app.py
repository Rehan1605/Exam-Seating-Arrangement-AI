from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from pdf_generator import generate_seating_pdf
from solver import SeatingSolver


app = Flask(__name__)
CORS(app)

solver = SeatingSolver()
students_store = []
halls_store = []
latest_arrangement = None
latest_generation = None
latest_pdf_path = None
REPORTS_DIR = Path(__file__).parent / "reports"

REQUIRED_STUDENT_COLUMNS = ["RollNo", "Name", "Branch"]


@app.get("/")
def health_check():
    return jsonify({"status": "ok", "service": "exam-seating-backend"})


@app.post("/upload")
def upload_students():
    global students_store, latest_arrangement, latest_generation, latest_pdf_path

    if "file" not in request.files:
        return jsonify({"error": "CSV file is required"}), 400

    uploaded_file = request.files["file"]
    if not uploaded_file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are supported"}), 400

    try:
        dataframe = pd.read_csv(uploaded_file, dtype=str)
    except Exception as exc:
        return jsonify({"error": f"Unable to parse CSV: {exc}"}), 400

    missing_columns = [column for column in REQUIRED_STUDENT_COLUMNS if column not in dataframe.columns]
    if missing_columns:
        return jsonify({
            "error": "Missing required columns",
            "missingColumns": missing_columns,
            "requiredColumns": REQUIRED_STUDENT_COLUMNS,
        }), 400

    dataframe = dataframe[REQUIRED_STUDENT_COLUMNS].fillna("").astype(str)
    students_store = dataframe.to_dict(orient="records")
    latest_arrangement = None
    latest_generation = None
    latest_pdf_path = None

    return jsonify({
        "message": "File uploaded successfully",
        "filename": uploaded_file.filename,
        "row_count": len(students_store),
        "students": students_store,
        "preview": students_store[:10],
    })


@app.post("/save-halls")
def save_halls():
    global halls_store, latest_arrangement, latest_generation, latest_pdf_path

    payload = request.get_json(silent=True) or {}
    halls = payload.get("halls", [])
    if not isinstance(halls, list) or not halls:
        return jsonify({"error": "At least one hall is required"}), 400

    normalized_halls = []
    for index, hall in enumerate(halls):
        hall_name = str(hall.get("hallName") or "").strip()
        try:
            rows = int(hall.get("rows") or 0)
            cols = int(hall.get("cols") or hall.get("columns") or 0)
        except (TypeError, ValueError):
            return jsonify({"error": f"Hall {index + 1} requires numeric rows and columns"}), 400

        if not hall_name:
            return jsonify({"error": f"Hall {index + 1} requires a hallName"}), 400
        if rows <= 0 or cols <= 0:
            return jsonify({"error": f"{hall_name} requires positive rows and columns"}), 400

        normalized_halls.append({
            "hallName": hall_name,
            "rows": rows,
            "cols": cols,
            "blockedSeats": hall.get("blockedSeats", ""),
        })

    halls_store = normalized_halls
    latest_arrangement = None
    latest_generation = None
    latest_pdf_path = None

    return jsonify({
        "message": "Hall configuration saved successfully",
        "halls": halls_store,
    })


@app.post("/generate-seating")
def generate_seating():
    return _generate(shuffle=False)


@app.post("/regenerate")
def regenerate():
    return _generate(shuffle=True)


@app.post("/select-arrangement")
def select_arrangement():
    global latest_arrangement, latest_pdf_path

    if not latest_generation or latest_generation.get("success") is False:
        return jsonify({"error": "Generate valid seating arrangements before selecting one"}), 400

    payload = request.get_json(silent=True) or {}
    arrangement_id = payload.get("arrangementId")
    selected = next(
        (item for item in latest_generation.get("arrangements", []) if item.get("id") == arrangement_id),
        None,
    )
    if not selected:
        return jsonify({"error": "Selected arrangement was not found"}), 404

    latest_arrangement = selected
    latest_pdf_path = None
    return jsonify({
        "message": f"{selected.get('label', 'Arrangement')} selected successfully",
        "arrangement": selected,
    })


@app.post("/generate-pdf")
def generate_pdf():
    global latest_pdf_path

    if not latest_arrangement:
        return jsonify({"error": "Generate seating before creating PDF"}), 400
    if latest_arrangement.get("success") is False:
        return jsonify({"error": latest_arrangement.get("message", "Cannot create PDF for failed seating generation")}), 400

    payload = request.get_json(silent=True) or {}
    metadata = payload.get("metadata", payload)
    latest_pdf_path = generate_seating_pdf(latest_arrangement, metadata, output_dir=REPORTS_DIR)

    return jsonify({
        "message": "PDF generated successfully",
        "filename": latest_pdf_path.name,
    })


@app.get("/download-pdf")
def download_pdf():
    if not latest_pdf_path or not Path(latest_pdf_path).exists():
        return jsonify({"error": "Generate PDF before downloading"}), 400

    return send_file(
        latest_pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=Path(latest_pdf_path).name,
    )


def _generate(shuffle):
    global latest_arrangement, latest_generation, latest_pdf_path

    if not students_store:
        return jsonify({"error": "Upload student CSV before generating seating"}), 400
    if not halls_store:
        return jsonify({"error": "Save hall configuration before generating seating"}), 400

    payload = request.get_json(silent=True) or {}
    constraints = payload.get("constraints", payload)
    latest_generation = solver.generate(students_store, halls_store, constraints, shuffle=shuffle)
    latest_arrangement = latest_generation
    latest_pdf_path = None

    if latest_generation.get("success") is False:
        message = latest_generation["message"]
    else:
        message = "Seating regenerated successfully" if shuffle else "Seating generated successfully"

    return jsonify({
        "message": message,
        "arrangement": latest_generation,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
