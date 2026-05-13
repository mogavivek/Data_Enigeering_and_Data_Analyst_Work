from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel # This useful when we have to put something

app = FastAPI() # make instance so we can access later

# amazon.com/create_user: so in this url create_user is the end point

# GET - Get an information
# POST - Create something new
# PUT - Update
# DELETE - delete somthing

# Run in the command prompt where path will be your file is saved: python -m uvicorn main:app --reload
# Open cmd terminal and then wirte: netstat -ano | findstr :8000
# Then write in terminal: taskkill /PID 12972 /F

students = {
    1: {
        "name": "Hello",
        "age": 17,
        "class": "year 12"
    },
    2: {
        "name": "World",
        "age": 15,
        "class": "year 10"
    }
}

# suppose we have to update the value or want to add something, then it is not good to do it in main class
class Student(BaseModel):
    name: str
    age:int
    year: str

# so instead of that create a new class
class UpdateStudent(BaseModel):
    name: Optional[str] = None # optional we need so we do not have to write compulsory
    age:Optional[int] = None
    year: Optional[str]=None

# create a new api
@app.get("/") # / shows the endpoint in URL
def index():
    return {"name": "First Data"}


# Path parameters
@app.get("/get_students/{student_id}") # get_students the endpoint in URL, so this will look like, google.com/get_students/1
def get_student(student_id: int = Path(None, description="The ID of the student you want to view", gt=0)): # gt=0 gives that the number should be greter than zero
    return students[student_id]

# query Parameters
# Suppose we have google.com/results?search=python, in this URL search=python is the query parameters

@app.get("/get-by-name")
# inside the function *, is required so we can pass any inputs like Optional, test and all
def get_student_name(*, name:Optional[str]= None, test:int): # def get_student_name(name:str=None) then it will remove required part
    for student_id in students:
        if students[student_id]["name"] == name:        # we are doing like /get-by-name?name=Hello, where hello will come as input parameter
            return students[student_id]
    return {"Data": "Not found"} 


# ------- Combining Path and Query Parameters ------------ 
@app.get("/get-by-name/{student_id}")
# inside the function *, is required so we can pass any inputs like Optional, test and all
def get_student_name(*, student_id:int, name:Optional[str]= None, test:int): # def get_student_name(name:str=None) then it will remove required part
    for student_id in students:
        if students[student_id]["name"] == name:        # we are doing like /get-by-name?name=Hello, where hello will come as input parameter
            return students[student_id]
    return {"Data": "Not found"} 


# ------- Request Body and The post Methods ------------ 
@app.post("/create_student/{student_id}") # we are providing evertime student_id for a better path
def create_students(student_id:int, student:Student):
    if student_id in student:
        return {"Error": "Student exsists"}
    
    student[student_id] = student
    return student[student_id] # when in page it will ask to add the details of the stdents

# ------- put Methods ------------

@app.put("/update_student/{student_id}")
def update_student(student_id:int, student: UpdateStudent):
    if student_id not in student:
        return {"Error": "Student does not exsist"}
    
    # The below if loops required because if we just add the students name only then other will remain as it is as before
    # If we not write below things then is till make null if we do not write anything
    if student.name != None:
        students[student_id].name = student.name 
    if student.age != None:
        students[student_id].age = student.age
    if student.year != None:
        students[student_id].year = student.year     
    return students[student_id]


# ------- Delete Methods ------------
@app.delete("/delete_student/{student_id}")
def delete_student(student_id: int, student: Student):
    if student_id not in student:
        return {"Error": "Student does not exsist"}
    del student[student_id]
    return {"message": "Student deleted successfully"}