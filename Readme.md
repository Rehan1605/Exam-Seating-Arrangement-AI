# AI-Based Examination Seating Arrangement System

An AI-powered web application that automates university examination seating arrangements using Constraint Satisfaction Problem (CSP) techniques.

Built using React, Flask, and Python-based CSP algorithms.

---

## Features

* Student CSV Upload
* Dynamic Hall Configuration
* Subject/Branch Mapping
* Constraint-Based Seating Allocation
* CSP Solver with:

  * Backtracking
  * Forward Checking
  * MRV Heuristic
* Regenerate Seating Layouts
* Hall-wise Seating Preview
* Official PDF Seating Report Generation
* Blocked Seat Handling
* Same-Subject Gap Constraints
* Responsive React Frontend
* Flask REST API Backend

---

## Tech Stack

### Frontend

* React + Vite
* React Router DOM
* CSS

### Backend

* Flask
* Flask-CORS
* Pandas
* ReportLab

### AI Concepts

* Constraint Satisfaction Problem (CSP)
* Recursive Backtracking
* Forward Checking
* MRV Heuristic
* Constraint Validation

---

## Project Structure

```text
Exam-Seating-AI/
│
├── frontend/
│   └── exam-seating/
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── services/
│       │   └── styles/
│       └── package.json
│
├── backend/
│   ├── app.py
│   ├── solver.py
│   ├── pdf_generator.py
│   ├── requirements.txt
│   └── reports/
│
└── README.md
```

---

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/Rehan1605/Exam-Seating-Arrangement-AI.git
cd Exam-Seating-Arrangement-AI
```

---

## Frontend Setup

```bash
cd frontend/exam-seating
npm install
npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

---

## Backend Setup

Create and activate virtual environment:

### Windows

```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Flask server:

```bash
python app.py
```

Backend runs on:

```text
http://localhost:5000
```

---

## Input CSV Format

### Student CSV

```csv
RollNo,Name,Branch
2520030239,Rehan,CSE
2520030240,Ravi,ECE
```

---

## Hall Configuration Example

| Hall Name | Rows | Columns | Blocked Seats |
| --------- | ---- | ------- | ------------- |
| H1-01     | 6    | 6       | A3,C4         |
| H1-02     | 6    | 5       | B2            |

---

## CSP Constraints Implemented

* One student per seat
* Blocked seats cannot be assigned
* Same-subject adjacency handling
* Gap constraints between same-subject students
* Hall capacity constraints

---

## Same Subject Handling Modes

* Allow Adjacent
* Prevent Adjacent
* Leave One Seat Gap

---

## PDF Report Features

* Hall Summary Page
* Hall-wise Seating Layout
* Registered/Present/Absent Counts
* Invigilator Signature Placeholder
* Professional Examination Branch Format

---

## Future Enhancements

* Database Integration
* Authentication System
* Manual Seat Swapping
* Subject-Level Mapping Integration
* Drag-and-Drop Seating
* Deployment

---

## Author

Rehan Shaik

---

## License

This project is developed for academic and educational purposes.
