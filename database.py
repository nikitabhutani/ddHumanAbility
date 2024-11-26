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
    withAudio=calculate_with_audio(user_data['responses'])
    images=calculate_images(user_data['responses'])
    withoutAudio=calculate_without_audio(user_data['responses'])
    user_data['withAudio']=withAudio
    user_data['withoutAudio']=withoutAudio
    user_data['images']=images
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
def calculate_without_audio(responses):
    correct_pairs = 0
    
    # Iterate through pairs (1-2, 3-4, 5-6, etc.)
    for i in range(1+50, 31+50, 2):
        pair_key1 = f'Video {i}'
        pair_key2 = f'Video {i+1}'
        
        # Odd-numbered videos (1, 3, 5, ...) should be real
        # Even-numbered videos (2, 4, 6, ...) should be fake
        is_odd_real = pair_key1 in responses
        is_even_fake = pair_key2 not in responses
        
        if is_odd_real and is_even_fake:
            correct_pairs += 1
    
    return correct_pairs
def calculate_images(responses):
    correct_pairs=0
    for i in range(1, 51, 2):
        pair_key1 = f'Image {i}'
        pair_key2 = f'Image {i+1}'
        
        # Odd-numbered images (1, 3, 5, ...) should be real
        # Even-numbered images (2, 4, 6, ...) should be fake
        is_odd_real = pair_key1 in responses
        is_even_fake = pair_key2 not in responses
        
        if is_odd_real and is_even_fake:
            correct_pairs += 1
    
    return correct_pairs
def calculate_with_audio(responses):
    correct_pairs = 0
    
    # Iterate through pairs (1-2, 3-4, 5-6, etc.)
    for i in range(1+80, 21+80, 2):
        pair_key1 = f'Video {i}'
        pair_key2 = f'Video {i+1}'
        
        # Odd-numbered videos (1, 3, 5, ...) should be real
        # Even-numbered videos (2, 4, 6, ...) should be fake
        is_odd_real = pair_key1 in responses
        is_even_fake = pair_key2 not in responses
        
        if is_odd_real and is_even_fake:
            correct_pairs += 1
    
    return correct_pairs
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
    """
    Calculate number of correct responses based on ground truth.
    
    Ground truth rules:
    - 25 image pairs: Odd-numbered images are real (1), even-numbered images are fake (0)
    - 15 video pairs without audio: Odd-numbered videos are real (1), even-numbered videos are fake (0)
    - 10 videos with audio: Odd-numbered videos are real (1), even-numbered videos are fake (0)
    
    Args:
    responses (list): List of response strings indicating the predicted label
    
    Returns:
    int: Number of correct responses
    """
    # Create ground truth dictionary
    ground_truth = {}
    
    # Add 25 image pairs
    for i in range(1, 51):
        ground_truth[f'Image {i}'] = 1 if i % 2 != 0 else 0
    
    # Add 15 video pairs without audio
    for i in range(1+50, 31+50):
        ground_truth[f'Video {i}'] = 1 if i % 2 != 0 else 0
    
    # Add 10 video pairs with audio
    for i in range(81, 101):
        ground_truth[f'Video {i}'] = 1 if i % 2 != 0 else 0
    
    # Calculate correct responses
    correct = 0
    for response, (key, truth) in zip(responses, ground_truth.items()):
        # Extract the predicted label from the response string
        # Assumes response is in format like "Image 1: 1" or "Video 2: 0"
        predicted_label = int(response.split()[-1])
        
        if predicted_label%2==1 :
            correct+=1
    
    return correct