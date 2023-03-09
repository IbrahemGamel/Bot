from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
Base = declarative_base()



class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    user_a_id = Column(Integer, nullable=False)
    user_b_id = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    picture_url = Column(JSON, nullable=False)
    time_of_trade = Column(DateTime, nullable=False)
    reason_of_deny = Column(String(255), nullable=True)
    trade_status = Column(String(255), nullable=False)
    
    
    def create_trade(user_a_id: str, user_b_id: str, description: str, picture_url: list, reason_of_deny, trade_status: str) -> None:
        
        new_trade = Trade(user_a_id=user_a_id, user_b_id=user_b_id, description=description, picture_url=picture_url, time_of_trade=datetime.now(), reason_of_deny= reason_of_deny, trade_status=trade_status)
        session.add(new_trade)
        session.commit()




class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    trade_count = Column(Integer, nullable=False)
    is_mod = Column(Boolean, nullable=False)
    
    
    def create_user(user_id: str, trade_count: int) -> None:
        
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            new_user = User(user_id=user_id, trade_count=trade_count, is_mod=False)
            session.add(new_user)
            session.commit()
    

engine = create_engine('sqlite:///DataBase.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
