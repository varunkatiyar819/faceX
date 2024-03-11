from fastapi import APIRouter, status, Path, HTTPException, Depends
from models.post import postCreatedResponse, postDetailsRequest, postUpdateRequest, DeletepostResponse
from utils.database_connect import connection
from typing import List
from utils.oauth2 import get_current_user
from models.user  import UserDetailsRequest
router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

try:
    conn = connection()
except Exception:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to reach Database")

def ispostPresent(post_id: int = None, category: str = None, title: str = None):
    if not (post_id is not None or category is not None or title is not None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No parameters passed.")

    query = "SELECT post_id, owner_id, category, title, content, image, created_at from posts"
    values = []
    # Everything we can fetch from just post_id only, so no extra info needed, if post_id present.
    if post_id is not None:
        query += " WHERE post_id=%s"
        values.append(post_id)

        if title is not None:
            query += " or title=%s"
            values.append(title)

    else:
        if category is not None and title is not None:
            query += " WHERE category=%s and title=%s"
            values.append(category)
            values.append(title)

        elif category is not None:
            print("here")
            query += " WHERE category=%s"
            values.append(category)

        else:
            query += " WHERE title=%s"
            values.append(title)

    cursor = conn.cursor()
    print(query, values)
    cursor.execute(query, tuple(values))
    posts = cursor.fetchall()
    cursor.close()

    return [{"post_id": user[0], "category": user[2], "title": user[3], "content": user[4], "image": user[4], "owner_id": user[1], "created_at": str(user[6])} for user in posts]


def createpostEntry(postDetails: postDetailsRequest, owner_id: int):
    query = "INSERT INTO posts(post_id, category, title, content, image, owner_id) VALUES(%s, %s, %s, %s, %s, %s);"

    cursor = conn.cursor()
    cursor.execute(query, (postDetails.post_id, postDetails.category, postDetails.title, postDetails.content, postDetails.image, owner_id))
    conn.commit()
    cursor.close()
    
    return [{"post_id": postDetails.post_id, "category": postDetails.category, "title": postDetails.title, "content": postDetails.content, "image": postDetails.image, "created_at": str(postDetails.created_at), "owner_id": owner_id}]


def updatepostEntry(post: dict, postUpdate: postUpdateRequest):
    print(post)
    category = postUpdate.category if postUpdate.category != "" else post["category"]
    title = postUpdate.title if postUpdate.title != "" else post["title"]
    content = postUpdate.content if postUpdate.content != "" else post["content"]
    image = postUpdate.image if postUpdate.image != "" else post["image"]

    query = "UPDATE posts SET category=%s, title=%s, content=%s, image=%s where post_id=%s;"

    cursor = conn.cursor()
    cursor.execute(query, (category, title, content, image, post["post_id"]))
    conn.commit()
    cursor.close()
    
    return [{"post_id": post["post_id"], "category": category, "title": title, "content": content, "image": image, "created_at": str(post["created_at"])}]

def deletepostEntry(postDetails: tuple):
    query = "DELETE from posts where post_id=%s;"

    cursor = conn.cursor()
    cursor.execute(query, (postDetails["post_id"],))
    conn.commit()
    cursor.close()
    
    return [{"post_id": postDetails["post_id"], "category": postDetails["category"], "title": postDetails["title"], "timestramp": str(postDetails["created_at"])}]

@router.post("/create-post", status_code=status.HTTP_201_CREATED, response_model=postCreatedResponse)
def createpost(postDetails: postDetailsRequest, userDetails: dict = Depends(get_current_user)):
    print("userDetails = ", userDetails)
    post = ispostPresent(post_id=postDetails.post_id, title=postDetails.title)
    if len(post):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already Exists!")

    response = createpostEntry(postDetails, userDetails["user_id"])[0]
    print(userDetails["user_id"])
    response.update({"owner_id": userDetails["user_id"]})
    return response

@router.put("/update-post/{post_id}", status_code=status.HTTP_200_OK, response_model=postCreatedResponse)
def updatepost(postUpdate: postUpdateRequest, creds: UserDetailsRequest = Depends(get_current_user), post_id: int = Path(description="Valid post Id to Update")):
    post = ispostPresent(post_id)

    if not len(post):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="post Does not exists")
    post = post[0]
    if post["owner_id"] != creds["user_id"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")
    
    response = updatepostEntry(post, postUpdate)[0]#Also apply a check for updating to same title.
    response.update({"owner_id": creds["user_id"]})
    return response

@router.delete("/delete-post/{post_id}", status_code=status.HTTP_200_OK, response_model=List[DeletepostResponse])
def deletepost(post_id: int = Path(description="Valid post Id to Delete"), creds: dict = Depends(get_current_user)):
    post = ispostPresent(post_id)
    if not len(post):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="post Does not exists")
    post = post[0]
    print("Values = ", post["owner_id"], creds["user_id"])
    if post["owner_id"] != creds["user_id"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")
    response = deletepostEntry(post)
    return response

@router.get("/post/{post_id}", status_code=status.HTTP_200_OK, response_model=List[postCreatedResponse])
def getpost(post_id: int = Path(description="Valid post Id to Delete")):
    post = ispostPresent(post_id)
    if not len(post):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="post Does not exists")

    return post

@router.get("/post/category/{category}", status_code=status.HTTP_200_OK, response_model=List[postCreatedResponse])
def getpost(category: str = Path(description="Valid post's Name")):
    post = ispostPresent(category=category)
    if not len(post):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="post Does not exists")
    
    return post

@router.get("/post/title/{title}", status_code=status.HTTP_200_OK, response_model=List[postCreatedResponse])
def getpost(title: str = Path(description="Valid post's Profession")):
    post = ispostPresent(title=title)
    if not len(post):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Profession Does not exists")
    
    return post

