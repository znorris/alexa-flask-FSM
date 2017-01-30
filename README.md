# Flask-ask with State Machine for use in Alexa Skills

After using [dgtony](https://github.com/dgtony)'s [AFG]() for scenario-based
dialogues I became more interested in using a state machine for managing
conversation state. In this example I use the python library [transitions](https://github.com/tyarkoni/transitions)
to handle all the heavy lifting.

Benefits:

1. It is much simpler to reason about the conversational flow when using
a state machine.

2. Most state machine libraries have a logging ability. This will be 
incredibly useful for keeping track of how your users interact with
your skill.

Feel free to create issues if you have questions or comments!
