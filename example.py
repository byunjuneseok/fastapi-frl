from fastapi import FastAPI, Depends, APIRouter, HTTPException

from fastapi_frl import LimiterBackend, Limiter
from fastapi_frl.algorithms import SimpleAlgorithm, FixedWindowCounter, SlidingWindowCounter
from fastapi_frl.key import NoKey, KeyByPath

app = FastAPI()

limiter_backend = LimiterBackend('redis://localhost')
single_limiter = Limiter(
    name='single_limiter',
    algorithm=SimpleAlgorithm(threshold=2),
    key_generator=NoKey()
)


@app.get('/', dependencies=[Depends(single_limiter)])
async def root():
    return {'message': 'Hello World'}


api_fruit_limiter = Limiter(
    name='api_fruit_limiter',
    algorithm=SimpleAlgorithm(threshold=10),
    key_generator=KeyByPath(),
    exception=HTTPException(status_code=503, detail='Too many requests for Apples API. (10 hits per minutes allowed)')
)
api_fruit_router = APIRouter(prefix='/fruits', tags=['Apple'], dependencies=[Depends(api_fruit_limiter)])


@api_fruit_router.get('/')
async def list_fruits():
    return [
        {
            'fruit_id': 3,
            'fruit_name': 'Strawberry flavoured apple'
        },
        {
            'fruit_id': 5,
            'fruit_name': 'Durian flavoured banana'
        }
    ]


@api_fruit_router.post('/{fruit_id}/', status_code=201)
async def create_fruits():
    return {
        'fruit_id': '6',
        'fruit_name': 'iMac with M1 Ultra'
    }


app.include_router(api_fruit_router)


api_animal_limiter = Limiter(
    name='api_animal_limiter',
    algorithm=FixedWindowCounter(1, 3),
    key_generator=KeyByPath(),
)
api_animal_router = APIRouter(prefix='/animals', tags=['Animals'], dependencies=[Depends(api_animal_limiter)])


@api_animal_router.get('/{animal_id}/')
async def get_fruits(animal_id: str):

    return {
        'requested_id': animal_id,
        'animal_id': f'#{animal_id} - Monkey'
    }


app.include_router(api_animal_router)


api_book_limiter = Limiter(
    name='api_book_limiter',
    algorithm=SlidingWindowCounter(10, 10),
    key_generator=KeyByPath(),
)
api_book_router = APIRouter(prefix='/books', tags=['Book'], dependencies=[Depends(api_book_limiter)])


@api_book_router.get('/{book_id}/')
async def get_books(book_id: str):

    return {
        'requested_id': book_id,
        'book': 'Book!'
    }


app.include_router(api_book_router)
