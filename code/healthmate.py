# =================================================
# Load the libraries
# =================================================
import streamlit as st
from rag_pipeline import ask_healthmate

# =================================================
# Page Configuration
# =================================================
st.set_page_config(
    page_title = "HealthMate",
    page_icon = "🏋️‍♂️",
    layout = "wide"
)

# =================================================
# Custom CSS
# =================================================
st.markdown("""
<style>
/* Main App Background */
.main {background-color: #F6FFF4;}

/* Sidebar */
[data-testid = "stSidebar"] {
            background: #7B8163;
            border-right: 2px solid #8D6E63;
            }

/* Sidebar Title */
.sidebar-title {
            font-size: 28px;
            font-weight: bold;
            color: black;
            text-align: center;
            margin-bottom: 15px;
            }

/* Chat Messages */
.stChatMessage {
            border-radius: 15px;
            padding: 12px;
            margin-bottom: 10px;
            }

/* Main Title*/
h1 {
    color: #166534;
    text-align: center;
    }
            
/* Subtitle*/
.healthmate-subtitle {
            text-align: center;
            color: #4B5563;
            margin-bottom: 30px;
            font-size: 18px;
            }

/*Sidebar Buttons*/
.stButton > button {
            width: 100%;
            border-radius: 12px;
            border: none;
            background-color: #D6DDC7;
            color: #166534;
            font-weight: bold;
            padding: 10px;
            transition: 0.3s;
            }

.stButton > button:hover {
            background-color: #15803D;
            color: white;
            }
       
/* Chat Input */
[data-testid = "stChatInput"] {
            border-top: 2px solid #8D6E63;
            padding-top: 18px;
            margin-top: 30px;
            }

/* Feature Cards */
.feature-card {
            background: #D6DDC7;
            
            padding: 25px;
            border-radius: 18px;
            text-align: center;
            border: 1px solid #8D6E63;
            height: 180px;
            
            box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
        }
            

            
/* Hero Section */
.hero-section {
        background: #7B8163;

        padding: 35px;
        border-radius: 22px;
        margin-bottom: 25px;

            
        }
</style>
""", unsafe_allow_html = True)

# =================================================
# Session State Initialization
# =================================================
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "chat_1"

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_titles" not in st.session_state:
    st.session_state.chat_titles = {}

# =================================================
# Sidebar
# =================================================
with st.sidebar:
    st.markdown(
        "<div class = 'sidebar-title'>🏋️‍♂️ HealthMate 🥗</div>",
        unsafe_allow_html = True)

    st.divider()

    # New Chat Button
    if st.button("New Chat 💬"):

        # Save Current Chat
        st.session_state.all_chats[
            st.session_state.current_chat
        ] = st.session_state.chat_history

        # Create New Chat
        st.session_state.chat_counter += 1

        new_chat_name = f"chat_{st.session_state.chat_counter}"

        st.session_state.current_chat = new_chat_name
        st.session_state.chat_history = []

        st.rerun()
    
    # Clear Current Chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []

        st.session_state.all_chats[
            st.session_state.current_chat
        ] = []

        st.rerun()
    
    st.divider()

    st.subheader("≪ Chat History 💬")

    # Show Previous Chats
    #for chat_name in st.session_state.all_chats.keys():
    #    if st.button(chat_name):
    
    for chat_id in st.session_state.all_chats.keys():
            
        # Get title or fallback
        display_title = st.session_state.chat_titles.get(
            chat_id,
            "New Chat"
        )

        if st.button(display_title):
            st.session_state.current_chat = chat_id

            st.session_state.chat_history = (
                st.session_state.all_chats[chat_id]
            )

            st.rerun()

# =================================================
# Main Title
# =================================================
st.title("🏋️‍♂️ HealthMate 🥗")

st.markdown(
    "<p class = 'healthmate-subtitle'>Your AI-powered Fitness & Nutrition Coach</p>",
    unsafe_allow_html = True
    )

