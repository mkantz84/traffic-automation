from fastapi import APIRouter

router = APIRouter()

@router.post("/submit_permutations")
def submit_permutations():
    return {"message": "Not implemented yet"} 