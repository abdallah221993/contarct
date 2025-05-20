from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

# إعداد قاعدة البيانات
engine = create_engine('sqlite:///managers.db')
Base = declarative_base()

# تعريف نموذج المدير مطابق للتعريف في app.py
class Manager(Base):
    __tablename__ = 'manager'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)  # الباسورد هنا نص عادي أو مشفر
    department = Column(String)
    region = Column(String)
    branch = Column(String)

Session = sessionmaker(bind=engine)
session = Session()

# جلب كل المديرين
managers = session.query(Manager).all()

for m in managers:
    # نتحقق إذا الباسورد مش مشفر (نفحص لو الباسورد غير مخزن كهاش)
    # طريقة بسيطة: لو الباسورد يبدأ بـ 'pbkdf2:' أو 'scrypt:' يعني مشفر، وإلا نص عادي
    if not (m.password.startswith('pbkdf2:') or m.password.startswith('scrypt:')):
        print(f"تشفير الباسورد للمدير: {m.email}")
        m.password = generate_password_hash(m.password)
        session.add(m)

session.commit()
print("تم تحديث وتشفير كلمات المرور بنجاح.")
