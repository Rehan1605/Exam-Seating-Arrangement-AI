# Exam-Seating-AI

An intelligent web application that automates university examination seating arrangements using Constraint Satisfaction Problem (CSP) algorithms. The system optimizes seat allocation based on student data, exam hall configurations, and customizable constraints.

**Live Demo:** [Coming Soon](#)  
**Documentation:** [See Below](#documentation)

---

## 🎯 Features

### Core Functionality
- **Student CSV Upload** - Import student data with roll number, name, and branch
- **Dynamic Hall Configuration** - Define multiple exam halls with custom dimensions
- **Intelligent Seating Arrangement** - AI-powered CSP solver for optimal seat allocation
- **Constraint Management** - Apply custom constraints like blocked seats, same-subject gaps
- **Multiple Seating Layouts** - Generate and regenerate different seating configurations
- **Hall-wise Preview** - View seating arrangements by individual exam halls
- **PDF Report Generation** - Export official seating reports with seat assignments

### Advanced Features
- **Responsive UI** - Mobile-friendly interface built with modern React
- **Real-time Validation** - Instant feedback on input data and constraints
- **Session Management** - Authentication support for exam coordinators
- **Role-Based Access** - Different permission levels for administrators and supervisors

---

## 💻 Tech Stack

### Frontend
- **React 19.2** - UI framework
- **Vite 8.0** - Build tool and dev server
- **React Router DOM 7.15** - Client-side routing
- **Modern CSS** - Responsive styling with custom components

### Backend
- **Flask 3.1** - Lightweight Python web framework
- **Flask-CORS 6.0** - Cross-origin resource sharing
- **Pandas 2.3** - Data processing and CSV handling
- **ReportLab 4.4** - PDF generation

### AI & Algorithms
- **Constraint Satisfaction Problem (CSP)** - Core problem formulation
- **Recursive Backtracking** - Solution exploration
- **Forward Checking** - Constraint propagation
- **Minimum Remaining Values (MRV) Heuristic** - Optimization strategy
- **Constraint Validation Engine** - Dynamic constraint checking

---

## 📁 Project Structure

```
Exam-Seating-AI/
├── backend/
│   ├── app.py                 # Flask application & API routes
│   ├── solver.py              # CSP solver implementation
│   ├── pdf_generator.py       # PDF report generation
│   ├── requirements.txt       # Python dependencies
│   └── reports/               # Generated PDF reports
│
├── frontend/
│   └── exam-seating/
│       ├── src/
│       │   ├── components/    # Reusable UI components
│       │   │   ├── Navbar.jsx
│       │   │   ├── PageContainer.jsx
│       │   │   ├── SeatingGrid.jsx
│       │   │   └── StepNavigation.jsx
│       │   ├── pages/         # Application pages
│       │   │   ├── LoginPage.jsx
│       │   │   ├── DashboardPage.jsx
│       │   │   ├── UploadPage.jsx
│       │   │   ├── ExamDetailsPage.jsx
│       │   │   ├── HallConfigPage.jsx
│       │   │   ├── ConstraintsPage.jsx
│       │   │   ├── PreviewPage.jsx
│       │   │   └── SuccessPage.jsx
│       │   ├── services/      # API communication
│       │   │   └── api.js
│       │   ├── styles/        # Global styles
│       │   │   └── global.css
│       │   ├── App.jsx
│       │   ├── main.jsx
│       │   └── index.css
│       ├── public/
│       ├── package.json
│       ├── vite.config.js
│       ├── eslint.config.js
│       └── index.html
│
├── Readme.md
└── .gitignore
```

---

## 🚀 Installation & Setup

### Prerequisites
- **Node.js** (v16+) and npm
- **Python** (v3.8+) and pip
- Git

### 1. Clone Repository

```bash
git clone https://github.com/Rehan1605/Exam-Seating-Arrangement-AI.git
cd Exam-Seating-AI
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Flask server
python app.py
```

**Backend Server:** `http://localhost:5000`

### 3. Frontend Setup

```bash
cd ../frontend/exam-seating

# Install dependencies
npm install

# Run development server
npm run dev
```

**Frontend Application:** `http://localhost:5173` (or as shown in terminal)

---

## 📖 Usage

### Workflow

1. **Login** - Access the application with credentials
2. **Upload Students** - Import CSV file with student data
   - Required columns: `RollNo`, `Name`, `Branch`
3. **Configure Halls** - Define exam halls and seating capacities
4. **Set Constraints** - Add special constraints (blocked seats, gaps, etc.)
5. **Generate Seating** - Run the CSP solver to create arrangements
6. **Preview Results** - Review seating arrangement by hall
7. **Export Report** - Download official PDF seating chart

### Sample CSV Format

```csv
RollNo,Name,Branch
001,John Doe,CSE
002,Jane Smith,ECE
003,Bob Johnson,MECH
```

---

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/upload` | Upload student CSV file |
| POST | `/save-halls` | Configure exam halls |
| POST | `/generate-seating` | Generate seating arrangement |
| GET | `/preview` | Get seating preview |
| GET | `/download-pdf` | Download PDF report |

### Request/Response Examples

**Upload Students:**
```bash
curl -X POST -F "file=@students.csv" http://localhost:5000/upload
```

**Configure Halls:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"halls":[{"hallName":"Hall-A","rows":10,"cols":10}]}' \
  http://localhost:5000/save-halls
```

---

## 🛠️ Development

### Frontend Development
```bash
cd frontend/exam-seating

# Development server with hot reload
npm run dev

# Build for production
npm build

# Run linter
npm run lint

# Preview production build
npm run preview
```

### Backend Development
```bash
cd backend

# Run with auto-reload (requires watchdog)
pip install watchdog
python -m flask run --reload

# Or run directly
python app.py
```

---

## 📚 Documentation

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
venv\Scripts\activate  # On Windows: venv\Scripts\activate
```

Running the application with hot-reload:
```bash
python -m flask run --reload
```

---

## 🎓 CSP Algorithm Details

### Problem Formulation
The seating arrangement problem is modeled as a Constraint Satisfaction Problem (CSP) where:
- **Variables:** Seats in exam halls
- **Domain:** Students to be seated
- **Constraints:** Blocked seats, same-subject gaps, capacity limits

### Solving Strategy
1. **Backtracking Search** - Explores solution space systematically
2. **Forward Checking** - Validates constraints before assigning seats
3. **MRV Heuristic** - Prioritizes variables with minimum remaining values
4. **Constraint Propagation** - Reduces domain of variables as constraints are satisfied

### Constraint Types
| Constraint | Description |
|-----------|-------------|
| Hard Constraints | One student per seat, blocked seats, hall capacity |
| Subject Adjacency | Control seating of same-subject students |
| Gap Constraints | Minimum distance between same-subject students |

---

## 📊 Configuration Examples

### Student Data (CSV)
```csv
RollNo,Name,Branch
001,Rehan,CSE
002,Ravi,ECE
003,Priya,MECH
004,Amit,CSE
```

### Hall Configuration
```json
{
  "halls": [
    {
      "hallName": "H1-01",
      "rows": 6,
      "cols": 6,
      "blockedSeats": ["A3", "C4"]
    },
    {
      "hallName": "H1-02",
      "rows": 6,
      "cols": 5,
      "blockedSeats": ["B2"]
    }
  ]
}
```

---

## 📄 PDF Report Features

The generated PDF reports include:
- **Summary Page** - Overview of all halls and student statistics
- **Per-Hall Layout** - Detailed seating arrangement visualization
- **Statistics** - Registered, present, and absent student counts
- **Professional Format** - Exam branch branding and official signatures
- **Ready to Print** - Formatted for standard A4 paper

---

## 🐛 Troubleshooting

### Backend Issues
- **Port 5000 already in use:** Change port in `app.py` or kill existing process
- **Module not found errors:** Ensure virtual environment is activated and packages installed
- **CORS errors:** Verify Flask-CORS is installed (`pip install flask-cors`)

### Frontend Issues
- **Dependencies won't install:** Try `npm ci` instead of `npm install`
- **Port 5173 in use:** Vite will auto-increment to the next available port
- **API calls failing:** Ensure backend is running on `http://localhost:5000`

---

## 📈 Performance Considerations

- **Large datasets:** For 500+ students, CSP solver may take time; consider implementing timeout
- **Hall constraints:** More blocked seats reduce solution space; can improve performance
- **Branch distribution:** Uneven distribution may require longer solving time

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'Add your feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📝 License

This project is developed for academic and educational purposes.  
Developed at **CFAI, JNTU Hyderabad**

---

## 👨‍💼 Author

**Rehan Shaik**

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team
- Check existing documentation

---

## 📚 References

- [Constraint Satisfaction Problem (CSP)](https://en.wikipedia.org/wiki/Constraint_satisfaction_problem)
- [React Documentation](https://react.dev)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Vite Guide](https://vitejs.dev)
