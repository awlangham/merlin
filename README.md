Microgrid Event Recognition and Load Identification Network (MERLIN)
========

A pipeline and visualization platform for electrical event recognition with a custom degree of supervision.

Development
------------

Install merlin for development by cloning this repository and opening it in a terminal. Then run

    pip -m venv venv
    source venv/bin/activate
    pip install -e .

This creates a new Python virtual environment and installs merlin in editable mode, so that changes to the source code are immediately reflected in the virtual environment's installation.

To run the development version of the visualization back-end, open a terminal in merlin/merlin and run ``./start_dev.sh``.
For the visualization front-end, open a terminal in merlin/frontend and run ``./start_dev.sh``. Note that [Node.js](https://nodejs.org) must be installed for merlin front-end development.

To run a development server for the [Sphinx](https://www.sphinx-doc.org) documentation, open a terminal in merlin/docs and run ``./start_dev.sh``.
