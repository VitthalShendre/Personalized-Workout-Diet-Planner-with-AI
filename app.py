import streamlit as st
import mysql.connector
from sklearn.tree import DecisionTreeClassifier
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# ---------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="KAR#14#vitthal",   # change this
        database="fitness_ai"
    )

# ---------------------------------------------------
# ML MODEL (BMI CLASSIFICATION)
# ---------------------------------------------------

X = [[16], [18], [22], [26], [30], [35]]
y = ["Underweight", "Underweight", "Normal", "Overweight", "Obese", "Obese"]

model = DecisionTreeClassifier()
model.fit(X, y)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.set_page_config(page_title="AI Fitness Planner", page_icon="🏋")
st.title("🏋 Advanced AI Personalized Workout & Diet Planner")

menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------

if menu == "Register":

    st.subheader("Create New Account")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Register"):
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username,password) VALUES (%s,%s)",
            (new_user, new_pass)
        )
        db.commit()
        db.close()
        st.success("Account Created Successfully ✅")

# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

if menu == "Login":

    if not st.session_state.logged_in:

        st.subheader("Login to Continue")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            db = connect_db()
            cursor = db.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            data = cursor.fetchone()
            db.close()

            if data:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login Successful ✅")
            else:
                st.error("Invalid Credentials ❌")

    else:

        st.success(f"Welcome {st.session_state.username} 👋")

        # ---------------------------------------------------
        # USER INPUT
        # ---------------------------------------------------

        age = st.number_input("Age", 15, 60)
        weight = st.number_input("Weight (kg)", 30, 150)
        height = st.number_input("Height (cm)", 120, 220)

        goal = st.selectbox(
            "Select Your Goal",
            ["Weight Loss", "Muscle Gain", "Maintain Fitness"]
        )

        # ---------------------------------------------------
        # GENERATE PLAN
        # ---------------------------------------------------

        if st.button("🔥 Generate Detailed AI Plan"):

            # BMI Calculation
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            category = model.predict([[bmi]])[0]

            # BMR & Calories
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
            calories = bmr * 1.55

            # Protein
            protein = weight * 2 if goal == "Muscle Gain" else weight * 1.2

            # ---------------------------------------------------
            # DISPLAY REPORT
            # ---------------------------------------------------

            st.header("📊 Body Analysis Report")

            st.subheader(f"BMI: {round(bmi,2)}")
            st.write(f"Category: **{category}**")

            if category == "Underweight":
                st.info("You are below ideal weight. Focus on strength training and calorie surplus diet.")
            elif category == "Normal":
                st.success("You are in healthy range. Maintain balanced lifestyle.")
            elif category == "Overweight":
                st.warning("You are slightly above ideal weight. Add cardio and calorie control.")
            else:
                st.error("You are in obesity range. Structured fitness program required.")

            st.subheader("🔥 Daily Nutrition Requirements")
            st.write(f"Estimated Calories: **{round(calories)} kcal/day**")
            st.write(f"Recommended Protein: **{round(protein)} g/day**")

            # ---------------------------------------------------
            # WORKOUT PLAN
            # ---------------------------------------------------

            st.header("🏋 Weekly Workout Plan")

            if goal == "Weight Loss":
                workout = """
Monday: Running + Core  
Tuesday: HIIT  
Wednesday: Brisk Walk  
Thursday: Cycling  
Friday: Full Body Cardio  
Saturday: Yoga  
Sunday: Rest  
"""
            elif goal == "Muscle Gain":
                workout = """
Monday: Chest + Triceps  
Tuesday: Back + Biceps  
Wednesday: Legs  
Thursday: Shoulders  
Friday: Arms  
Saturday: Heavy Lifting  
Sunday: Rest  
"""
            else:
                workout = """
Monday: Cardio  
Wednesday: Full Body  
Friday: Core  
Sunday: Light Jog  
"""

            st.text(workout)

            # ---------------------------------------------------
            # DIET PLAN
            # ---------------------------------------------------

            st.header("🥗 Diet Plan")

            if goal == "Weight Loss":
                diet = """
Breakfast: Oats + Fruits  
Lunch: Dal + Brown Rice  
Dinner: Roti + Vegetables  
Snacks: Nuts + Green Tea  
Avoid Junk Food  
"""
            elif goal == "Muscle Gain":
                diet = f"""
Breakfast: Eggs + Milk  
Lunch: Chicken/Paneer + Rice  
Dinner: Roti + Dal  
Snacks: Peanut Butter  
Target Protein: {round(protein)}g daily  
"""
            else:
                diet = """
Breakfast: Poha + Milk  
Lunch: Roti + Sabzi  
Dinner: Light Khichdi  
Snacks: Fruits  
"""

            st.text(diet)

            # ---------------------------------------------------
            # SAVE TO DATABASE
            # ---------------------------------------------------

            db = connect_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO user_plans (username,bmi,calories,protein,goal) VALUES (%s,%s,%s,%s,%s)",
                (st.session_state.username, bmi, calories, protein, goal)
            )
            db.commit()
            db.close()

            # ---------------------------------------------------
            # PDF GENERATION
            # ---------------------------------------------------

            file_name = "fitness_plan.pdf"
            doc = SimpleDocTemplate(file_name, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph("AI Personalized Fitness Plan", styles['Heading1']))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"User: {st.session_state.username}", styles['Normal']))
            elements.append(Paragraph(f"BMI: {round(bmi,2)} ({category})", styles['Normal']))
            elements.append(Paragraph(f"Calories: {round(calories)} kcal", styles['Normal']))
            elements.append(Paragraph(f"Protein: {round(protein)} g/day", styles['Normal']))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Workout Plan:", styles['Heading2']))
            elements.append(Paragraph(workout.replace("\n", "<br/>"), styles['Normal']))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Diet Plan:", styles['Heading2']))
            elements.append(Paragraph(diet.replace("\n", "<br/>"), styles['Normal']))

            doc.build(elements)

            with open(file_name, "rb") as f:
                st.download_button("📄 Download Full PDF Plan", f, file_name)

            st.success("✅ Detailed AI Plan Generated Successfully!")

        # ---------------------------------------------------
        # LOGOUT
        # ---------------------------------------------------

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()