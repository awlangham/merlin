import os
from fastapi import FastAPI
import subprocess
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
    new_env = os.environ.copy()
    new_env['PORT'] = '8050'
    with subprocess.Popen(['node', 'build'], cwd=files(merlin).joinpath('frontend'), env=new_env):
        uvicorn.run('merlin.main:app', host='', port=8051)
