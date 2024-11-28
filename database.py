import json
from pathlib import Path
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
import streamlit as st
# Configure Google Sheets access
def get_google_sheet():
    """
    Authenticate and get access to the Google Sheet.
    Make sure to set up a service account and download the credentials JSON.
    """
    # Define the scope
    credentials_dict = st.secrets["google_sheets"]
        
    # Create credentials using the dictionary
    creds = Credentials.from_service_account_info(
        credentials_dict, 
        scopes=[
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
    )
    
    # Authorize and open spreadsheet
    client = gspread.authorize(creds)
    
    # Open the specific spreadsheet 
    sheet = client.open('ddhumanability').sheet1
    
    return sheet

def save_user_response(user_data):
    """Save user response to Google Sheets."""
    # Calculate accuracy
    correct_answers = calculate_accuracy(user_data['responses'])
    user_data['accuracy'] = correct_answers / len(user_data['responses'])
    
    # Calculate familiarity score
    noofyes = count_familiarity(user_data['familiarity'])
    user_data['fam_score'] = noofyes / len(user_data['familiarity'])
    
    # Calculate additional metrics
    withAudio = calculate_with_audio(user_data['responses'])
    images = calculate_images(user_data['responses'])
    withoutAudio = calculate_without_audio(user_data['responses'])
    
    user_data['withAudio'] = withAudio
    user_data['withoutAudio'] = withoutAudio
    user_data['images'] = images
    
    # Get the Google Sheet
    sheet = get_google_sheet()
    
    # Prepare the row to be added
    row_to_add = [
        user_data.get('name', ''),
        user_data.get('age', ''),
        user_data.get('gender', ''),
        user_data.get('social_media_hours', ''),
        json.dumps(user_data.get('responses', [])),
        json.dumps(user_data.get('familiarity', [])),
        user_data.get('accuracy', ''),
        user_data.get('fam_score', ''),
        user_data.get('withAudio', ''),
        user_data.get('withoutAudio', ''),
        user_data.get('images', '')
    ]
    
    # Append the row to the end of the sheet
    try:
        sheet.append_row(row_to_add, value_input_option='RAW')
        print("Response saved successfully.")
    except Exception as e:
        print(f"Error saving response: {e}")


def load_all_responses():
    """Load all responses from Google Sheets into a pandas DataFrame."""
    sheet = get_google_sheet()
    
    # Get all values from the sheet
    all_data = sheet.get_all_values()
    
    # The first row is assumed to be the header
    headers = all_data[0]
    
    # The rest are data rows
    data_rows = all_data[1:]
    
    # Create a DataFrame
    df = pd.DataFrame(data_rows, columns=headers)
    
    # Parse JSON columns if they exist
    if 'responses' in df.columns:
        df['responses'] = df['responses'].apply(json.loads)
    if 'familiarity' in df.columns:
        df['familiarity'] = df['familiarity'].apply(json.loads)
    
    return df


# The rest of the functions remain the same as in the original script
def calculate_without_audio(responses):
    correct_pairs = 0
    
    # Iterate through pairs (1-2, 3-4, 5-6, etc.)
    for i in range(1+40, 17+40, 2):
        pair_key1 = f'Video {i}'
        pair_key2 = f'Video {i+1}'
        
        # Odd-numbered videos (1, 3, 5, ...) should be real
        # Even-numbered videos (2, 4, 6, ...) should be fake
        is_odd_real = pair_key1 not in responses
        is_even_fake = pair_key2 in responses
        
        if is_odd_real and is_even_fake:
            correct_pairs += 1
    
    return correct_pairs/8

def calculate_images(responses):
    correct_pairs = 0
    for i in range(1, 41, 2):
        pair_key1 = f'Image {i}'
        pair_key2 = f'Image {i+1}'
        
        # Odd-numbered images (1, 3, 5, ...) should be real
        # Even-numbered images (2, 4, 6, ...) should be fake
        is_odd_real = pair_key1 not in responses
        is_even_fake = pair_key2 in responses
        
        if is_odd_real and is_even_fake:
            correct_pairs += 1
    
    return correct_pairs/20

def calculate_with_audio(responses):
    correct_pairs = 0
    
    # Iterate through pairs (1-2, 3-4, 5-6, etc.)
    for i in range(1+56, 17+56, 2):
        pair_key1 = f'Video {i}'
        pair_key2 = f'Video {i+1}'
        
        # Odd-numbered videos (1, 3, 5, ...) should be real
        # Even-numbered videos (2, 4, 6, ...) should be fake
        is_odd_real = pair_key1 not in responses
        is_even_fake = pair_key2 in responses
        
        if is_odd_real and is_even_fake:
            correct_pairs += 1
    
    return correct_pairs/8

def count_familiarity(responses):
    count = 0
    for response in responses:
        if response == 'Yes':
            count += 1
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
    for i in range(1, 41):
        ground_truth[f'Image {i}'] = 1 if i % 2 == 0 else 0
    
    # Add 15 video pairs without audio
    for i in range(1+40, 17+40):
        ground_truth[f'Video {i}'] = 1 if i % 2 == 0 else 0
    
    # Add 10 video pairs with audio
    for i in range(57, 57+1):
        ground_truth[f'Video {i}'] = 1 if i % 2 == 0 else 0
    
    # Calculate correct responses
    correct = 0
    for response, (key, truth) in zip(responses, ground_truth.items()):
        # Extract the predicted label from the response string
        # Assumes response is in format like "Image 1: 1" or "Video 2: 0"
        predicted_label = int(response.split()[-1])
        
        if predicted_label % 2 == 0:
            correct += 1
    
    return correct