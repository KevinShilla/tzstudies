import os

class Config:
    raw_db_url = os.getenv("DATABASE_URL", "postgresql://u9o7tguuile3km:pdbc0711015539daf265db61a087a4fc6d094ef8f1db4b7a7b763f88062108034@c3cj4hehegopde.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d1ho4vshg30ue9")

    fixed_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = fixed_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
