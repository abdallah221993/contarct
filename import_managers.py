import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# إعداد تطبيق Flask وقاعدة البيانات
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///managers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# نموذج المدير مع الحقول المطلوبة
class Manager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    department = db.Column(db.String(100))
    region = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    role = db.Column(db.String(50))  # 'manager', 'hr', 'region_manager'

# تحديد نوع المدير
def determine_role(row):
    if 'الموارد' in str(row['department']) or str(row['code']) == '893':
        return 'hr'
    elif 'المنطقة' in str(row['department']) or str(row['code']) == '2004':
        return 'region_manager'
    else:
        return 'manager'

# استيراد المديرين من ملف Excel
def import_managers():
    df = pd.read_excel('managers.xlsx')

    with app.app_context():
        db.create_all()  # يتأكد من إنشاء الجداول

        for _, row in df.iterrows():
            role = determine_role(row)
            existing = Manager.query.filter_by(email=row['email']).first()
            if existing:
                print(f"تخطي {row['email']} - موجود مسبقًا")
                continue

            manager = Manager(
                code=row['code'],
                name=row['name'],
                email=row['email'],
                password=str(row['password']),
                department=row['department'],
                region=row['region'],
                branch=row['branch'],
                role=role
            )
            db.session.add(manager)

        db.session.commit()
        print("تم استيراد المديرين بنجاح.")

if __name__ == "__main__":
    import_managers()
