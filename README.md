
# Pharmacy Safety System

**Status:** Functional prototype with full system design documentation  
**Goal:** Reduce pharmacy dispensing errors by providing an automated prescription validation and decision-support tool.  

---

## Overview
The Pharmacy Safety System is a **Flask-based prototype web application** backed by detailed system design and modeling.  
It supports pharmacists by automatically validating prescriptions against multiple safety and compliance checks, helping to reduce risks of:  
- Drug interactions  
- Duplicate dosages  
- Invalid or fraudulent prescriptions  
- Insurance and identity mismatches  
- Regulatory alerts and shortages  

The system provides pharmacists with clear decision support while maintaining final control over approval.  

---

## Features

- **Prescription Workflow**  
  - View pending, in-progress, and completed prescriptions  
  - Process prescriptions step by step with automated checks  

- **Automated Validation**  
  - Patient insurance verification  
  - Physician credential validation  
  - Inventory and stock availability check  
  - Drug interaction and safety alerts  
  - Regulatory alerts (e.g., shortages, outbreak-related demand)  
  - Patient medical history and allergy checks  

- **Decision Support Dashboard**  
  - Displays results of each check (green = safe, yellow = caution, red = critical)  
  - Allows pharmacists to approve, reject, or override with comments  

- **Audit & Logging**  
  - Every decision is logged for traceability and accountability  

---

## Architecture & Design
This project was initially developed as a **software architecture case study** and extended into a working prototype.  
It includes full design documentation:  

- **Data Flow Diagrams (DFD)** – Level 1–3 decomposition of the prescription process  
- **Entity & Data Dictionaries** – Six interconnected databases:  
  - Drug Inventory  
  - Prescription History  
  - Drug Interactions  
  - Patient Records  
  - Order Analytics  
  - Electronic Prescriptions  
- **Use Case Diagrams & Pseudocode** – Detailed workflows for validation, doctor verification, conflict resolution  
- **UML & Sequence Diagrams** – Modeling system logic and interactions  
- **Prototype Implementation** – Flask web app, SQLite backend, Bootstrap frontend  

---

## Technologies
- **Backend:** Python (Flask)  
- **Database:** SQLite (schema supports migration to PostgreSQL/MySQL)  
- **Frontend:** HTML, CSS (Bootstrap), JavaScript  
- **Documentation:** UML, DFD, use cases, sequence diagrams  

---

## Getting Started

### 1. Clone Repository
```bash
git clone https://github.com/IgorD-lab/Pharmacy.git
cd Pharmacy
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Development Server

```bash
python app.py
```

Visit: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## Screens & Workflow

* **Login Page** – Secure access for pharmacists
* **Dashboard** – View pending, approved, and rejected prescriptions
* **Processing View** – Step-by-step validation results (insurance, doctor, inventory, safety)
* **Alert Handling** – Clear warnings (yellow = caution, red = critical)
* **Decision & Logging** – Approve, reject, or override with mandatory comment

---

## Future Improvements

* UI refinements (simplify prescription processing view)
* Real-time notifications (new prescriptions, failed checks)
* Integration with external medical databases for advanced drug interaction checks
* Detailed audit trail with timestamps for regulatory compliance
* Responsive design for tablets/mobile devices

---

## Documentation

Full design documentation is included in the repo:

* [System Design Document (Apoteka.docx)](Apoteka.docx)

This covers DFDs, UML diagrams, database schemas, and detailed process logic.

---

## Disclaimer

This project is a **research prototype** and not intended for production medical use.
It demonstrates system design, architecture, and proof-of-concept implementation for academic and portfolio purposes.
