#!/usr/bin/env python3

import uvicorn

if __name__ == '__main__':
    uvicorn.run('merlin.visualizer.main:app', host='', port=8050, reload=True, reload_dirs='..')
