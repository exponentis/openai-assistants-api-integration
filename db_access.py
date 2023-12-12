import pandas as pd

import database
from models import XConversation,  XRunDetail
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import Session
import datetime


engine = database.get_engine()

def store(data):
    data.created_at=datetime.datetime.now() #TODO

    with Session(engine) as session:
        session.add(data)
        session.commit()

def get_all(entity):
    session = Session(engine)
    stmt = select(entity)
    return session.scalars(stmt).all()

def get_conversation(thread_id):
    session = Session(engine)
    stmt = select(XConversation).where(XConversation.thread_id == thread_id)
    return session.scalars(stmt).all()

def get_all_as_df(entity):
    session = Session(engine)
    stmt = select(entity)
    df_data = pd.read_sql(stmt, con = session.bind)
    return df_data

def get_all_as_dict(entity):
    row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
    all = get_all(entity)
    return list(map(row2dict, all))

def get_run_steps_as_df():
    session = Session(engine)
    stmt = select(XRunDetail, func.count(XRunDetail.id).label("num_calls")).group_by("run_id").order_by("created_at")
    df_data = pd.read_sql(stmt, con = session.bind)
    return df_data