#st.divider()
st.markdown("<div style = 'margin-top: 35px;'></div>",
            unsafe_allow_html = True)
st.markdown("<hr style = 'border: 1px solid #8D6E63;'>",
            unsafe_allow_html = True)

# =====================================
# HERO SECTION
# =====================================
st.markdown("""
<div class = "hero-section">
<h2 style = "
            color: #F5F1E8;
            text-align: center;
            margin-bottom: 12px;
            font-size: 42px
    ">
     💪 Your AI Fitness & Nutrition Coach       
    </h2>

<p style = "
            text-align: center;
            color: #F5F1E8;
            font-size: 20px;
            line-height: 1.7;
    ">
    Get personalized guidance for workouts, muscle gain, fat loss, meal planning,
        recovery, and healthy living - powered by AI.
</p>         
</div>""",
unsafe_allow_html = True)



# =====================================
# FEATURE CARDS
# =====================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class = "feature-card">
        <h3 style = "color: #166534;">
            🏋️‍♂️ Workout Plans
        </h3>
        
    <p style = "color: solid #8D6E63;
                    font-size: 16px;">
        Beginner to advanced fitness guidance, exercises, sets, reps & routines.   
    </p>
    </div>""",
    unsafe_allow_html = True)

with col2:
    st.markdown("""
    <div class = "feature-card">
        <h3 style = "color: #166534;">
            🥗 Nutrition Tips
        </h3>
                
    <p style = "color: solid #8D6E63;
                font-size: 16px;">
        Meal prep plan, protein intake, dietary guidance & healthy eating.
    </p>
    </div>""",
    unsafe_allow_html = True)

with col3:
    st.markdown("""
    <div class = "feature-card">
        <h3 style = "color: #166534;">
           🛏️ Recovery & Wellness
        </h3>
                
    <p style = "color: solid #8D6E63;
                font-size: 16px;">
        Recovery strategies, sleep habits, hydration &
                healthy lifestyle tips.
    </p>
    </div>""",
    unsafe_allow_html = True)

st.markdown("<div style = 'margin-top: 35px;'></div>",
            unsafe_allow_html = True)
st.markdown("<hr style = 'border: 1px solid #8D6E63;'>",
            unsafe_allow_html = True)

# =================================================
# Session State
# =================================================
#if "chat_history" not in st.session_state:
#    st.session_state.chat_history = []

# =================================================
# Display Chat History
# =================================================
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["message"])

        if chat["role"] == "assistant" and "sources" in chat:
            with st.expander("📚 Source Documents"):
                for src in chat["sources"]:
                    st.markdown(f"- {src}")

# =================================================
# User Input
# =================================================
user_prompt = st.chat_input("Ask HealthMate anything about fitness & nutrition…")

# =================================================
# Process User Input
# =================================================
if user_prompt:

    # Add user message
    st.session_state.chat_history.append({
        "role" : "user",
        "message" : user_prompt
    })

    # Auto Generate Chat Title
    current_chat = st.session_state.current_chat

    # Only create title if it doesn't exist yet
    if current_chat not in st.session_state.chat_titles:
        
        # Use first user question
        title = user_prompt.strip()

        # Limit title length
        if len(title) > 40:
            title = title[:40] + "…"
        
        st.session_state.chat_titles[current_chat] = title

    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Generating insights…"):
            # answer, sources = ask_healthmate(user_prompt)
            answer, sources = ask_healthmate(
                user_prompt,
                st.session_state.chat_history)

            st.markdown(answer)

            with st.expander("📚 Source Documents"):
                for src in sources:
                    st.markdown(f"- {src}")
    
    # Save Assistant Response
    st.session_state.chat_history.append({
        "role" : "assistant",
        "message" : answer,
        "sources" : sources
    })
    
    # Save current chat into all chats
    st.session_state.all_chats[
        st.session_state.current_chat
    ] = st.session_state.chat_history

# =================================================
# Previous Custom CSS
# =================================================
# st.markdown("""
#<style>

