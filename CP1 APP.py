import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import json
import re

# --- PAGE SETUP ---
st.set_page_config(page_title="AI Roadmap Optimizer", page_icon="📈", layout="wide")

st.title("📈 AI Roadmap Optimizer")
st.markdown("### Turn a messy backlog into a strategic plan.")

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Setup")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    
    st.divider()
    st.write("built by Arjun Shivhare")

# --- MAIN INPUT AREA ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Define Strategy")
    goal = st.text_input("Business Goal:", value="Increase User Retention")
    
    st.subheader("2. Add Features")
    # We use a text area because it's easier than adding buttons 1-by-1
    default_features = "Dark Mode\nDrone Delivery\nVoice Search\nOne-Click Checkout\nReferral Bonus"
    features_input = st.text_area("Enter features (one per line):", value=default_features, height=150)
    
    optimize_btn = st.button("🚀 Optimize Roadmap", type="primary")

# --- THE LOGIC ENGINE ---
if optimize_btn:
    if not api_key:
        st.error("⚠️ Please enter your API Key in the sidebar.")
        st.stop()
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Process the list
    feature_list = [f.strip() for f in features_input.split('\n') if f.strip()]
    
    with st.spinner(f"🧠 AI is calculating RICE scores for {len(feature_list)} features..."):
        try:
            # THE PROMPT
            prompt = f"""
            Goal: {goal}
            Features: {feature_list}
            
            Task: Score each feature 1-10 on RICE (Reach, Impact, Confidence, Effort).
            Calculate 'rice_score' = (Reach * Impact * Confidence) / Effort.
            
            Return ONLY raw JSON list:
            [
                {{"name": "Feature Name", "R": 8, "I": 9, "C": 8, "E": 4, "rice_score": score}},
                ...
            ]
            """
            
            response = model.generate_content(prompt)
            # Clean JSON
            clean_json = re.sub(r'```json|```', '', response.text).strip()
            data = json.loads(clean_json)
            df = pd.DataFrame(data)
            
            # --- DISPLAY RESULTS ---
            st.success("Analysis Complete!")
            
            # Create Tabs for View
            tab1, tab2 = st.tabs(["📊 Matrix Chart", "📋 Data Table"])
            
            with tab1:
                # DRAW CHART
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Scatter plot
                scatter = ax.scatter(df['E'], df['I'], s=df['rice_score']*25, alpha=0.6, c='dodgerblue', edgecolors='black')
                
                # Labels
                ax.set_title(f"Prioritization Matrix: {goal}")
                ax.set_xlabel("Effort (Lower is Better)")
                ax.set_ylabel("Impact (Higher is Better)")
                ax.grid(True, linestyle='--', alpha=0.3)
                
                # Annotate bubbles
                for i, txt in enumerate(df['name']):
                    ax.annotate(txt, (df['E'].iloc[i], df['I'].iloc[i]), xytext=(0, 5), textcoords='offset points', ha='center', fontsize=9)
                
                st.pyplot(fig)
                
            with tab2:
                # SHOW TABLE
                st.dataframe(df.sort_values(by="rice_score", ascending=False), use_container_width=True)
                
        except Exception as e:
            st.error(f"Error parsing AI response: {e}")
            st.text(response.text) # Show raw text for debugging
