from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bank(db.Model):
    __tablename__ = 'banks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    branches = db.relationship('Branch', backref='bank', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'total_branches': len(self.branches) if self.branches else 0
        }

class Branch(db.Model):
    __tablename__ = 'branches'
    
    id = db.Column(db.Integer, primary_key=True)
    ifsc = db.Column(db.String(20), unique=True, nullable=False, index=True)
    branch = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(50), index=True)
    district = db.Column(db.String(50), index=True)
    state = db.Column(db.String(50), index=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ifsc': self.ifsc,
            'branch': self.branch,
            'address': self.address,
            'city': self.city,
            'district': self.district,
            'state': self.state,
            'bank_id': self.bank_id,
            'bank': self.bank.to_dict() if self.bank else None
        }
