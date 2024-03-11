from fastapi import APIRouter, status, Path, HTTPException, Depends, Query
from utils.database_connect import connection
from typing import List
from utils.oauth2 import get_current_user
from models.comment import commentRequest, commentResponse, commentUpdate, commentDeleteResponse
from routers.posts import ispostPresent

router = APIRouter(
    prefix="/comment",
    tags=["comments"]
)

try:
    conn = connection()
except Exception:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to reach Database")

def createCommentEntry(commentDetails: commentRequest, post_id: int, user_id: int):
    query = "INSERT INTO comments(post_id, user_id, comment) VALUES(%s, %s, %s);"

    cursor = conn.cursor()
    cursor.execute(query, (post_id, user_id, commentDetails.comment))
    conn.commit()
    cursor.close()
    
    return [{"post_id": post_id, "modified_at": str(commentDetails.modified_at), "user_id": user_id, "comment": commentDetails.comment}]


def updateCommentEntry(post_id: int, user_id: int, commUpdate: commentUpdate):
    category = commUpdate.comment if commUpdate.comment != "" else post["comment"]


    query = "UPDATE posts SET comment=%s where post_id=%s and user_id=%s;"

    cursor = conn.cursor()
    cursor.execute(query, (commentRetrieve["comment", post_id, user_id]))
    conn.commit()
    cursor.close()
    
    return [{"post_id": commentDetails.post_id, "modified_at": str(commentDetails.modified_at), "user_id": user_id, "comment": commentDetails.comment}]


def deleteCommentEntry(postDetails: tuple):
    query = "DELETE from posts where post_id=%s;"

    cursor = conn.cursor()
    cursor.execute(query, (postDetails["post_id"],))
    conn.commit()
    cursor.close()
    
    return [{"post_id": postDetails["post_id"], "category": postDetails["category"], "title": postDetails["title"], "timestramp": str(postDetails["modified_at"])}]


def isCommentedByUser(post_id, comment_id, user_id):
    query = "SELECT post_id, user_id, comment_id, comment from comments where post_id=%s AND comment_id=%s AND user_id=%s"

    cursor = conn.cursor()
    cursor.execute(query, (post_id, comment_id, user_id))
    commentPresent = cursor.fetchall()
    conn.close()

    if not len(commentPresent):
        return []

    return [{"post_id": comment[0][0], "user_id" : comment[0][1], "comment_id": comment[0][2], "comment" : comment[0][3]} for comment in commentPresent]

@router.post("/{post_id}/create-comment", status_code=status.HTTP_201_CREATED, response_model=commentResponse)
def create_comment(post_id: int, commentDetails: commentRequest, userDetails: dict = Depends(get_current_user)):
    post = ispostPresent(post_id=post_id)
    if len(post):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already Exists!")

    response = createCommentEntry(commentDetails, post_id, userDetails["user_id"])[0]
    response.update({"user_id": userDetails["user_id"]})
    return response

@router.post("/{post_id}/update-comment/", status_code=status.HTTP_200_OK, response_model=commentUpdate)
def update_comment(commUpdate: commentUpdate, creds: dict = Depends(get_current_user), post_id: int = Path(description="Valid post Id to Update")):
    post = ispostPresent(post_id)
    if not len(post):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="post Does not exists")
    post = post[0]

    isComment = isCommentedByUser(post_id, commUpdate.comment_id, creds["user_id"])[0]
    if not len(isComment):

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment Not Found")
    
    response = updateCommentEntry(isComment, commUpdate)[0]#Also apply a check for updating to same title.
    response.update({"user_id": creds["user_id"]})
    return response


@router.post("/{post_id}/delete-comment", status_code=status.HTTP_200_OK, response_model=List[commentDeleteResponse])
def delete_comment(post_id: int = Path(description="Valid post Id to Delete"), creds: dict = Depends(get_current_user)):
    post = ispostPresent(post_id)
    if not len(post):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="post Does not exists")
    post = post[0]
    print("Values = ", post["owner_id"], creds["user_id"])
    if post["owner_id"] != creds["user_id"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")
    response = deleteCommentEntry(post)
    return response

#Apply Path Parameters here for user, limit, offset etc..
@router.get("/{post_id}/get-all-comments-by-post", status_code=status.HTTP_200_OK, response_model=List[commentResponse])
def view_all_comments_for_specific_post(post_id: int = Path(description="Valid post Id to Delete"), limit: int = Query(), offset: int = Query(), name: str = Query()):
    post = ispostPresent(post_id)
    if not len(post):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="post Does not exists")

    return post

#Apply Path Parameters here for user, limit, offset etc..
@router.get("/{post_id}/get-all-comment-by-users", status_code=status.HTTP_200_OK, response_model=List[commentResponse])
def view_all_comments_for_specific_user(post_id: int = Path(description="Valid post Id to Delete"), limit: int = Query(), offset: int = Query()):
    post = ispostPresent(post_id)
    if not len(post):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="post Does not exists")

    return post