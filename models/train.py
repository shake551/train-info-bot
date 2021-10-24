from config.config import db

class TrainData(db.Model):
    __tablename__ = 'train'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    info = db.Column(db.String(200))
