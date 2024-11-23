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
    noofyes=count_familiarity(user_data['familiarity'])
    user_data['fam_score']=noofyes/len(user_data['familiarity'])
    # user_data['familiarity']=countofyes/len(user_data['familiarity'])
    
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
def count_familiarity(responses):
    count=0
    for i in range(len(responses)):
        if responses[i]=='Yes':
            count=count+1
    return count
def calculate_accuracy(responses):
    """Calculate number of correct responses based on ground truth."""
    # Replace this with actual ground truth for your media pairs
    ground_truth = {}

# Add 25 images
    for i in range(1, 26):
        ground_truth[f'Image {i}'] = 1

    # Add 15 videos
    for i in range(1, 16):
        ground_truth[f'Video {i}'] = 1

    # Add 10 audio videos
    for i in range(1, 11):
        ground_truth[f'Audio Video {i}'] = 1
    
    correct = 0
    for response, truth in zip(responses, ground_truth.values()):
        if int(response.split()[-1]) == truth:
            correct += 1
            
    return correct