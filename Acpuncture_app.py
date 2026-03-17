import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Page Configuration
st.set_page_config(
    page_title="Acupuncture Clinic System",
    page_icon="💉",
    layout="wide"
)

# Modern UI CSS
st.markdown("""
<style>

.main {
    background-color:#f5f7fb;
}

.stButton>button {
    background-color:#2a7de1;
    color:white;
    border-radius:8px;
    height:40px;
    width:100%;
}

.card {
    background:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

# Database Connection
conn = sqlite3.connect("clinic.db", check_same_thread=False)
c = conn.cursor()

# Create Tables
def create_tables():

    c.execute('''CREATE TABLE IF NOT EXISTS patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 age INTEGER,
                 gender TEXT,
                 phone TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 patient TEXT,
                 date TEXT,
                 time TEXT,
                 status TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS treatments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 patient TEXT,
                 treatment_date TEXT,
                 diagnosis TEXT,
                 acupuncture_points TEXT,
                 duration TEXT,
                 notes TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 patient TEXT,
                 amount REAL,
                 method TEXT,
                 payment_date TEXT)''')

    conn.commit()

create_tables()

# Sidebar
st.sidebar.title("💉 Clinic System")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Patient",
        "Patients",
        "Appointments",
        "Treatments",
        "Payments"
    ]
)

# Dashboard
if menu == "Dashboard":

    st.title("Clinic Dashboard")

    patient_count = pd.read_sql("SELECT COUNT(*) as count FROM patients", conn)
    appointment_count = pd.read_sql("SELECT COUNT(*) as count FROM appointments", conn)
    treatment_count = pd.read_sql("SELECT COUNT(*) as count FROM treatments", conn)
    revenue = pd.read_sql("SELECT SUM(amount) as total FROM payments", conn)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Patients", patient_count['count'][0])

    with col2:
        st.metric("Appointments", appointment_count['count'][0])

    with col3:
        st.metric("Treatments", treatment_count['count'][0])

    with col4:
        total = revenue['total'][0] if revenue['total'][0] else 0
        st.metric("Revenue", f"₹ {total}")

# Add Patient
elif menu == "Add Patient":

    st.title("Add New Patient")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Patient Name")
        age = st.number_input("Age", 1, 120)

    with col2:
        gender = st.selectbox("Gender", ["Male","Female","Other"])
        phone = st.text_input("Phone Number")

    if st.button("Save Patient"):

        c.execute("INSERT INTO patients (name,age,gender,phone) VALUES (?,?,?,?)",
                  (name,age,gender,phone))

        conn.commit()

        st.success("Patient added successfully")

# View Patients
elif menu == "Patients":

    st.title("Patient Records")

    df = pd.read_sql("SELECT * FROM patients", conn)

    st.dataframe(df, use_container_width=True)

# Appointments
elif menu == "Appointments":

    st.title("Appointment Scheduling")

    patients = pd.read_sql("SELECT name FROM patients", conn)

    if len(patients) == 0:
        st.warning("Please add patients first.")

    else:

        patient = st.selectbox("Select Patient", patients['name'])

        col1, col2 = st.columns(2)

        with col1:
            appt_date = st.date_input("Appointment Date")

        with col2:
            appt_time = st.time_input("Appointment Time")

        if st.button("Book Appointment"):

            c.execute("INSERT INTO appointments (patient,date,time,status) VALUES (?,?,?,?)",
                      (patient,str(appt_date),str(appt_time),"Scheduled"))

            conn.commit()

            st.success("Appointment booked")

    st.subheader("All Appointments")

    df = pd.read_sql("SELECT * FROM appointments", conn)

    st.dataframe(df, use_container_width=True)

# Treatments
elif menu == "Treatments":

    st.title("Treatment Records")

    patients = pd.read_sql("SELECT name FROM patients", conn)

    if len(patients) == 0:

        st.warning("Add patients first")

    else:

        patient = st.selectbox("Patient", patients['name'])

        col1, col2 = st.columns(2)

        with col1:
            treatment_date = st.date_input("Treatment Date")
            diagnosis = st.text_input("Diagnosis")

        with col2:
            duration = st.text_input("Session Duration (minutes)")
            acupuncture_points = st.text_input("Acupuncture Points Used")

        notes = st.text_area("Doctor Notes")

        if st.button("Save Treat"):

            c.execute("""
            INSERT INTO treatments
            (patient,treatment_date,diagnosis,acupuncture_points,duration,notes)
            VALUES (?,?,?,?,?,?)
            """,(patient,str(treatment_date),diagnosis,acupuncture_points,duration,notes))

            conn.commit()

            st.success("Treatment saved")

    st.subheader("Treatment History")

    df = pd.read_sql("SELECT * FROM treatments", conn)

    st.dataframe(df, use_container_width=True)

# Payments
elif menu == "Payments":

    st.title("Payment Management")

    patients = pd.read_sql("SELECT name FROM patients", conn)

    if len(patients) == 0:

        st.warning("Add patients first")

    else:

        patient = st.selectbox("Patient", patients['name'])

        amount = st.number_input("Amount")

        method = st.selectbox(
            "Payment Method",
            ["Cash","UPI","Card"]
        )

        if st.button("Record Payment"):

            c.execute("""
            INSERT INTO payments
            (patient,amount,method,payment_date)
            VALUES (?,?,?,?)
            """,(patient,amount,method,str(date.today())))

            conn.commit()

            st.success("Payment recorded")

    st.subheader("Payment History")

    df = pd.read_sql("SELECT * FROM payments", conn)

    st.dataframe(df, use_container_width=True)
