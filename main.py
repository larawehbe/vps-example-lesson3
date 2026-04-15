from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine
import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/todos", response_model=schemas.TodoOut)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    new_todo = models.Todo(title=todo.title)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.get("/todos", response_model=list[schemas.TodoOut])
def get_todos(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()

@app.patch("/todos/{todo_id}", response_model=schemas.TodoOut)
def update_todo(todo_id: int, update: schemas.TodoUpdate, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.done = update.done
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Deleted"}
