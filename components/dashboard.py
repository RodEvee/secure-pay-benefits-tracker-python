import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from database.db_manager import get_settings, get_time_entries, save_time_entry, delete_time_entry
from services.calculator import calculate_weekly_pay

def render_dashboard():
    st.header("Dashboard")
    
    settings = get_settings()
    entries = get_time_entries()
    
    if "selected_week" not in st.session_state:
        st.session_state.selected_week = datetime.now()
        
    current_date = st.session_state.selected_week
    start_of_week = current_date - timedelta(days=current_date.weekday())
    
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("⬅️"):
            st.session_state.selected_week -= timedelta(days=7)
            st.rerun()
    with col2:
        end_of_week = start_of_week + timedelta(days=6)
        st.markdown(f"<h3 style='text-align: center;'>{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}</h3>", unsafe_allow_html=True)
    with col3:
        if st.button("➡️"):
            st.session_state.selected_week += timedelta(days=7)
            st.rerun()

    current_week_entries = []
    for e in entries:
        try:
            e_date = datetime.strptime(e['day'], "%Y-%m-%d").date()
            if start_of_week.date() <= e_date <= end_of_week.date():
                current_week_entries.append(e)
        except:
            pass
            
    summary = calculate_weekly_pay(current_week_entries, settings)
    
    # Days List
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        day_str = day_date.strftime("%Y-%m-%d")
        
        entry = next((e for e in current_week_entries if e['day'] == day_str), None)
        
        with st.container():
            st.markdown("---")
            d_col1, d_col2, d_col3, d_col4 = st.columns([2, 2, 2, 2])
            
            with d_col1:
                st.markdown(f"**{day_date.strftime('%a')}**<br>{day_date.strftime('%d')}", unsafe_allow_html=True)
                
            if entry:
                with d_col2:
                    st.markdown(f"<span style='color: gray; font-size: 0.8em;'>Shift</span><br>{entry['startTime']} - {entry['endTime']}", unsafe_allow_html=True)
                with d_col3:
                    st.markdown(f"<span style='color: gray; font-size: 0.8em;'>Total</span><br>**{entry['duration']/60:.1f}h**", unsafe_allow_html=True)
                with d_col4:
                    if st.button("Edit", key=f"edit_{day_str}"):
                        st.session_state.editing_entry = entry
                        st.session_state.editing_date = day_str
                        st.session_state.show_modal = True
                        st.rerun()
            else:
                with d_col2:
                    st.markdown("<span style='color: gray; font-style: italic;'>No entry</span>", unsafe_allow_html=True)
                with d_col3:
                    st.empty()
                with d_col4:
                    if st.button("Add", key=f"add_{day_str}"):
                        st.session_state.editing_entry = None
                        st.session_state.editing_date = day_str
                        st.session_state.show_modal = True
                        st.rerun()

    st.markdown("---")
    # Summary persistent footer equivalent
    st.markdown("""
        <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; display: flex; justify-content: space-between;'>
            <div>
                <div style='font-size: 10px; color: gray; text-transform: uppercase;'>Hours</div>
                <div style='font-size: 24px; font-weight: bold;'>{:.1f}</div>
            </div>
            <div>
                <div style='font-size: 10px; color: gray; text-transform: uppercase;'>Gross</div>
                <div style='font-size: 24px; font-weight: bold;'>${:,.2f}</div>
            </div>
            <div>
                <div style='font-size: 10px; color: #3b82f6; text-transform: uppercase;'>Net Pay</div>
                <div style='font-size: 24px; font-weight: bold; color: #2563eb;'>${:,.2f}</div>
            </div>
        </div>
    """.format(summary['totalHours'], summary['grossPay'], summary['netPay']), unsafe_allow_html=True)

    # Modal handling
    if getattr(st.session_state, 'show_modal', False):
        st.markdown("### Log Time for " + st.session_state.editing_date)
        entry = getattr(st.session_state, 'editing_entry', None)
        
        start_time = st.time_input("Start Time", value=datetime.strptime(entry['startTime'], "%H:%M").time() if entry else datetime.strptime("09:00", "%H:%M").time())
        end_time = st.time_input("End Time", value=datetime.strptime(entry['endTime'], "%H:%M").time() if entry else datetime.strptime("17:00", "%H:%M").time())
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", type="primary"):
                start_dt = datetime.combine(datetime.today(), start_time)
                end_dt = datetime.combine(datetime.today(), end_time)
                if end_dt < start_dt:
                    end_dt += timedelta(days=1)
                
                duration = int((end_dt - start_dt).total_seconds() / 60)
                
                new_entry = {
                    'id': entry['id'] if entry else st.session_state.editing_date + "_id",
                    'day': st.session_state.editing_date,
                    'startTime': start_time.strftime("%H:%M"),
                    'endTime': end_time.strftime("%H:%M"),
                    'duration': duration
                }
                save_time_entry(new_entry)
                st.session_state.show_modal = False
                st.rerun()
                
        with col2:
            if st.button("Cancel"):
                st.session_state.show_modal = False
                st.rerun()
                
        if entry:
            if st.button("Delete", type="secondary"):
                delete_time_entry(entry['id'])
                st.session_state.show_modal = False
                st.rerun()
