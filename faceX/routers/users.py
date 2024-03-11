from fastapi import APIRouter, status, Path, HTTPException
from models.user import UserCreatedResponse, UserDetailsRequest, UserUpdateRequest, DeleteUserResponse
from utils.database_connect import connection
from typing import Optional, List
from utils.password_manager import encryptPassword

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

try:
    print("database connected~!")
    conn = connection()
except Exception:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to reach Database")


def isUserPresent(user_id: int = None, email: str = None, name: str = None, profession: str = None):
    if not (user_id is not None or email is not None or name is not None or profession is not None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No parameters passed.")

    query = "SELECT user_id, name, email, password, profession, about, created_at from users"
    values = []
    # Everything we can fetch from just user_id only, so no extra info needed, if user_id present.
    if user_id is not None:
        query += " WHERE user_id=%s"
        values.append(user_id)

        if email is not None:
            query += " or email=%s"
            values.append(email)

    else:
        if name is not None and profession is not None:
            query += " WHERE name=%s and profession=%s"
            values.append(name)
            values.append(profession)

        elif name is not None:
            print("here")
            query += " WHERE name=%s"
            values.append(name)

        else:
            query += " WHERE profession=%s"
            values.append(profession)

    cursor = conn.cursor()
    print(query, values)
    cursor.execute(query, tuple(values))
    users = cursor.fetchall()
    cursor.close()

    return [{"user_id": user[0], "name": user[1], "email": user[2], "password": user[3], "profession": user[4], "about": user[5], "created_at": str(user[6])} for user in users]


def createUserEntry(userDetails: UserDetailsRequest):
    query = "INSERT INTO users(user_id, name, email, password, profession, about) VALUES(%s, %s, %s, %s, %s, %s);"

    userDetails.password = encryptPassword(userDetails.password)
    cursor = conn.cursor()
    cursor.execute(query, (userDetails.user_id, userDetails.name, userDetails.email, userDetails.password, userDetails.profession, userDetails.about,))
    conn.commit()
    cursor.close()
    
    return [{"user_id": userDetails.user_id, "name": userDetails.name, "email": userDetails.email, "profession": userDetails.profession, "about": userDetails.about, "created_at": userDetails.created_at}]


def updateUserEntry(user: dict, userUpdate: UserUpdateRequest):
    name = userUpdate.name if userUpdate.name != "" else user["name"]
    email = userUpdate.email if userUpdate.email != "sample@example.com" else user["email"]
    password = userUpdate.password if userUpdate.password != "" else user["password"]
    password = encryptPassword(password)
    profession = userUpdate.profession if userUpdate.profession != "" else user["profession"]
    about = userUpdate.about if userUpdate.about != "" else user["about"]

    query = "UPDATE users SET name=%s, email=%s, password=%s, profession=%s, about=%s where user_id=%s;"

    cursor = conn.cursor()
    cursor.execute(query, (name, email, password, profession, about, user["user_id"]))
    conn.commit()
    cursor.close()
    
    return [{"user_id": user["user_id"], "name": name, "email": email, "profession": profession, "about": about, "created_at": str(user["created_at"])}]



def deleteUserEntry(userDetails: dict):
    query = "DELETE from users where user_id=%s;"

    cursor = conn.cursor()
    cursor.execute(query, (userDetails["user_id"],))
    conn.commit()
    cursor.close()
    
    return [{"user_id": userDetails["user_id"], "name": userDetails["name"], "email": userDetails["email"], "timestramp": str(userDetails["created_at"])}]

@router.post("/create-user", status_code=status.HTTP_201_CREATED, response_model=List[UserCreatedResponse])
def createUser(userDetails: UserDetailsRequest):
    # Check with user_id or email both are valid.
    user = isUserPresent(user_id=userDetails.user_id, email=userDetails.email)
    if len(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already Exists!")

    response = createUserEntry(userDetails)
    return response


@router.put("/update-user/{user_id}", status_code=status.HTTP_200_OK, response_model=List[UserCreatedResponse])
def updateUser(userUpdate: UserUpdateRequest, user_id: int = Path(description="Valid User Id to Update")):
    user = isUserPresent(user_id)
    print("user = ", user)

    if not len(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Does not exists")
    user = user[0]
    response = updateUserEntry(user, userUpdate) #Also apply a check for updating to same user's email.
    return response


@router.delete("/delete-user/{user_id}", status_code=status.HTTP_200_OK, response_model=List[DeleteUserResponse])
def deleteUser(user_id: int = Path(description="Valid User Id to Delete")):
    user = isUserPresent(user_id)
    if not len(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Does not exists")
    user = user[0]
    response = deleteUserEntry(user)
    return response


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK, response_model=List[UserCreatedResponse])
def getUser(user_id: int = Path(description="Valid User Id to Delete")):
    user = isUserPresent(user_id)
    if not len(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Does not exists")
    [cred.pop("password") for cred in user]
    return user


@router.get("/user/name/{name}", status_code=status.HTTP_200_OK, response_model=List[UserCreatedResponse])
def getUser(name: str = Path(description="Valid User's Name")):
    user = isUserPresent(name=name)
    if not len(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Does not exists")
    
    [cred.pop("password") for cred in user]
    return user


@router.get("/user/profession/{profession}", status_code=status.HTTP_200_OK, response_model=List[UserCreatedResponse])
def getUser(profession: str = Path(description="Valid User's Profession")):
    user = isUserPresent(profession=profession)
    if not len(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Profession Does not exists")

    [cred.pop("password") for cred in user]
    return user
