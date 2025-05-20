from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# قراءة ملفات الإكسل
employees_df = pd.read_excel('employees.xlsx')
managers_df = pd.read_excel('managers.xlsx')

# تحويل تاريخ انتهاء العقد إلى نوع datetime
employees_df['تاريخ انتهاء العقد'] = pd.to_datetime(employees_df['تاريخ انتهاء العقد'], errors='coerce')

# تنظيف الأكواد من الفراغات وتحويلها إلى سترينج
employees_df['كود المدير المباشر'] = employees_df['كود المدير المباشر'].astype(str).str.strip()
employees_df['كود الموارد البشرية'] = employees_df['كود الموارد البشرية'].astype(str).str.strip()
employees_df['كود مدير المنطقة'] = employees_df['كود مدير المنطقة'].astype(str).str.strip()

# قرارات التقييم مخزنة في قاموس (يمكن ربطها بقاعدة بيانات لاحقاً)
decisions = {}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code = str(request.form['code']).strip()
        password = request.form['password'].strip()

        managers_df['code'] = managers_df['code'].astype(str).str.strip()
        managers_df['password'] = managers_df['password'].astype(str).str.strip()

        manager = managers_df[(managers_df['code'] == code) & (managers_df['password'] == password)]

        if not manager.empty:
            session['manager'] = manager.iloc[0].to_dict()
            return redirect(url_for('employees'))
        else:
            error = 'بيانات الدخول غير صحيحة'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/employees')
def employees():
    if 'manager' not in session:
        return redirect(url_for('login'))

    manager = session['manager']
    role = manager['role']
    code = str(manager['code']).strip()

    role_column_map = {
        'manager': 'كود المدير المباشر',
        'hr': 'كود الموارد البشرية',
        'region_manager': 'كود مدير المنطقة'
    }
    column = role_column_map.get(role)
    if not column:
        return 'دور المدير غير معروف'

    today = datetime.today()
    one_month_later = today + timedelta(days=30)

    filtered = employees_df[
        (employees_df[column] == code) &
        (employees_df['تاريخ انتهاء العقد'] >= today) &
        (employees_df['تاريخ انتهاء العقد'] <= one_month_later)
    ]

    # التحقق إذا تم تقديم القرار لكل الموظفين المعروضين للمدير الحالي حسب دوره
    has_submitted = True
    for emp_code in filtered['كود']:
        try:
            key = (int(emp_code), role)
            if key not in decisions:
                has_submitted = False
                break
        except:
            # لو الكود ليس رقم صحيح نتجاهله هنا (أو تعامل مع الخطأ حسب الحاجة)
            has_submitted = False
            break

    message = "تم التقديم بالفعل. لا يمكنك تعديل القرارات." if has_submitted else None

    return render_template('employees.html',
                           employees=filtered.to_dict(orient='records'),
                           manager=manager,
                           decisions=decisions,
                           submitted=has_submitted,
                           message=message)

@app.route('/save_decision', methods=['POST'])
def save_decision():
    if 'manager' not in session:
        return jsonify({'status': 'error', 'message': 'يجب تسجيل الدخول'})

    manager = session['manager']
    role = manager['role']

    data = request.get_json()
    if not data or 'decisions' not in data or len(data['decisions']) == 0:
        return jsonify({'status': 'error', 'message': 'لم يتم إرسال أي قرار'})

    # تحقق من عدم تقديم قرارات مسبقاً لأي موظف من قبل هذا المدير (دوره)
    for d in data['decisions']:
        try:
            key = (int(d['employee_code']), role)
            if key in decisions:
                return jsonify({'status': 'error', 'message': 'تم التقديم بالفعل ولا يمكن تعديل القرارات'})
        except:
            return jsonify({'status': 'error', 'message': 'كود موظف غير صالح'})

    # حفظ القرارات الجديدة
    for decision in data['decisions']:
        try:
            key = (int(decision['employee_code']), decision['role'])
            decisions[key] = decision['decision']
        except:
            return jsonify({'status': 'error', 'message': 'خطأ في حفظ القرار'})

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
