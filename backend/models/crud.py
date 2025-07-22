from backend.db import SessionLocal
from backend.models.models import Task, Feedback
from backend.models.task_model import TaskCreate
from backend.models.task_model import TaskUpdate
from backend.db import init_db


init_db()

def get_tasks():
    db = SessionLocal()
    tasks = db.query(Task).all()
    db.close()
    return tasks

def create_task(task_data: TaskCreate):
    db = SessionLocal()
    task = Task(title=task_data.title)
    db.add(task)
    db.commit()
    db.refresh(task)
    db.close()
    return task

def delete_task(task_id: int):
    db = SessionLocal()
    task = db.query(Task).get(task_id)
    if not task:
        db.close()
        return False
    db.delete(task)
    db.commit()
    db.close()
    return True

def mark_done(task_id: int):
    db = SessionLocal()
    task = db.query(Task).get(task_id)
    if not task:
        db.close()
        return False
    task.is_done = True
    db.commit()
    db.close()
    return True

def update_task(task_id: int, update_data: TaskUpdate):
    db = SessionLocal()
    task = db.query(Task).get(task_id)
    if not task:
        db.close()
        return None
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    db.close()
    return task

def delete_all_tasks():
    db = SessionLocal()
    db.query(Task).delete()
    db.commit()
    db.close()

def add_feedback(task_id: int, rating: int = None, comment: str = None):
    db = SessionLocal()
    feedback = Feedback(task_id=task_id, rating=rating, comment=comment)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    db.close()
    return feedback

def get_feedback_for_task(task_id: int):
    db = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.task_id == task_id).all()
    db.close()
    return feedback
