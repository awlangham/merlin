#!/usr/bin/env python3

import uvicorn
from merlin.main import app

if __name__ == '__main__':
    uvicorn.run('merlin.main:app', host='', port=8050, reload=True)