#.main {background-color: #0E1117;}

#.stChatMessage {
#            border-radius: 15px;
#            padding: 12px;
#            margin-bottom: 10px;
#            }

#h1 {
#        color: #00FFAA;
#        text-align: center;
#    }

#.healthmate-subtitle {
#        text-align: center;
#        color: #B0B0B0;
#        margin-bottom: 30px;        
#}

#.source-box {
#        background-color: #1E1E1E;
#        padding: 10px;
#        border-radius: 10px;
#        margin-top: 10px;        
#}

#</style>
#""",
#unsafe_allow_html = True)

# =====================================
# Previous HERO SECTION
# =====================================

#st.markdown("""
#<div style="
#    background: linear-gradient(135deg, #1E293B, #0F172A);
#    padding: 30px;
#    border-radius: 20px;
#    margin-bottom: 25px;
#    border: 1px solid #334155;
#">

#<h2 style="
#    color: #22C55E;
#    text-align: center;
#    margin-bottom: 10px;
#">
#💪 Your AI Fitness & Nutrition Coach
#</h2>

#<p style="
#    text-align: center;
#    color: #CBD5E1;
#    font-size: 18px;
#    margin-bottom: 25px;
#">
#Get personalized guidance for workouts, muscle gain, fat loss,
#meal planning, recovery, and healthy living — powered by AI.
#</p>

#</div>
#""", unsafe_allow_html=True)

# =====================================
# Previous FEATURE CARDS
# =====================================

#col1, col2, col3 = st.columns(3)

#with col1:
#    st.markdown("""
#    <div style="
#        background-color:#111827;
#        padding:20px;
#        border-radius:15px;
#        text-align:center;
#        border:1px solid #1F2937;
#        height:180px;
#    ">
#        <h3>🏋️ Workout Plans</h3>
#        <p style="color:#9CA3AF;">
#        Beginner to advanced fitness guidance,
#        exercises, sets, reps & routines.
#        </p>
#    </div>
#    """, unsafe_allow_html=True)

#with col2:
#    st.markdown("""
#    <div style="
#        background-color:#111827;
#        padding:20px;
#        border-radius:15px;
#        text-align:center;
#        border:1px solid #1F2937;
#        height:180px;
#    ">
#        <h3>🥗 Nutrition Tips</h3>
#        <p style="color:#9CA3AF;">
#        Meal suggestions, protein intake,
#        calorie guidance & healthy eating.
#        </p>
#    </div>
#    """, unsafe_allow_html=True)

#with col3:
#    st.markdown("""
#    <div style="
#        background-color:#111827;
#        padding:20px;
#        border-radius:15px;
#        text-align:center;
#        border:1px solid #1F2937;
#        height:180px;
#    ">
#        <h3>⚡ Recovery & Wellness</h3>
#        <p style="color:#9CA3AF;">
#        Learn recovery strategies, sleep habits,
#        hydration & lifestyle improvements.
#        </p>
#    </div>
#    """, unsafe_allow_html=True)

# =====================================
# Previous SUGGESTED QUESTIONS
# =====================================

#st.markdown("## 🔥 Try Asking")

#suggestions_cols = st.columns(5)

#suggestions = [
#    "🥚 High-protein breakfast",
#    "🏋️ Beginner workout",
#    "💪 Muscle gain protein",
#    "🔥 Foods for fat loss",
#    "😴 Recovery after workout"
#]

#for col, suggestion in zip(suggestions_cols, suggestions):

#    with col:
#        st.markdown(f"""
#        <div style="
#            background-color:#1E293B;
#           padding:12px;
#            border-radius:12px;
#            text-align:center;
#            color:white;
#            border:1px solid #334155;
#            font-size:14px;
#        ">
#        {suggestion}
#        </div>
#        """, unsafe_allow_html=True)

#st.markdown("<br>", unsafe_allow_html=True)