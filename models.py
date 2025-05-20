from extensions import db

class Manager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    department = db.Column(db.String(100))
    region = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    role = db.Column(db.String(50))

class RenewalDecision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(50), nullable=False)
    manager_code = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20))  # manager | hr | region_manager
    decision = db.Column(db.String(10))  # 'yes' أو 'no'
