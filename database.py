# database.py
import json
from pathlib import Path
import pandas as pd

DB_PATH = Path('data/responses.json')

def save_user_response(user_data):
    """Save user response to JSON database."""
    # Calculate accuracy
    correct_answers = calculate_accuracy(user_data['responses'])
    user_data['accuracy'] = correct_answers / len(user_data['responses'])
    
    # Load existing responses
    if DB_PATH.exists():
        with open(DB_PATH, 'r') as f:
            responses = json.load(f)
    else:
        responses = []
    
    # Add new response
    responses.append(user_data)
    
    # Save updated responses
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, 'w') as f:
        json.dump(responses, f)

def load_all_responses():
    """Load all responses from JSON database into a pandas DataFrame."""
    if not DB_PATH.exists():
        return pd.DataFrame()
        
    with open(DB_PATH, 'r') as f:
        responses = json.load(f)
    
    return pd.DataFrame(responses)

def calculate_accuracy(responses):
    """Calculate number of correct responses based on ground truth."""
    # Replace this with actual ground truth for your media pairs
    ground_truth = {
        'Image 1': 2,
        'Image 2': 1,
        'Image 3': 2,
        'Video 1': 2,
        'Video 2': 1,
        'Audio Video 1': 2,
        'Audio Video 2': 1
    }
    
    correct = 0
    for response, truth in zip(responses, ground_truth.values()):
        if int(response.split()[-1]) == truth:
            correct += 1
            
    return correct