from flask import Flask, request, render_template
import numpy as np
import pandas as pd
import pickle
from difflib import get_close_matches
import os
import logging
from pathlib import Path
from flask_wtf.csrf import CSRFProtect

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24).hex()
csrf = CSRFProtect(app)

# Get the absolute path to the current directory
BASE_DIR = Path(__file__).resolve().parent
logger.info(f"Base directory: {BASE_DIR}")

# Define paths to datasets and models
def get_path(relative_path):
    """Get absolute path from relative path"""
    path = BASE_DIR / relative_path
    logger.info(f"Resolved path: {path}")
    return path

# Load datasets
try:
    logger.info("Loading datasets...")
    sym_des = pd.read_csv(get_path("datasets/symtoms_df.csv"))
    precautions_df = pd.read_csv(get_path("datasets/precautions_df.csv"))
    workout_df = pd.read_csv(get_path("datasets/workout_df.csv"))
    description_df = pd.read_csv(get_path("datasets/description.csv"))
    medications_df = pd.read_csv(get_path('datasets/medications.csv'))
    diets_df = pd.read_csv(get_path("datasets/diets.csv"))
    logger.info("Successfully loaded all datasets")
except Exception as e:
    logger.error(f"Error loading datasets: {str(e)}")
    datasets_dir = get_path("datasets")
    if datasets_dir.exists():
        logger.error(f"Files in datasets directory: {os.listdir(datasets_dir)}")
    else:
        logger.error(f"Datasets directory does not exist: {datasets_dir}")
    raise

# Load model
try:
    logger.info("Loading model...")
    with open(get_path('models/svc.pkl'), 'rb') as f:
        svc = pickle.load(f)
    logger.info("Successfully loaded the model")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    models_dir = get_path("models")
    if models_dir.exists():
        logger.error(f"Files in models directory: {os.listdir(models_dir)}")
    else:
        logger.error(f"Models directory does not exist: {models_dir}")
    raise

# =========== DEFINE SYMPTOMS DICTIONARY ===========
symptoms_dict = {'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61, 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75, 'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131}
diseases_list = {15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction', 33: 'Peptic ulcer diseae', 1: 'AIDS', 12: 'Diabetes ', 17: 'Gastroenteritis', 6: 'Bronchial Asthma', 23: 'Hypertension ', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A', 19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack', 39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 31: 'Osteoarthristis', 5: 'Arthritis', 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne', 38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'}

# Create list of predictable diseases
predictable_diseases = sorted(list(set(diseases_list.values())))
medicine_diseases = medications_df['Disease'].str.strip().str.title().unique()
all_diseases = sorted(list(set(predictable_diseases) | set(medicine_diseases)))

# Create list of recognizable symptoms
recognizable_symptoms = sorted(list(symptoms_dict.keys()))

# =========== CREATE NORMALIZED SYMPTOM DICTIONARY ===========
normalized_symptoms = {symptom.lower().replace(' ', '_'): symptom for symptom in symptoms_dict}

# Context processor for global template variables
@app.context_processor
def inject_global_data():
    return dict(normalized_symptoms=normalized_symptoms)

# Helper function
def helper(dis):
    try:
        # Description
        desc = description_df[description_df['Disease'] == dis]['Description']
        desc = desc.iloc[0] if not desc.empty else "Description not available"
        
        # Precautions
        pre = precautions_df[precautions_df['Disease'] == dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
        pre = pre.values.tolist()[0] if not pre.empty else ["No precautions available"]
        
        # Medications
        med = medications_df[medications_df['Disease'] == dis]['Medication']
        med = med.tolist() if not med.empty else ["No medications recommended"]
        
        # Diets
        die = diets_df[diets_df['Disease'] == dis]['Diet']
        die = die.tolist() if not die.empty else ["No specific diet recommendations"]
        
        # Workouts
        wrkout = workout_df[workout_df['disease'] == dis]['workout']
        wrkout = wrkout.tolist() if not wrkout.empty else ["No specific workout recommendations"]

        return desc, pre, med, die, wrkout
    except Exception as e:
        logger.error(f"Error in helper function: {str(e)}")
        return (
            "Description not available",
            ["No precautions available"],
            ["No medications recommended"],
            ["No specific diet recommendations"],
            ["No specific workout recommendations"]
        )

# Model Prediction function
def get_predicted_value(patient_symptoms):
    try:
        input_vector = np.zeros(len(symptoms_dict))
        for item in patient_symptoms:
            if item in symptoms_dict:
                input_vector[symptoms_dict[item]] = 1
        return diseases_list[svc.predict([input_vector])[0]]
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return None

# Validate symptoms
def validate_symptoms(user_input):
    try:
        valid = []
        invalid = []
        suggestions = {}
        
        # Clean and normalize input
        cleaned = [s.strip().lower().replace(' ', '_') for s in user_input.split(',') if s.strip()]
        
        for symptom in cleaned:
            # Check if normalized symptom exists
            if symptom in normalized_symptoms:
                valid.append(normalized_symptoms[symptom])
                continue
            
            # Find close matches
            close_matches = get_close_matches(symptom, normalized_symptoms.keys(), n=3, cutoff=0.6)
            
            if close_matches:
                original_matches = [normalized_symptoms[m] for m in close_matches]
                suggestions[symptom] = original_matches
                invalid.append(symptom)
            else:
                invalid.append(symptom)
        
        return valid, invalid, suggestions
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return [], [user_input], {}

# Routes
@app.route("/")
def root():
    return render_template("index.html", predictable_diseases=predictable_diseases, all_diseases=all_diseases, recognizable_symptoms=recognizable_symptoms)

@app.route("/index")
def index():
    return render_template("index.html", predictable_diseases=predictable_diseases, all_diseases=all_diseases, recognizable_symptoms=recognizable_symptoms)

@app.route('/predict', methods=['POST'])
def home():
    symptoms = request.form.get('symptoms', '').strip()
    
    if not symptoms or symptoms.lower() == "symptoms":
        return render_template('index.html', 
                              message="Please enter your symptoms. Example: headache, fever, nausea",
                              predictable_diseases=predictable_diseases)
    
    valid, invalid, suggestions = validate_symptoms(symptoms)
    
    if invalid:
        error_message = "Invalid symptoms detected:"
        for symptom in invalid:
            if symptom in suggestions:
                error_message += f"<br>• <strong>{symptom}</strong> (did you mean: {', '.join(suggestions[symptom])}?)"
            else:
                error_message += f"<br>• <strong>{symptom}</strong> (no similar symptoms found)"
        error_message += "<br>Please correct your input and try again."
        return render_template('index.html', 
                              message=error_message,
                              predictable_diseases=predictable_diseases)
    
    if not valid:
        return render_template('index.html', 
                              message="No valid symptoms recognized. Please check your input and try again.",
                              predictable_diseases=predictable_diseases)
    
    try:
        predicted_disease = get_predicted_value(valid)
        if not predicted_disease:
            raise ValueError("Prediction failed")
            
        dis_des, precautions_list, medications_list, rec_diet, workout_list = helper(predicted_disease)
        
        return render_template('index.html', 
                              predicted_disease=predicted_disease, 
                              dis_des=dis_des,
                              my_precautions=precautions_list, 
                              medications=medications_list, 
                              my_diet=rec_diet,
                              workout_list=workout_list,
                              predictable_diseases=predictable_diseases)
    except Exception as e:
        logger.error(f"Full prediction error: {str(e)}")
        return render_template('index.html', 
                              message=f"System error: {str(e)}",
                              predictable_diseases=predictable_diseases)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 