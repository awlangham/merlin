from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from importlib.resources import files
import click

import merlin
from merlin.visualizer import datasets, features, transient, download, label, learn, config


app = FastAPI()
app.node = ''

app.include_router(datasets.router, prefix='/api')
app.include_router(features.router, prefix='/api')
app.include_router(transient.router, prefix='/api')
app.include_router(download.router, prefix='/api')
# app.include_router(mds.router, prefix='/api')
app.include_router(label.router, prefix='/api')
app.include_router(learn.router, prefix='/api')
# app.include_router(clusters.router, prefix='/api')
app.include_router(config.router, prefix='/api')


@click.command()
@click.option('--node', '-n', default='', help='Joule node to use (uses default if unspecified).')
def run(node) -> None:
    app.node = node
    static_path = files(merlin).joinpath('static')
    app.mount('/', StaticFiles(directory=static_path, html=True), name='static')
    uvicorn.run('merlin.visualizer.main:app', port=8050)
