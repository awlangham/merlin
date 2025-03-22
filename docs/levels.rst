Levels of Microgrid Abstraction
-------------------------------

The fundamental units of abstraction in MERLIN are *states* and *transients*.

A state describes a repeatable load behavior with a duration noticeable on a human timescale.
In MERLIN source and documentation, state names are denoted in all capital letters.
The most basic set of states are ``OFF`` and ``ON``.
States have a "steady-state" value associated with each feature.

A transient is a continuous and homogenous block of data with a start and end timestamp.
Transients connect two states of a load's operation. These may be different or the same state.
In MERLIN source and documentation, transient names are denoted with the start state followed by an arrow pointing to thend state.
For example, a transient connecting the ``OFF`` and ``ON`` state would be referred to as ``OFF->ON``.

Both states and transients are associated with individual loads.
In MERLIN source and documentation, when referring to a particular load's state or transient, the name of the load followed by "::"
is placed in front of the state or transient name. For example, ``Fridge::ON`` is the state of the Fridge after a ``Fridge::OFF->ON`` transient.

Combining the states and transients model forms the next layer of abstraction, the *finite state machine (FSM)*. This is a collection of
states and transients associated with a load. This can be visually represented with a directed graph. Vertices (nodes) correspond to states and
edges (arrows) correspond to transients.

The following layer of abstraction is the *schedule*. The schedule describes when transitions between states occur. For example, a load may
transition on a fixed period (e.g., every 15 minutes). Closed-loop hysteresis control of loads may result in transitions with periods changing
over time with environmental conditions. Transitions that occur without a known schedule can be modeled as stochastic arrival processes.
Schedules may change depending on the operating conditions and overall status of a microgrid.

The final layer of abstraction is *condition*. As loads degrade or fail, their behavior changes.
This can be due to a change in any one of the previous abstractions.
Some examples for each layer of abstraction are:
    - A sudden fault to ground changing the *state* of a load, adding zero-sequence current.
    - An existing fault to ground changing the ``OFF->ON`` *transient* of a load.
    - A sudden failure on one phase of a three-phse load creating a new state in its *finite state machine*.
    - A feedback sensor failure causing a load's *schedule* to alter as it struggles to meet an impossible setpoint.