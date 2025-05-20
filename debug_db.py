from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# إعداد الاتصال بقاعدة البيانات
engine = create_engine('sqlite:///managers.db')
Base = declarative_base()

# تعريف نموذج المدير (نفس التعريف اللي في import_managers.py)
class Manager(Base):
    __tablename__ = 'manager'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    department = Column(String)
    region = Column(String)
    branch = Column(String)

# إعداد جلسة الاتصال
Session = sessionmaker(bind=engine)
session = Session()

# طباعة كل المدراء في قاعدة البيانات
all_managers = session.query(Manager).all()
for m in all_managers:
    print(f"{m.email} - {m.password}")
