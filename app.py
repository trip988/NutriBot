import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import re

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="NutriBot",
    page_icon="🥗",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #1a1a2e; color: #eaeaea; }
    .stChatMessage { background-color: #16213e; border-radius: 15px; padding: 10px; margin: 5px 0; border: 1px solid #0f3460; }
    .stSidebar { background-color: #16213e; }
    h1, h2, h3 { color: #e94560; }
    .stButton button { background-color: #e94560; color: white; border-radius: 10px; border: none; width: 100%; }
    .stButton button:hover { background-color: #c73652; }
    .stProgress > div > div { background-color: #e94560; }
    p, li { color: #eaeaea; }
    .stCaption { color: #a0a0a0; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """You are NutriBot, an expert nutrition assistant.
        When asked about any food or drink, always provide a response in this exact format:

        Brief intro line about the food.

        **Nutritional Info (per serving):**
        - 🔥 Calories: Xkcal
        - 💪 Protein: Xg
        - 🍞 Carbohydrates: Xg
        - 🧈 Fats: Xg
        - 🌿 Fiber: Xg

        **Key Vitamins & Minerals:**
        - List 3-4 key ones

        **Health Tip:**
        One short friendly tip about this food.

        Be concise, friendly and helpful."""}
    ]

if "calorie_log" not in st.session_state:
    st.session_state.calorie_log = []

if "daily_goal" not in st.session_state:
    st.session_state.daily_goal = 2000

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None

def extract_calories(text):
    match = re.search(r'Calories:\s*(\d+)', text)
    if match:
        return int(match.group(1))
    return None

def ask_nutribot(prompt, show_user_message=True):
    if show_user_message:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages if show_user_message else
                     st.session_state.messages + [{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
        st.markdown(reply)
        calories = extract_calories(reply)
        if calories:
            food_name = prompt.replace("What are the nutrients in", "").replace("Nutrients in", "").replace("?", "").strip()
            st.session_state.calorie_log.append({
                "food": food_name,
                "calories": calories
            })

    st.session_state.messages.append({"role": "assistant", "content": reply})

with st.sidebar:
    st.image("https://img.icons8.com/color/96/salad.png", width=80)
    st.markdown("## 🥗 NutriBot")
    st.markdown("---")

    st.markdown("### 🎯 Daily Calorie Goal")
    st.session_state.daily_goal = st.number_input(
        "Set your daily goal (kcal)",
        min_value=500,
        max_value=5000,
        value=st.session_state.daily_goal,
        step=50
    )

    total_calories = sum(item["calories"] for item in st.session_state.calorie_log)
    progress = min(total_calories / st.session_state.daily_goal, 1.0)

    st.markdown("### 📊 Today's Progress")
    st.progress(progress)
    st.caption(f"{total_calories} / {st.session_state.daily_goal} kcal consumed")

    if total_calories == 0:
        st.info("Start asking about foods to track calories!")
    elif total_calories < st.session_state.daily_goal * 0.5:
        st.success("Keep eating, you need more fuel!")
    elif total_calories < st.session_state.daily_goal:
        st.info("Going well, almost at your goal!")
    else:
        st.warning("You have reached your daily goal!")

    if st.session_state.calorie_log:
        st.markdown("### 🍽️ Today's Food Log")
        for item in st.session_state.calorie_log:
            st.markdown(f"- {item['food']}: **{item['calories']} kcal**")
        if st.button("🗑️ Clear Log"):
            st.session_state.calorie_log = []
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚡ Quick Search")
    if st.button("🍌 Banana"):
        st.session_state.quick_prompt = "What are the nutrients in a banana?"
    if st.button("🍗 Chicken breast"):
        st.session_state.quick_prompt = "What are the nutrients in 100g chicken breast?"
    if st.button("🥚 Boiled eggs"):
        st.session_state.quick_prompt = "What are the nutrients in 2 boiled eggs?"
    if st.button("🥤 Coca Cola"):
        st.session_state.quick_prompt = "What are the nutrients in Coca Cola?"
    st.markdown("---")
    st.caption("Built with Groq LLaMA + Streamlit")

st.title("🥗 NutriBot")
st.caption("Your personal AI nutrition assistant — ask about any food or drink!")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["💬 Chat", "⚖️ Compare Foods", "🗓️ Meal Planner"])

with tab2:
    st.markdown("### Compare two foods side by side")
    col1, col2 = st.columns(2)
    with col1:
        food1 = st.text_input("First food", placeholder="e.g. Chicken breast")
    with col2:
        food2 = st.text_input("Second food", placeholder="e.g. Paneer")

    if st.button("⚖️ Compare Now"):
        if food1 and food2:
            with st.spinner(f"Comparing {food1} vs {food2}..."):
                compare_prompt = f"""Compare the nutrition of {food1} vs {food2} per 100g.
                Return a markdown table with these rows:
                Calories, Protein, Carbohydrates, Fats, Fiber.
                Add a Winner column showing which food wins for each nutrient.
                Then add a 2 line summary of which food is overall healthier and why."""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": compare_prompt}]
                )
                result = response.choices[0].message.content
                st.markdown(result)
        else:
            st.warning("Please enter both foods to compare!")

with tab3:
    st.markdown("### Generate your personalized meal plan")

    col1, col2, col3 = st.columns(3)
    with col1:
        calorie_target = st.number_input(
            "Daily calorie target",
            min_value=1000,
            max_value=5000,
            value=2000,
            step=100
        )
    with col2:
        diet_type = st.selectbox(
            "Diet type",
            ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"]
        )
    with col3:
        goal = st.selectbox(
            "Your goal",
            ["Weight Loss", "Muscle Gain", "Maintain Weight", "Improve Energy"]
        )

    cuisine = st.selectbox(
        "Cuisine preference",
        ["Indian", "Mediterranean", "Mixed International", "Continental"]
    )

    if st.button("🗓️ Generate Meal Plan"):
        with st.spinner("Creating your personalized meal plan..."):
            meal_prompt = f"""Create a detailed one day meal plan for someone with these requirements:
            - Daily calorie target: {calorie_target} kcal
            - Diet type: {diet_type}
            - Goal: {goal}
            - Cuisine preference: {cuisine}

            Format it exactly like this:

            ## Breakfast
            - Meal name and portion
            - Calories: X kcal
            - Key nutrients: protein, carbs, fats

            ## Mid Morning Snack
            - Meal name and portion
            - Calories: X kcal
            - Key nutrients: protein, carbs, fats

            ## Lunch
            - Meal name and portion
            - Calories: X kcal
            - Key nutrients: protein, carbs, fats

            ## Evening Snack
            - Meal name and portion
            - Calories: X kcal
            - Key nutrients: protein, carbs, fats

            ## Dinner
            - Meal name and portion
            - Calories: X kcal
            - Key nutrients: protein, carbs, fats

            ## Daily Summary
            - Total calories
            - Total protein
            - Total carbs
            - Total fats
            - One tip for achieving the {goal} goal

            Make it practical, delicious and achievable."""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": meal_prompt}]
            )
            meal_plan = response.choices[0].message.content
            st.markdown(meal_plan)

            st.success("Meal plan generated! You can screenshot this or copy it.")

with tab1:
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.quick_prompt:
        prompt = st.session_state.quick_prompt
        st.session_state.quick_prompt = None
        ask_nutribot(prompt, show_user_message=False)
        st.rerun()

    if prompt := st.chat_input("Ask about any food or drink... e.g. 'nutrients in brown rice'"):
        ask_nutribot(prompt, show_user_message=True)
        st.rerun()
