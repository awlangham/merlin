.. Merlin documentation master file, created by
   sphinx-quickstart on Tue Jun 11 11:57:54 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MERLIN: Microgrid Event Recognition and Load Identification Network
====================================================================

MERLIN aims to simplify the process of setting up data-driven energy monitoring systems.
Built on the `Joule <https://wattsworth.net/joule/>`_ distributed signal processing framework,
MERLIN takes a stream of transient events and performs unsupervised, semi-supervised, or supervised
analysis.

At the core of MERLIN is an emphasis on interpretable feature spaces and transformations. An
interactive web-based feature space visualization tool allows for quick examination of the
participants on an energy monitoring system.

MERLIN provides three interfaces: a command line interface, a Joule processing module, and
a web-based visualization tool.

.. toctree::
   :maxdepth: 3

   levels
   cli
   filters
   visualizer