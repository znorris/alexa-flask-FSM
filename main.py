from flask import Flask
from flask_ask import Ask, statement, question
from machines.routine import DailyRoutineMachine


routine = DailyRoutineMachine('routine')
app = Flask(__name__)
ask = Ask(app, '/')


@ask.launch
def launched():
    return question(routine.state)


@ask.intent('GetUp')
def get_up():
    return routine.execute_transition('get_up')


@ask.intent('GoToBed')
def go_to_bed():
    return routine.execute_transition('go_to_bed')


@ask.intent('State')
def get_state():
    return statement(routine.state)


@ask.intent('AMAZON.YesIntent')
def yes_intent():
    return routine.execute_transition('yes')


@ask.intent('AMAZON.NoIntent')
def no_intent():
    return routine.execute_transition('no')


@ask.on_session_started
def new_session():
    app.logger.debug('new session started')


def close_user_session():
    app.logger.debug('user session stopped')


@ask.session_ended
def session_ended():
    close_user_session()
    return "", 200


if __name__ == '__main__':
    app.run(debug=True)
