from fastapi import FastAPI
from fastapi.routing import APIRouter
from routes.instagram import get_ig_photos
import uvicorn

app = FastAPI()
router = APIRouter()
app.add_api_route('/getPhotos', get_ig_photos)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)
