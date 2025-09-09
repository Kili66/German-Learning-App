import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# Set page configuration
st.set_page_config(
    page_title="DeutschLernen - German Learning App",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E90FF;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #FF8C00;
        margin-bottom: 1rem;
    }
    .section-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .progress-bar {
        height: 20px;
        border-radius: 10px;
        background-color: #e0e0e0;
        margin-bottom: 1rem;
    }
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        background-color: #1E90FF;
        text-align: center;
        color: white;
        line-height: 20px;
    }
    .metric-box {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .level-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    .A1 { background-color: #FF6B6B; color: white; }
    .A2 { background-color: #4ECDC4; color: white; }
    .B1 { background-color: #FFD166; color: black; }
    .B2 { background-color: #06D6A0; color: white; }
    .C1 { background-color: #118AB2; color: white; }
    .C2 { background-color: #073B4C; color: white; }
</style>
""", unsafe_allow_html=True)

# Initialize session state for user data and progress
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'level': 'A1',
        'points': 0,
        'vocabulary_progress': 0,
        'grammar_progress': 0,
        'listening_progress': 0,
        'streak_days': 0,
        'last_login': None,
        'completed_exercises': [],
        'vocabulary_mastered': 0,
        'daily_goal': 30  # minutes
    }

if 'vocabulary_list' not in st.session_state:
    # Sample vocabulary data by level
    st.session_state.vocabulary_list = {
        'A1': [
            {'german': 'Haus', 'english': 'house', 'mastered': False},
            {'german': 'Buch', 'english': 'book', 'mastered': False},
            {'german': 'Stuhl', 'english': 'chair', 'mastered': False},
            {'german': 'Tisch', 'english': 'table', 'mastered': False},
            {'german': 'Frau', 'english': 'woman', 'mastered': False},
        ],
        'A2': [
            {'german': 'entscheiden', 'english': 'to decide', 'mastered': False},
            {'german': 'wichtig', 'english': 'important', 'mastered': False},
            {'german': 'versuchen', 'english': 'to try', 'mastered': False},
            {'german': 'erklären', 'english': 'to explain', 'mastered': False},
            {'german': 'Arbeit', 'english': 'work', 'mastered': False},
        ]
    }

if 'grammar_exercises' not in st.session_state:
    # Sample grammar exercises by level
    st.session_state.grammar_exercises = {
        'A1': [
            {'question': '___ heißt du? (What is your name?)', 
             'options': ['Wer', 'Wie', 'Wo', 'Was'], 
             'answer': 'Wie',
             'completed': False},
            {'question': 'Ich ___ aus Deutschland. (I am from Germany.)', 
             'options': ['bin', 'bist', 'ist', 'sind'], 
             'answer': 'bin',
             'completed': False},
        ],
        'A2': [
            {'question': 'Gestern ___ ich ins Kino gegangen. (Yesterday I went to the cinema.)', 
             'options': ['habe', 'hat', 'bin', 'ist'], 
             'answer': 'bin',
             'completed': False},
            {'question': 'Wenn ich Zeit ___, komme ich. (If I have time, I will come.)', 
             'options': ['habe', 'hätte', 'hatte', 'haben'], 
             'answer': 'habe',
             'completed': False},
        ]
    }

# Function to update user progress
def update_progress(area, points=10):
    if area == 'vocabulary':
        st.session_state.user_data['vocabulary_progress'] = min(
            st.session_state.user_data['vocabulary_progress'] + 2, 100
        )
    elif area == 'grammar':
        st.session_state.user_data['grammar_progress'] = min(
            st.session_state.user_data['grammar_progress'] + 2, 100
        )
    elif area == 'listening':
        st.session_state.user_data['listening_progress'] = min(
            st.session_state.user_data['listening_progress'] + 2, 100
        )
    
    st.session_state.user_data['points'] += points
    
    # Check if user should level up
    total_progress = (
        st.session_state.user_data['vocabulary_progress'] + 
        st.session_state.user_data['grammar_progress'] + 
        st.session_state.user_data['listening_progress']
    ) / 3
    
    levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    current_index = levels.index(st.session_state.user_data['level'])
    
    if total_progress >= 80 and current_index < len(levels) - 1:
        st.session_state.user_data['level'] = levels[current_index + 1]
        st.success(f"Herzlichen Glückwunsch! You've reached level {levels[current_index + 1]}!")

# Function to update streak
def update_streak():
    today = datetime.now().date()
    last_login = st.session_state.user_data['last_login']
    
    if last_login is None:
        st.session_state.user_data['streak_days'] = 1
    else:
        if today == last_login:
            # Already logged in today
            return
        elif today - last_login == timedelta(days=1):
            # Consecutive day
            st.session_state.user_data['streak_days'] += 1
        else:
            # Broken streak
            st.session_state.user_data['streak_days'] = 1
    
    st.session_state.user_data['last_login'] = today

# Main app
def main():
    # Update login streak
    update_streak()
    
    # Header
    st.markdown('<h1 class="main-header">🇩🇪 DeutschLernen</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Your Learning Profile")
        st.markdown(f"""
        <div class="metric-box">
            <h3>Current Level</h3>
            <span class="level-badge {st.session_state.user_data['level']}">{st.session_state.user_data['level']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-box">
            <h3>Points</h3>
            <p style="font-size: 1.5rem;">{st.session_state.user_data['points']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-box">
            <h3>Streak</h3>
            <p style="font-size: 1.5rem;">{st.session_state.user_data['streak_days']} days 🔥</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.header("Progress Overview")
        
        # Progress bars
        st.markdown("Vocabulary")
        vocab_progress = st.session_state.user_data['vocabulary_progress']
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {vocab_progress}%">{vocab_progress}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("Grammar")
        grammar_progress = st.session_state.user_data['grammar_progress']
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {grammar_progress}%">{grammar_progress}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("Listening")
        listening_progress = st.session_state.user_data['listening_progress']
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {listening_progress}%">{listening_progress}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.header("Daily Goal")
        goal_progress = min(st.session_state.user_data['points'] / 3, 100)
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {goal_progress}%">{int(goal_progress)}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Learn Vocabulary", "Grammar Practice", "Listening Exercises", "Analytics Dashboard"])
    
    # Vocabulary tab
    with tab1:
        st.markdown('<h2 class="sub-header">Learn Vocabulary</h2>', unsafe_allow_html=True)
        
        level = st.selectbox("Select Level", ["A1", "A2", "B1", "B2", "C1", "C2"], key="vocab_level")
        
        # Display vocabulary list for selected level
        vocab_data = st.session_state.vocabulary_list.get(level, [])
        
        if vocab_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Vocabulary List")
                for i, word in enumerate(vocab_data):
                    status = "✅" if word['mastered'] else "📝"
                    st.write(f"{status} {word['german']} - {word['english']}")
            
            with col2:
                st.markdown("### Practice")
                if st.button("Practice Random Word", key="practice_vocab"):
                    word_to_practice = random.choice(vocab_data)
                    st.session_state.current_word = word_to_practice
                
                if 'current_word' in st.session_state:
                    word = st.session_state.current_word
                    st.write(f"**What does '{word['german']}' mean in English?**")
                    
                    user_answer = st.text_input("Your answer:", key="vocab_answer")
                    
                    if st.button("Check Answer", key="check_vocab"):
                        if user_answer.lower() == word['english'].lower():
                            st.success("Correct! 🎉")
                            # Mark as mastered
                            for w in vocab_data:
                                if w['german'] == word['german']:
                                    w['mastered'] = True
                                    st.session_state.user_data['vocabulary_mastered'] += 1
                            update_progress('vocabulary')
                        else:
                            st.error(f"Sorry, the correct answer is '{word['english']}'")
        else:
            st.info(f"No vocabulary available for level {level} yet. Check back soon!")
    
    # Grammar tab
    with tab2:
        st.markdown('<h2 class="sub-header">Grammar Practice</h2>', unsafe_allow_html=True)
        
        level = st.selectbox("Select Level", ["A1", "A2", "B1", "B2", "C1", "C2"], key="grammar_level")
        
        # Display grammar exercises for selected level
        grammar_data = st.session_state.grammar_exercises.get(level, [])
        
        if grammar_data:
            exercise = random.choice(grammar_data)
            st.write(f"**{exercise['question']}**")
            
            user_answer = st.radio("Select the correct option:", 
                                  exercise['options'], 
                                  key="grammar_answer")
            
            if st.button("Check Answer", key="check_grammar"):
                if user_answer == exercise['answer']:
                    st.success("Correct! 🎉")
                    if exercise not in st.session_state.user_data['completed_exercises']:
                        st.session_state.user_data['completed_exercises'].append(exercise)
                    update_progress('grammar')
                else:
                    st.error(f"Sorry, the correct answer is '{exercise['answer']}'")
        else:
            st.info(f"No grammar exercises available for level {level} yet. Check back soon!")
    
    # Listening tab
    with tab3:
        st.markdown('<h2 class="sub-header">Listening Comprehension</h2>', unsafe_allow_html=True)
        
        level = st.selectbox("Select Level", ["A1", "A2", "B1", "B2", "C1", "C2"], key="listening_level")
        
        # Sample listening exercises
        listening_exercises = {
            'A1': {
                'title': 'Introductions',
                'question': 'What is the name of the speaker?',
                'options': ['Anna', 'Hanna', 'Hannah', 'Ana'],
                'answer': 'Hanna'
            },
            'A2': {
                'title': 'Daily Routine',
                'question': 'What time does Markus get up?',
                'options': ['6:00', '6:30', '7:00', '7:30'],
                'answer': '6:30'
            }
        }
        
        exercise = listening_exercises.get(level)
        
        if exercise:
            st.write(f"**{exercise['title']}**")
            st.write("🎧 Listen to the audio and answer the question:")
            st.write("*(Audio would play here in a real application)*")
            
            st.write(f"**{exercise['question']}**")
            
            user_answer = st.radio("Select the correct answer:", 
                                  exercise['options'], 
                                  key="listening_answer")
            
            if st.button("Check Answer", key="check_listening"):
                if user_answer == exercise['answer']:
                    st.success("Correct! 🎉")
                    update_progress('listening')
                else:
                    st.error(f"Sorry, the correct answer is '{exercise['answer']}'")
        else:
            st.info(f"No listening exercises available for level {level} yet. Check back soon!")
    
    # Analytics tab
    with tab4:
        st.markdown('<h2 class="sub-header">Learning Analytics Dashboard</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.plotly_chart(px.pie(
                values=[st.session_state.user_data['vocabulary_progress'], 
                       st.session_state.user_data['grammar_progress'],
                       st.session_state.user_data['listening_progress']],
                names=['Vocabulary', 'Grammar', 'Listening'],
                title='Skill Distribution',
                color=['Vocabulary', 'Grammar', 'Listening'],
                color_discrete_map={'Vocabulary':'#1E90FF', 'Grammar':'#FF8C00', 'Listening':'#32CD32'}
            ), use_container_width=True)
        
        with col2:
            # Generate some sample historical data
            dates = [datetime.now() - timedelta(days=i) for i in range(7)][::-1]
            points = [random.randint(10, 50) for _ in range(7)]
            
            st.plotly_chart(px.line(
                x=dates, y=points,
                title='Points Earned (Last 7 Days)',
                labels={'x': 'Date', 'y': 'Points'}
            ), use_container_width=True)
        
        with col3:
            levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
            current_level = st.session_state.user_data['level']
            current_index = levels.index(current_level)
            level_progress = (current_index / (len(levels) - 1)) * 100
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = level_progress,
                title = {'text': "Level Progress"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#1E90FF"},
                    'steps': [
                        {'range': [0, 100], 'color': "lightgray"}
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        # Additional analytics
        st.markdown("### Learning Statistics")
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.metric("Vocabulary Mastered", st.session_state.user_data['vocabulary_mastered'])
        
        with col5:
            st.metric("Exercises Completed", len(st.session_state.user_data['completed_exercises']))
        
        with col6:
            st.metric("Current Streak", f"{st.session_state.user_data['streak_days']} days")
        
        # Time spent learning (simulated data)
        st.markdown("### Time Spent Learning")
        learning_data = {
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Minutes': [25, 35, 15, 40, 20, 60, 10]
        }
        df = pd.DataFrame(learning_data)
        st.bar_chart(df, x='Day', y='Minutes')

if __name__ == "__main__":
    main()