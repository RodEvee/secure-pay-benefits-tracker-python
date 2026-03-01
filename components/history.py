import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.db_manager import get_settings, get_time_entries
from services.calculator import calculate_weekly_pay

def render_history():
    st.header("History")
    
    settings = get_settings()
    entries = get_time_entries()
    
    # Group entries by Week (Monday-Sunday)
    groups = {}
    for entry in entries:
        try:
            d = datetime.strptime(entry['day'], "%Y-%m-%d").date()
            monday = d - timedelta(days=d.weekday())
            mon_str = monday.strftime("%Y-%m-%d")
            
            if mon_str not in groups:
                groups[mon_str] = []
            groups[mon_str].append(entry)
        except:
            pass
            
    weekly_summaries = []
    for monday, week_entries in groups.items():
        summary = calculate_weekly_pay(week_entries, settings)
        weekly_summaries.append(summary)
        
    # Sort by start date descending
    weekly_summaries.sort(key=lambda x: datetime.strptime(x['startDate'], "%m/%d/%Y") if x['startDate'] != 'N/A' else datetime.min, reverse=True)
    
    lifetime_net = sum(s['netPay'] for s in weekly_summaries)
    
    st.markdown(f"""
    <div style='background-color: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: space-between;'>
        <div>
            <div style='font-size: 12px; font-weight: bold; color: gray; text-transform: uppercase;'>Lifetime Net Pay</div>
            <div style='font-size: 36px; font-weight: 900; color: #111827;'>${lifetime_net:,.2f}</div>
        </div>
        <div style='background-color: #dcfce7; color: #16a34a; padding: 12px; border-radius: 50%; font-size: 24px;'>
            📈
        </div>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    st.markdown("### Previous Weeks")
    
    if not weekly_summaries:
        st.info("No payment history yet.")
    else:
        for idx, summary in enumerate(weekly_summaries):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**<span style='color: #2563eb;'>{summary['startDate']} - {summary['endDate']}</span>**", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: gray; font-size: 14px;'>{summary['totalHours']:.1f} Hours Worked</span>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div style='text-align: right;'><span style='font-size: 20px; font-weight: bold;'>${summary['netPay']:,.0f}</span><br><span style='font-size: 10px; color: gray; text-transform: uppercase;'>Net Pay</span></div>", unsafe_allow_html=True)
                with col3:
                    if st.button("Export CSV", key=f"export_{idx}"):
                        # Extract the entries for this specific week to export
                        start_dt = datetime.strptime(summary['startDate'], "%m/%d/%Y")
                        end_dt = datetime.strptime(summary['endDate'], "%m/%d/%Y")
                        
                        week_entries_to_export = []
                        for e in entries:
                            try:
                                e_date = datetime.strptime(e['day'], "%Y-%m-%d")
                                if start_dt <= e_date <= end_dt:
                                    week_entries_to_export.append(e)
                            except:
                                pass
                                
                        df = pd.DataFrame(week_entries_to_export)
                        if not df.empty:
                            del df['id'] # optional: Remove DB id from export
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name=f"pay_summary_{summary['startDate'].replace('/', '-')}.csv",
                                mime="text/csv",
                                key=f"dl_{idx}"
                            )
                st.markdown("---")
