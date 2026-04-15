from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str

class TodoUpdate(BaseModel):
    done: bool

class TodoOut(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        from_attributes = True
