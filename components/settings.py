import streamlit as st
from database.db_manager import get_settings, save_settings

def render_settings():
    st.header("Settings")
    
    settings = get_settings()
    
    st.markdown("### 💼 Income Settings")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            hourly_rate = st.number_input("Hourly Rate ($)", value=float(settings['salary']['hourlyRate']), step=0.5)
            ot_threshold = st.number_input("Weekly OT Threshold (Hours)", value=float(settings['salary']['otThreshold']), step=1.0)
        with col2:
            ot_multiplier = st.number_input("Overtime Multiplier (e.g. 1.5x)", value=float(settings['salary']['otMultiplier']), step=0.1)

    st.markdown("---")
    st.markdown("### 🛡️ Retirement (401k)")
    
    is_k401_percent = st.radio("Contribution Type", ["Percentage (%)", "Fixed Amount ($)"], index=0 if settings['deductions'].get('isK401Percent', True) else 1)
    is_percent = is_k401_percent == "Percentage (%)"
    
    col3, col4 = st.columns(2)
    with col3:
        if is_percent:
            k401_employee_pct = st.number_input("Employee Contrib. (%)", value=float(settings['deductions']['k401EmployeePercent']), step=1.0)
            k401_employee_amt = settings['deductions']['k401EmployeeAmount']
        else:
            k401_employee_amt = st.number_input("Employee Contrib. ($)", value=float(settings['deductions']['k401EmployeeAmount']), step=10.0)
            k401_employee_pct = settings['deductions']['k401EmployeePercent']
            
    with col4:
        k401_employer_match = st.number_input("Employer Match (%)", value=float(settings['deductions']['k401EmployerMatchPercent']), step=10.0)

    st.markdown("---")
    st.markdown("### ❤️ Insurance & Benefits")
    
    def benefit_input(label, emp_key, empl_key, default_emp, default_empl):
        st.markdown(f"**{label}**")
        c1, c2 = st.columns(2)
        with c1:
            emp = st.number_input(f"Your Cost ($/wk) - {label}", value=float(settings['deductions'].get(emp_key, default_emp)), step=5.0)
        with c2:
            empl = st.number_input(f"Employer Paid ($/wk) - {label}", value=float(settings['deductions'].get(empl_key, default_empl)), step=5.0)
        return emp, empl

    health_emp, health_empl = benefit_input("Healthcare", "healthEmployee", "healthEmployer", 50.0, 150.0)
    dental_emp, dental_empl = benefit_input("Dental", "dentalEmployee", "dentalEmployer", 10.0, 30.0)
    vision_emp, vision_empl = benefit_input("Vision", "visionEmployee", "visionEmployer", 5.0, 15.0)

    if st.button("Update Payroll Profile", type="primary", use_container_width=True):
        new_settings = {
            "salary": {
                "hourlyRate": hourly_rate,
                "otThreshold": ot_threshold,
                "otMultiplier": ot_multiplier
            },
            "deductions": {
                "isK401Percent": is_percent,
                "k401EmployeePercent": k401_employee_pct,
                "k401EmployeeAmount": k401_employee_amt,
                "k401EmployerMatchPercent": k401_employer_match,
                "healthEmployee": health_emp,
                "healthEmployer": health_empl,
                "dentalEmployee": dental_emp,
                "dentalEmployer": dental_empl,
                "visionEmployee": vision_emp,
                "visionEmployer": vision_empl
            },
            "isBiometricEnabled": settings.get('isBiometricEnabled', True),
            "is2FAEnabled": settings.get('is2FAEnabled', False)
        }
        save_settings(new_settings)
        st.success("Settings Saved!")
