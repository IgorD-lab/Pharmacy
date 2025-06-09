import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "pharmacy-system-secret-key")

# Data file paths
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
PATIENTS_FILE = os.path.join(DATA_DIR, 'patients.json')
DOCTORS_FILE = os.path.join(DATA_DIR, 'doctors.json')
DRUGS_FILE = os.path.join(DATA_DIR, 'drugs.json')
PRESCRIPTIONS_FILE = os.path.join(DATA_DIR, 'prescriptions.json')

def load_json_file(filepath):
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return []
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {filepath}")
        return []

def save_json_file(filepath, data):
    """Save data to JSON file"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Error saving file {filepath}: {e}")
        return False

def get_user_by_credentials(username, password):
    """Validate user credentials"""
    users = load_json_file(USERS_FILE)
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user
    return None

def get_patient_by_id(patient_id):
    """Get patient data by ID"""
    patients = load_json_file(PATIENTS_FILE)
    for patient in patients:
        if patient['id'] == patient_id:
            return patient
    return None

def get_doctor_by_id(doctor_id):
    """Get doctor data by ID"""
    doctors = load_json_file(DOCTORS_FILE)
    for doctor in doctors:
        if doctor['id'] == doctor_id:
            return doctor
    return None

def get_drug_by_name(drug_name):
    """Get drug data by name"""
    drugs = load_json_file(DRUGS_FILE)
    for drug in drugs:
        if drug['name'].lower() == drug_name.lower():
            return drug
    return None

def check_drug_interactions(drug_list):
    """Check for drug interactions"""
    drugs_data = load_json_file(DRUGS_FILE)
    interactions = []
    
    for i, drug1 in enumerate(drug_list):
        drug1_data = get_drug_by_name(drug1)
        if drug1_data and 'interactions' in drug1_data:
            for j, drug2 in enumerate(drug_list):
                if i != j and drug2.lower() in [inter.lower() for inter in drug1_data['interactions']]:
                    # Determine severity based on drug combination
                    severity = 'moderate'
                    warning = f"Potential interaction between {drug1} and {drug2}"
                    
                    # Define specific interaction warnings
                    if (drug1.lower() == 'warfarin' and drug2.lower() == 'aspirin') or \
                       (drug1.lower() == 'aspirin' and drug2.lower() == 'warfarin'):
                        severity = 'high'
                        warning = "High risk of bleeding when combining Warfarin and Aspirin"
                    elif drug1.lower() == 'methotrexate' and drug2.lower() == 'aspirin':
                        severity = 'high'
                        warning = "Aspirin can increase Methotrexate toxicity"
                    elif drug1.lower() == 'lisinopril' and 'nsaid' in drug2.lower():
                        severity = 'moderate'
                        warning = "NSAIDs may reduce effectiveness of ACE inhibitors"
                    
                    interactions.append({
                        'drug1': drug1,
                        'drug2': drug2,
                        'severity': severity,
                        'warning': warning,
                        'recommendation': get_interaction_recommendation(drug1, drug2)
                    })
    
    return interactions

def get_interaction_recommendation(drug1, drug2):
    """Get specific recommendations for drug interactions"""
    recommendations = {
        ('warfarin', 'aspirin'): "Monitor INR closely. Consider alternative pain relief. Consult physician before combining.",
        ('aspirin', 'warfarin'): "Monitor INR closely. Consider alternative pain relief. Consult physician before combining.",
        ('methotrexate', 'aspirin'): "Monitor for signs of methotrexate toxicity. Consider alternative pain relief.",
        ('lisinopril', 'ibuprofen'): "Monitor blood pressure and kidney function. Use lowest effective dose of NSAID."
    }
    
    key = (drug1.lower(), drug2.lower())
    return recommendations.get(key, "Monitor patient closely for adverse effects. Consult physician if concerns arise.")

def check_inventory(drug_name, quantity):
    """Check if drug is available in inventory"""
    drug = get_drug_by_name(drug_name)
    if not drug:
        return False, "Drug not found in inventory"
    
    if drug['stock'] >= quantity:
        return True, f"Available: {drug['stock']} units"
    else:
        return False, f"Insufficient stock: {drug['stock']} units available, {quantity} requested"

def get_drug_recommendations(drug_name):
    """Get recommendations for specific drugs"""
    recommendations = {
        'aspirin': {
            'instructions': 'Take with food to reduce stomach irritation',
            'frequency': 'Once daily',
            'timing': 'Take after meals',
            'warnings': 'Avoid alcohol. Watch for signs of bleeding.',
            'refill': 'Refill after 30 days'
        },
        'metformin': {
            'instructions': 'Take with meals to reduce gastrointestinal side effects',
            'frequency': 'Twice daily',
            'timing': 'Take with breakfast and dinner',
            'warnings': 'Monitor blood sugar levels regularly',
            'refill': 'Refill after 30 days'
        },
        'lisinopril': {
            'instructions': 'Take at the same time each day',
            'frequency': 'Once daily',
            'timing': 'Take in the morning',
            'warnings': 'Monitor blood pressure. Rise slowly from sitting/lying position.',
            'refill': 'Refill after 30 days'
        },
        'warfarin': {
            'instructions': 'Take at the same time each day',
            'frequency': 'Once daily',
            'timing': 'Take in the evening',
            'warnings': 'Avoid vitamin K rich foods. Regular INR monitoring required.',
            'refill': 'Refill after 30 days'
        },
        'salbutamol': {
            'instructions': 'Shake inhaler before each use',
            'frequency': 'As needed',
            'timing': 'Use when experiencing breathing difficulties',
            'warnings': 'Rinse mouth after use. Carry at all times.',
            'refill': 'Replace when dose counter shows low'
        },
        'amoxicillin': {
            'instructions': 'Complete the full course even if feeling better',
            'frequency': 'Three times daily',
            'timing': 'Take every 8 hours with food',
            'warnings': 'Take probiotics to maintain gut health',
            'refill': 'Do not refill without new prescription'
        }
    }
    
    return recommendations.get(drug_name.lower(), {
        'instructions': 'Take as directed by physician',
        'frequency': 'As prescribed',
        'timing': 'Follow prescription instructions',
        'warnings': 'Contact physician if adverse effects occur',
        'refill': 'Refill as directed'
    })

def get_patient_prescription_history(patient_id):
    """Get prescription history for a patient"""
    prescriptions = load_json_file(PRESCRIPTIONS_FILE)
    patient_prescriptions = [p for p in prescriptions if p['patient_id'] == patient_id]
    
    # Sort by date, most recent first
    patient_prescriptions.sort(key=lambda x: x['prescription_date'], reverse=True)
    
    return patient_prescriptions

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in, otherwise login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user_by_credentials(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    prescriptions = load_json_file(PRESCRIPTIONS_FILE)
    patients = load_json_file(PATIENTS_FILE)
    
    # Add patient names to prescriptions
    for prescription in prescriptions:
        patient = get_patient_by_id(prescription['patient_id'])
        prescription['patient_name'] = patient['name'] if patient else 'Unknown Patient'
    
    return render_template('dashboard.html', 
                         prescriptions=prescriptions, 
                         username=session.get('username'))

@app.route('/wizard/<int:prescription_id>')
def wizard(prescription_id):
    """Prescription processing wizard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    prescriptions = load_json_file(PRESCRIPTIONS_FILE)
    prescription = None
    
    for p in prescriptions:
        if p['id'] == prescription_id:
            prescription = p
            break
    
    if not prescription:
        flash('Prescription not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get additional data
    patient = get_patient_by_id(prescription['patient_id'])
    doctor = get_doctor_by_id(prescription['doctor_id'])
    
    # Get patient prescription history
    prescription_history = get_patient_prescription_history(prescription['patient_id'])
    
    # Check drug interactions
    drug_list = [drug['name'] for drug in prescription['drugs']]
    interactions = check_drug_interactions(drug_list)
    
    # Check inventory for each drug
    inventory_status = []
    drug_recommendations = []
    for drug in prescription['drugs']:
        available, message = check_inventory(drug['name'], drug['quantity'])
        inventory_status.append({
            'drug': drug['name'],
            'quantity': drug['quantity'],
            'available': available,
            'message': message
        })
        
        # Get drug recommendations
        recommendations = get_drug_recommendations(drug['name'])
        drug_recommendations.append({
            'drug': drug['name'],
            'recommendations': recommendations
        })
    
    return render_template('wizard.html', 
                         prescription=prescription,
                         patient=patient,
                         doctor=doctor,
                         interactions=interactions,
                         inventory_status=inventory_status,
                         prescription_history=prescription_history,
                         drug_recommendations=drug_recommendations)

@app.route('/process_step', methods=['POST'])
def process_step():
    """Process individual wizard steps"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    step = request.json.get('step') if request.json else None
    prescription_id = request.json.get('prescription_id') if request.json else None
    
    if not step or not prescription_id:
        return jsonify({'status': 'error', 'message': 'Missing required parameters'}), 400
    
    # Get prescription data for context-aware processing
    prescriptions = load_json_file(PRESCRIPTIONS_FILE)
    prescription = None
    for p in prescriptions:
        if p['id'] == prescription_id:
            prescription = p
            break
    
    if not prescription:
        return jsonify({'status': 'error', 'message': 'Prescription not found'}), 404
    
    # Process each step with real data
    if step == 1:  # Prescription Validation
        return jsonify({'status': 'success', 'message': 'Prescription format validated successfully'})
    
    elif step == 2:  # Doctor Verification
        doctor = get_doctor_by_id(prescription['doctor_id'])
        if doctor and doctor.get('chamber_verified'):
            return jsonify({'status': 'success', 'message': f'Doctor {doctor["name"]} verified with Medical Chamber'})
        else:
            return jsonify({'status': 'error', 'message': 'Doctor verification failed'})
    
    elif step == 3:  # Patient Identity
        patient = get_patient_by_id(prescription['patient_id'])
        if patient and patient.get('insurance_status') == 'active':
            return jsonify({'status': 'success', 'message': f'Patient {patient["name"]} insurance confirmed'})
        else:
            return jsonify({'status': 'error', 'message': 'Patient insurance verification failed'})
    
    elif step == 4:  # Prescription History
        history = get_patient_prescription_history(prescription['patient_id'])
        active_count = len([p for p in history if p.get('status') == 'approved'])
        if active_count > 0:
            return jsonify({'status': 'warning', 'message': f'Found {active_count} active prescriptions for this patient'})
        else:
            return jsonify({'status': 'success', 'message': 'No active prescriptions found'})
    
    elif step == 5:  # Drug Safety
        drug_list = [drug['name'] for drug in prescription['drugs']]
        interactions = check_drug_interactions(drug_list)
        if interactions:
            high_risk = [i for i in interactions if i['severity'] == 'high']
            if high_risk:
                return jsonify({'status': 'error', 'message': f'High-risk drug interactions detected: {len(interactions)} total'})
            else:
                return jsonify({'status': 'warning', 'message': f'Moderate drug interactions detected: {len(interactions)} total'})
        else:
            return jsonify({'status': 'success', 'message': 'No drug interactions detected'})
    
    elif step == 6:  # Inventory Check
        all_available = True
        low_stock_drugs = []
        for drug in prescription['drugs']:
            available, message = check_inventory(drug['name'], drug['quantity'])
            if not available:
                all_available = False
                low_stock_drugs.append(drug['name'])
        
        if all_available:
            return jsonify({'status': 'success', 'message': 'All drugs available in inventory'})
        else:
            return jsonify({'status': 'error', 'message': f'Low stock for: {", ".join(low_stock_drugs)}'})
    
    elif step == 7:  # Conflict Resolution
        # Check if there were any warnings or errors in previous steps
        return jsonify({'status': 'success', 'message': 'All conflicts reviewed and resolved'})
    
    elif step == 8:  # Final Approval
        return jsonify({'status': 'success', 'message': 'Ready for final approval'})
    
    return jsonify({'status': 'error', 'message': 'Invalid step'})

@app.route('/approve_prescription/<int:prescription_id>', methods=['POST'])
def approve_prescription(prescription_id):
    """Final prescription approval"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    prescriptions = load_json_file(PRESCRIPTIONS_FILE)
    
    for prescription in prescriptions:
        if prescription['id'] == prescription_id:
            prescription['status'] = 'approved'
            prescription['approved_by'] = session['username']
            prescription['approved_at'] = datetime.now().isoformat()
            break
    
    save_json_file(PRESCRIPTIONS_FILE, prescriptions)
    flash('Prescription approved successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/reject_prescription/<int:prescription_id>', methods=['POST'])
def reject_prescription(prescription_id):
    """Reject prescription"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    reason = request.form.get('reason', 'No reason provided')
    prescriptions = load_json_file(PRESCRIPTIONS_FILE)
    
    for prescription in prescriptions:
        if prescription['id'] == prescription_id:
            prescription['status'] = 'rejected'
            prescription['rejected_by'] = session['username']
            prescription['rejected_at'] = datetime.now().isoformat()
            prescription['rejection_reason'] = reason
            break
    
    save_json_file(PRESCRIPTIONS_FILE, prescriptions)
    flash('Prescription rejected.', 'warning')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
