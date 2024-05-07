from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from importlib.resources import files

import merlin
from merlin.endpoints import datasets, features, mds, transient, download, label, clusters


app = FastAPI()

app.include_router(datasets.router, prefix='/api')
app.include_router(features.router, prefix='/api')
app.include_router(transient.router, prefix='/api')
app.include_router(download.router, prefix='/api')
app.include_router(mds.router, prefix='/api')
app.include_router(label.router, prefix='/api')
app.include_router(clusters.router, prefix='/api')


def run():
    static_path = files(merlin).joinpath('static')
    app.mount('/', StaticFiles(directory=static_path, html=True), name='static')
    uvicorn.run('merlin.main:app', host='', port=8050)
