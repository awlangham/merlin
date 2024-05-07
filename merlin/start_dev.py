#!/usr/bin/env python3

import uvicorn
from fastapi.staticfiles import StaticFiles

from merlin.main import app

static_path = '../frontend/build'
app.mount('/', StaticFiles(directory=static_path, html=True), name='static')


if __name__ == '__main__':
    uvicorn.run('merlin.main:app', host='', port=8050, reload=True)
