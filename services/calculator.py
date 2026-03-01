from datetime import datetime

def calculate_weekly_pay(entries, settings):
    total_minutes = sum(entry['duration'] for entry in entries if entry.get('duration'))
    total_hours = total_minutes / 60.0
    
    salary_settings = settings.get('salary', {})
    deduction_settings = settings.get('deductions', {})
    
    hourly_rate = float(salary_settings.get('hourlyRate', 0))
    ot_threshold = float(salary_settings.get('otThreshold', 40))
    ot_multiplier = float(salary_settings.get('otMultiplier', 1.5))

    regular_hours = min(total_hours, ot_threshold)
    overtime_hours = max(0, total_hours - ot_threshold)

    gross_pay = (regular_hours * hourly_rate) + (overtime_hours * hourly_rate * ot_multiplier)

    # Pre-tax 401k
    k401_employee = 0
    if deduction_settings.get('isK401Percent', False):
        k401_employee = gross_pay * (float(deduction_settings.get('k401EmployeePercent', 0)) / 100.0)
    else:
        k401_employee = float(deduction_settings.get('k401EmployeeAmount', 0))

    insurance_deductions = (
        float(deduction_settings.get('healthEmployee', 0)) + 
        float(deduction_settings.get('dentalEmployee', 0)) + 
        float(deduction_settings.get('visionEmployee', 0))
    )

    total_deductions = k401_employee + insurance_deductions
    net_pay = max(0, gross_pay - total_deductions)

    # Hidden/Report Logic: Total Compensation
    employer_401k_match = k401_employee * (float(deduction_settings.get('k401EmployerMatchPercent', 0)) / 100.0)
    employer_insurance = (
        float(deduction_settings.get('healthEmployer', 0)) + 
        float(deduction_settings.get('dentalEmployer', 0)) + 
        float(deduction_settings.get('visionEmployer', 0))
    )
    
    total_compensation = gross_pay + employer_401k_match + employer_insurance

    # Find start/end dates from entries
    if entries:
        try:
            dates = [datetime.strptime(e['day'], "%Y-%m-%d").timestamp() for e in entries if e.get('day')]
            start_date = datetime.fromtimestamp(min(dates)).strftime("%m/%d/%Y") if dates else 'N/A'
            end_date = datetime.fromtimestamp(max(dates)).strftime("%m/%d/%Y") if dates else 'N/A'
        except Exception:
            start_date = 'N/A'
            end_date = 'N/A'
    else:
        start_date = 'N/A'
        end_date = 'N/A'

    return {
        'startDate': start_date,
        'endDate': end_date,
        'totalHours': total_hours,
        'grossPay': gross_pay,
        'netPay': net_pay,
        'totalDeductions': total_deductions,
        'totalCompensation': total_compensation
    }
