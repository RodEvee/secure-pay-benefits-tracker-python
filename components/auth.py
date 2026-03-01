import streamlit as st
import time

def render_auth(on_success_callback):
    st.markdown("""
        <style>
            .auth-container { text-align: center; margin-top: 50px; }
            .auth-title { font-size: 36px; font-weight: 900; }
            .auth-subtitle { color: #888; margin-bottom: 40px; }
            .bio-btn { 
                background: white; color: #2563eb; border: 2px solid #2563eb; 
                padding: 20px 40px; font-size: 24px; border-radius: 50px; 
                cursor: pointer; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2); 
            }
        </style>
    """, unsafe_allow_html=True)
    
    if 'auth_step' not in st.session_state:
        st.session_state.auth_step = 'BIO'
        
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    if st.session_state.auth_step == 'BIO':
        st.markdown('<div class="auth-title">Secure Pay</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-subtitle">Device Authentication Required</div>', unsafe_allow_html=True)
        if st.button('🛡️ TAP TO SCAN FACE / FINGERPRINT', use_container_width=True):
            st.session_state.auth_step = 'SENDING'
            st.rerun()

    elif st.session_state.auth_step == 'SENDING':
        st.markdown("### Verifying Biometrics...")
        with st.spinner("Processing..."):
            time.sleep(1.5)
        st.session_state.auth_step = 'SMS'
        st.rerun()

    elif st.session_state.auth_step == 'SMS':
        st.markdown("### Enter Code")
        st.markdown("We've sent a 6-digit verification code to your phone.")
        st.info("Your Secure Pay code is **882-941**")
        
        otp = st.text_input("Enter 6-digit code", max_chars=6)
        if st.button("Verify Identity"):
            if otp == "882941":
                st.session_state.auth_step = 'SUCCESS'
                st.rerun()
            else:
                st.error("Invalid code")
        
        if st.button("Back to Biometric"):
            st.session_state.auth_step = 'BIO'
            st.rerun()

    elif st.session_state.auth_step == 'SUCCESS':
        st.success("Authorized: Decryption Complete")
        time.sleep(1)
        # Advance to Dashboard
        on_success_callback()
        
    st.markdown('</div>', unsafe_allow_html=True)
