from flask import render_template
from flask_ask import question, statement
from IPython.display import Image, display, display_png
from random import random
from transitions.extensions import GraphMachine as Machine
from transitions.core import MachineError


# Helpers
# TODO: Move these elsewhere
def render_statement(template_name_or_list, **kwargs):
    # Statements will tell Alexa we are trying to end the session.
    return statement(render_template(template_name_or_list, **kwargs))


def render_question(template_name_or_list, **kwargs):
    # Questions will tell Alexa we are not trying to end the session.
    return question(render_template(template_name_or_list, **kwargs))


class DailyRoutineMachine(object):
    states = ['awake', 'asleep', 'begging']

    def __init__(self, name):
        self.name = name
        self.begging_from = None
        self.machine = Machine(model=self, states=DailyRoutineMachine.states, initial='awake')

        # Go To Bed Trigger / Intent
        # TODO: Determine order of operations for transition as I'm using conditionals first
        # then allowing a non-conditional catch-all.
        self.machine.add_transition(trigger='go_to_bed', source='awake', dest='begging', conditions='should_beg', before='set_begging_from')
        self.machine.add_transition('go_to_bed', 'awake', 'asleep')
        # Get Up Trigger / Intent
        self.machine.add_transition('get_up', 'asleep', 'begging', conditions='should_beg', before='set_begging_from')
        self.machine.add_transition('get_up', 'asleep', 'awake')
        # Yes Trigger / Intent
        self.machine.add_transition('yes', 'begging', 'asleep', conditions='is_begging_to_stay_awake', after='reset_begging_from')
        self.machine.add_transition('yes', 'begging', 'awake', conditions='is_begging_to_stay_asleep', after='reset_begging_from')
        # No Trigger / Intent
        self.machine.add_transition('no', 'begging', 'awake', conditions='is_begging_to_stay_awake', after='reset_begging_from')
        self.machine.add_transition('no', 'begging', 'asleep', conditions='is_begging_to_stay_asleep', after='reset_begging_from')
        # TODO: Determine if there is a better way of handling "after='reset_begging_from'". Very Repetitive.

    # State Retry Replies
    def current_retry(self):
        # Returning a retry this way is convenient because
        # The retries I have do not need to pass variables
        # into the template.
        current_retry_name = self.state + '_retry'
        return render_question(current_retry_name)

    # State Replies
    def current_reply(self):
        # Handy if you need to send variables into the template.
        current_reply_name = self.state + '_reply'
        current_reply_method = getattr(self, current_reply_name)
        return current_reply_method()

    def asleep_reply(self):
        return render_question('asleep_reply', state=self.state)

    def awake_reply(self):
        return render_question('awake_reply', state=self.state)

    def begging_reply(self):
        return render_question('begging_reply', state=self.state, begging_from=self.begging_from)

    # Transition Extras
    def set_begging_from(self):
        self.begging_from = self.state

    def reset_begging_from(self):
        self.begging_from = None

    def execute_transition(self, name):
        transition = getattr(self, name)
        try:
            # If a transition has conditionals
            # but they are not met, the transition will
            # return False.
            assert True == transition()
            return self.current_reply()
        except (MachineError, AssertionError):
            # We weren't able to make the transition.
            # Send back the states retry msg.
            return self.current_retry()

    # Transition Conditions
    def is_begging_to_stay_awake(self):
        return self.begging_from == 'awake'

    def is_begging_to_stay_asleep(self):
        return self.begging_from == 'asleep'

    @staticmethod
    def should_beg(): return random() < 0.50  # 50/50 chance there is gonna be begging

    # Machine Helpers
    def show_graph(self):
        # graph object is created by the machine
        self.graph.draw('state.png', prog='dot')
        display(Image('state.png'))
        # TODO: Could be cool to have it display the graph as a card
