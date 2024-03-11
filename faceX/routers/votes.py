from fastapi import APIRouter, status, Path, HTTPException, Depends
from utils.database_connect import connection
from typing import List
from utils.oauth2 import get_current_user
from routers.posts import ispostPresent
from models.vote import voteRequest, voteResponse

router = APIRouter(
    prefix="/vote",
    tags=["votes"]
)

try:
    conn = connection()
except Exception:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to reach Database")

def isPostAlreadyLiked(post_id: int, user_id: int):
    query = "SELECT * from votes WHERE post_id=%s AND user_id=%s"
    cursor = conn.cursor()
    cursor.execute(query, (post_id, user_id))
    presentVotes = cursor.fetchall()
    conn.close()

    return presentVotes

def unlikePost(post_id: int, user_id: int):
    query = "DELETE from votes WHERE post_id=%s AND user_id=%s"
    cursor = conn.cursor()
    cursor.execute(query, (post_id, user_id))
    conn.commit()
    conn.close()

    return dict(voteResponse(post_id, 0, user_id))

def likePost(post_id: int, user_id: int):
    query = "INSERT INTO votes VALUES(%s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (post_id, user_id))
    conn.commit()
    conn.close()

    return dict(voteResponse(post_id, 1, user_id))

def votePost(vote: voteRequest, user_id: int):
    liked = isPostAlreadyLiked(vote.post_id, user_id)
    if not vote.dir:
        if liked:
            return unlikePost(vote.post_id, user_id)#This will delete from the database
    
    else:
        if not liked:
            return likePost(vote.post_id, user_id)#This will insert into database.
        
    raise HTTPException(status_code=400, detail="You haven't liked the post yet!")

def fetchAllVotes(post_id: int):
    query = "SELECT user_id from votes where post_id=%s"
    cursor = conn.cursor()
    cursor.execute(query, (post_id, ))
    votes = cursor.fetchall()
    conn.close()

    return [{"user_id": vot[0]} for vot in votes]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=voteResponse)
def vote(voteDetails: voteRequest, user: dict = Depends(get_current_user)):
    if not len(ispostPresent(voteDetails.post_id)):
        raise HTTPException(status_code=404, detail="Post does not exists")
    
    return votePost(voteDetails, user["user_id"])

@router.post("/{post_id}/get-all-likes", status_code=status.HTTP_201_CREATED, response_model=List[voteResponse])
def vote(post_id: int):
    if not len(ispostPresent(post_id)):
        raise HTTPException(status_code=404, detail="Post does not exists")
    
    return fetchAllVotes(post_id)
    