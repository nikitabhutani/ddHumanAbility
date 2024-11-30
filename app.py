# app.py
import statistics
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from analysis import perform_bayesian_analysis
from database import save_user_response, load_all_responses
import matplotlib.pyplot as plt
def load_media_paths():
    """Load paths to deepfake and real media files."""
    # Replace these paths with your actual dataset paths
    media_config = {
        'images': {
            'real': sorted(Path('data/celeb-df/real/images').glob('*.jpg')),
            'fake': sorted(Path('data/celeb-df/fake/images').glob('*.jpg'))
        },
        'videos': {
            'no_audio': {
                'real': sorted(Path('data/celeb-df/real/videos').glob('*.mp4')),
                'fake': sorted(Path('data/celeb-df/fake/videos').glob('*.mp4'))
            },
            'with_audio': {
                'real': sorted(Path('data/audio_dataset/real').glob('*.mp4')),
                'fake': sorted(Path('data/audio_dataset/fake').glob('*.mp4'))
            }
        }
    }
    return media_config

def main():
    st.set_page_config(page_title="Can you detect a deepfake?", layout="wide")
    st.title("How good are you in Detecting Deepfakes?")

    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'form'
    
    # User Information Form
    if st.session_state.page == 'form':
        with st.form("user_info"):
            st.header("Please provide your information")
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=18, max_value=100)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
            st.subheader("Social Media Usage (hours per day)")
            facebook = st.number_input("Facebook", min_value=0.0, max_value=24.0, step=0.5)
            instagram = st.number_input("Instagram", min_value=0.0, max_value=24.0, step=0.5)
            twitter = st.number_input("Twitter", min_value=0.0, max_value=24.0, step=0.5)
            tiktok = st.number_input("TikTok", min_value=0.0, max_value=24.0, step=0.5)
            
            if st.form_submit_button("Start Test"):
                st.session_state.user_data = {
                    'name': name,
                    'age': age,
                    'gender': gender,
                    'social_media_hours': facebook + instagram + twitter + tiktok
                }
                st.session_state.page = 'test'
                st.rerun()

    # Media Test Page
    elif st.session_state.page == 'test':
        media_config = load_media_paths()
        st.header("Deepfake Detection Test")
        
        with st.form("detection_test"):
            responses = []
            familiarity=[]
           
            # Display Images
            st.subheader("Image Analysis")
            for i, (real_img, fake_img) in enumerate(zip(
                media_config['images']['real'][:20], 
                media_config['images']['fake'][:20]
            )):
                col1, col2 = st.columns(2)
                with col1:
                    st.image(str(real_img), caption=f"Image {i*2 + 1}")
                    fam1=st.radio(
                    f"do you know person in image {i*2+1} (Pair {i+1})",
                    [f"No", f"Yes"]
                )
                with col2:
                    st.image(str(fake_img), caption=f"Image {i*2 + 2}")
                    fam2=st.radio(
                    f"do you know person in image {i*2+2} (Pair {i+1})",
                    [f"No", f"Yes"]
                )
               
                
                response = st.radio(
                    f"Which image do you think is fake? (Pair {i+1})",
                    [f"Image {i*2 + 1}", f"Image {i*2 + 2}"]
                )
                responses.append(response)
                familiarity.append(fam1)
                familiarity.append(fam2)
            # Display Videos
            st.subheader("Video Analysis")
            for i, (real_video, fake_video) in enumerate(zip(
                media_config['videos']['no_audio']['real'][:8],
                media_config['videos']['no_audio']['fake'][:8]
            )):
                col1, col2 = st.columns(2)
                with col1:
                    st.video(str(real_video))
                    fam1=st.radio(
                    f"do you know person in video {2*i+1} (Pair {i+1})",
                    [f"No", f"Yes"]
                    )
                with col2:
                    st.video(str(fake_video))
                    fam2=st.radio(
                    f"do you know person in video {2*i+2} (Pair {i+1})",
                    [f"No", f"Yes"]
                    )
                response = st.radio(
                    f"Which video do you think is fake? (Pair {i+1})",
                    [f"Video {i*2 + 1+40}", f"Video {i*2 + 2+40}"]
                )
                responses.append(response)
                familiarity.append(fam1)
                familiarity.append(fam2)
            # Display Audio Videos
            st.subheader("Video with Audio Analysis")
            for i, (real_video, fake_video) in enumerate(zip(
                media_config['videos']['with_audio']['real'][:8],
                media_config['videos']['with_audio']['fake'][:8]
            )):
                col1, col2 = st.columns(2)
                with col1:
                    st.video(str(real_video))
                    fam1=st.radio(
                    f"do you know person in video {2*i+1}? ",
                    [f"No", f"Yes"]
                    )
                with col2:
                    st.video(str(fake_video))
                    fam2=st.radio(
                    f"do you know person in video {2*i+2} ? ",
                    [f"No", f"Yes"]
                    )
                response = st.radio(
                    f"Which video do you think is fake? (Audio Pair {i+1})",
                    [f"Video {i*2 + 1+56}", f"Video {i*2 + 2+56}"]
                )
                responses.append(response)
                familiarity.append(fam1)
                familiarity.append(fam2)

            if st.form_submit_button("Submit Responses"):
                st.session_state.user_data['responses'] = responses
                st.session_state.user_data['familiarity'] = familiarity
                save_user_response(st.session_state.user_data)
                st.session_state.page = 'results'
                st.rerun()

    # Results Page
    elif st.session_state.page == 'results':
        st.header("Analysis Results")
        
        # Load all responses and perform Bayesian analysis
        all_responses = load_all_responses()
        analysis_results = perform_bayesian_analysis(all_responses)
        
        # Display correlation plots
        st.subheader("Correlation Analysis")
        
        # Age vs Detection Accuracy
        fig_age = px.scatter(all_responses, x='age', y='accuracy',
                           title='Age vs Detection Accuracy',
                           trendline="ols")
        st.plotly_chart(fig_age)
        
        # Social Media Hours vs Detection Accuracy
        fig_social = px.scatter(all_responses, x='social_media_hours', 
                              y='accuracy',
                              title='Social Media Usage vs Detection Accuracy',
                              trendline="ols")
        st.plotly_chart(fig_social)
        # familiarty
        fig_fam = px.scatter(all_responses, x='fam_score', 
                              y='accuracy',
                              title='familiarity vs Detection Accuracy',
                              trendline="ols")
        st.plotly_chart(fig_fam)
    
        all_responses['withAudio'] = all_responses['withAudio'].astype(float)
        all_responses['withoutAudio'] = all_responses['withoutAudio'].astype(float)
        all_responses['images'] = all_responses['images'].astype(float)
        withaudio=all_responses['withAudio'].mean()
        withoutaudio=all_responses['withoutAudio'].mean()
        print(withoutaudio)
        images=all_responses['images'].mean()
        fig, ax = plt.subplots(figsize=(10, 5))
        categories = ['Images', 'WithAudio', 'WithoutAudio']
        accuracy = [images, withaudio, withoutaudio]

        ax.bar(categories, accuracy, color=['skyblue', 'lightgreen', 'lightcoral'], width=0.5, alpha=0.8)

        # Adding labels and title
        ax.set_xlabel('Categories')
        ax.set_ylabel('Accuracy')
        ax.set_title('Accuracy for Images, With Audio, and Without Audio')

        # Display the plot in Streamlit
        st.pyplot(fig)
        # images
        # fig_images = px.scatter(all_responses, x='images', 
        #                       y='accuracy',
        #                       title='Images vs Detection Accuracy',
        #                       trendline="ols")
        # st.plotly_chart(fig_images)
        #  # Videos without Audio
        # fig_videos = px.scatter(all_responses, x='withoutAudio', 
        #                       y='accuracy',
        #                       title='Videos without Audio vs Detection Accuracy',
        #                       trendline="ols")
        # st.plotly_chart(fig_videos)
        # # Videos with Audio
        # fig_videos_audio = px.scatter(all_responses, x='withAudio', 
        #                       y='accuracy',
        #                       title='Videos with Audio vs Detection Accuracy',
        #                       trendline="ols")
        # st.plotly_chart(fig_videos_audio)
        # Gender comparison
        fig_gender = px.box(all_responses, x='gender', y='accuracy',
                          title='Detection Accuracy by Gender')
        st.plotly_chart(fig_gender)
        
        # Display Bayesian analysis results
        st.subheader("Bayesian Analysis Results")
        st.json(analysis_results)
        
        if st.button("Start New Test"):
            st.session_state.page = 'form'
            st.rerun()

if __name__ == "__main__":
    main()