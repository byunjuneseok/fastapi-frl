from fastapi import FastAPI, Depends, APIRouter

from frl.algorithms import SimpleAlgorithm
from frl.backend import LimiterBackend
from frl.key import NoKey, KeyByPath
from frl.limiter import Limiter

app = FastAPI()

limiter_backend = LimiterBackend('redis://localhost')
single_limiter = Limiter(
    backend=limiter_backend,
    algorithm=SimpleAlgorithm(threshold=2),
    key_generator=NoKey()
)


@app.get('/', dependencies=[Depends(single_limiter)])
async def root():
    return {'message': 'Hello World'}


api_apple_limiter = Limiter(
    backend=limiter_backend,
    algorithm=SimpleAlgorithm(threshold=10),
    key_generator=KeyByPath()
)
api_apple_router = APIRouter(prefix='/apples', tags=['Apple'], dependencies=[Depends(api_apple_limiter)])


@api_apple_router.get('/')
async def list_apples():
    return [
        {
            'apple_id': 3,
            'apple_name': 'Strawberry flavoured apple'
        },
        {
            'apple_id': 5,
            'apple_name': 'Durian flavoured apple'
        }
    ]


@api_apple_router.post('/{apple_id}/', status_code=201)
async def create_apples():
    return {
        'apple_id': '6',
        'apple_name': 'iMac with M1 Ultra'
    }


app.include_router(api_apple_router)
