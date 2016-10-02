import fileinput
import re
import sys


class smtp:  # define regex
    path = re.compile("")
    mail_from = re.compile("^From: <[^\s<>()[\]\.,;:@\"]+" +
                           "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>\n$")
    rcpt_to = re.compile("^To: <[^\s<>()[\]\.,;:@\"]+" +
                         "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>\n$")
    finish = re.compile("^.\n$")


class states:      # define states
    start = 0      # initial state, accept from:
    rcpt = 1       # accept to:
    data = 2       # accept to: or data
    message = 3    # accept data
    error = -1     # error state


def command_check(line):  # validate command, return state that accepts it
    if smtp.mail_from.match(line):
        return states.start
    elif smtp.rcpt_to.match(line):
        return states.rcpt
    return states.data


def state_check(line, command, state):  # ensure state sligns with command
    if state == states.message and command == states.data:
        print(line.rstrip('\n'))
        return state
    else:
        return response_check(line, send_command(line, command, state))


def send_command(line, command, state):  # write command to stdout
    if state == states.message:
        if command == states.start:
            print(".")
        return state
    elif command == states.start:
        print("MAIL FROM: " + line[line.index('<'):].rstrip('\n'))
    elif command == states.rcpt:
        print("RCPT TO: " + line[line.index('<'):].rstrip('\n'))
    elif command == states.data:
        print("DATA")
    return command


def response_check(line, command):
    response = raw_input()
    print >> sys.stderr, response
    if command == states.data:
        if response.startswith("354"):
            print(line.rstrip('\n'))
            return states.message
        else:
            return states.error
    elif response.startswith("250"):
        return states.start if command == states.message else command + 1
    return states.error


def process_email():  # process input and output
    state = states.start
    line = ""
    for line in fileinput.input():
        state = state_check(line, command_check(line), state)
        if state == states.start:
            state = state_check(line, command_check(line), state)
        if state == states.error:
            break
    if state == states.message:
        response_check(line, send_command(line, states.start, state))
    print("QUIT")


process_email()
