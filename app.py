from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import os
from datetime import datetime
import json

app = Flask(__name__)

# Placeholder for model loading
def load_model():
    """
    Placeholder function for loading the ML model.
    To be replaced with actual model loading code later.
    """
    return None

# Placeholder for prediction
def predict_disorder(features):
    """
    Placeholder function for making predictions.
    To be replaced with actual model prediction code later.
    """
    # Simulate prediction probabilities
    disorders = ['MDD', 'NPD', 'SSD']
    probabilities = np.random.dirichlet(np.ones(3))
    prediction = disorders[np.argmax(probabilities)]
    
    return {
        'prediction': prediction,
        'probabilities': dict(zip(disorders, probabilities.tolist()))
    }

# Feature options
OCCUPATION_OPTIONS = [
    "business", "farmer", "housewife", "labor_service", "none", "other", "student"
]
EDUCATION_OPTIONS = [
    "1-8th", "9-12th", "graduate", "illiterate"
]
MARITAL_STATUS_OPTIONS = [
    "married", "unmarried", "no_information"
]
YES_NO_OPTIONS = ["yes", "no"]
BP_STATUS_OPTIONS = [
    "BP_Elevated", "BP_Healthy", "BP_Stage_1_Hypertension", "BP_Stage_2_Hypertension"
]

def encode_features(form):
    features = {}
    # Basic Information
    features['age'] = int(form.get('age', 0))
    features['gender'] = 1 if form.get('gender') == 'M' else 0
    features['address'] = form.get('address', '')
    
    # Occupation one-hot
    for occ in OCCUPATION_OPTIONS:
        features[occ] = 1 if form.get('occupation') == occ else 0
    
    # Education one-hot
    for edu in EDUCATION_OPTIONS:
        features[f'education_{edu}'] = 1 if form.get('education') == edu else 0
    
    # Marital Status one-hot
    for status in MARITAL_STATUS_OPTIONS:
        features[f'marital_status_{status}'] = 1 if form.get('marital_status') == status else 0
    
    # Binary Features (Yes/No)
    binary_features = [
        'diet', 'abnormal_behaviour', 'anxiety', 'appetite', 'body_pain',
        'crying', 'irrelevant_talks', 'fatiguability', 'generalized_weakness',
        'hallucination', 'headache', 'abnormal_body_movements', 'less_sleep',
        'low_mood', 'menstrual_problems', 'others', 'palpitation', 'phobia',
        'substance_use', 'suicidal_ideation', 'previous_illness_encoded',
        'family_history_encoded', 'physical_examination_encoded'
    ]
    
    for feature in binary_features:
        features[feature] = 1 if form.get(feature) == 'yes' else 0
    
    # Lab Tests
    lab_tests = [
        'lab_test_cbc', 'lft', 'kft', 'ecg', 'urine_r_m', 'lab_report_encoded'
    ]
    
    for test in lab_tests:
        features[test] = 1 if form.get(test) == 'yes' else 0
    
    # Blood Pressure Status one-hot
    for bp_status in BP_STATUS_OPTIONS:
        features[bp_status] = 1 if form.get('bp_status') == bp_status else 0
    
    return features

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home')
def home_redirect():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' in request.files:
            # Handle batch prediction
            file = request.files['file']
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                return jsonify({'error': 'Invalid file format'}), 400
            
            # Process each row
            predictions = []
            for _, row in df.iterrows():
                # Map row to form-like dict for encoding
                form = row.to_dict()
                features = encode_features(form)
                pred = predict_disorder(features)
                predictions.append(pred)
            
            # Save results to CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            results_df = pd.DataFrame(predictions)
            results_df.to_csv(f'static/results_{timestamp}.csv', index=False)
            
            return jsonify({
                'success': True,
                'predictions': predictions,
                'download_url': f'/download/{timestamp}'
            })
        else:
            # Handle single prediction
            form = request.form.to_dict()
            features = encode_features(form)
            prediction = predict_disorder(features)
            return jsonify({
                'success': True,
                'prediction': prediction
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<timestamp>')
def download_results(timestamp):
    try:
        return send_file(
            f'static/results_{timestamp}.csv',
            as_attachment=True,
            download_name=f'predictions_{timestamp}.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 