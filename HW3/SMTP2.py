import fileinput
import re
import sys


class smtp:  # define regex
    path = re.compile("")
    mail_from = re.compile("^From: <[^\s<>()[\]\.,;:@\"]+"\
            "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>\n$")
    rcpt_to = re.compile("^To: <[^\s<>()[\]\.,;:@\"]+"\
            "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>\n$")
    finish = re.compile("^.\n$")


class states:      # define states
    start = 0      # initial state, accept from:
    rcpt = 1       # accept to:
    data = 2       # accept to: or data
    message = 3    # accept data


def command_check(line):  # validate command, return state that accepts it
    if smtp.mail_from.match(line):
        return states.start
    elif smtp.rcpt_to.match(line):
        return states.rcpt
    return states.data


def state_check(line, state, command):  # ensure state+input align
    if state == command == states.message:
        print(line.rstrip('\n'))
        return state
    elif state == command or (state == states.data and command == states.rcpt):
        return response_check(line, send_command(line, command, state))
    elif state == states.message and command == states.start:
        return response_check(line, send_command(line, command,\
                response_check(line, send_command(line, command, state))))
    return state


def send_command(line, command, state):  # write command to stdout
    if command == states.start and state == states.message:
        print(".")
        return state
    if command == states.start:
        print("MAIL FROM: " + line[line.index('<'):].rstrip('\n'))
    elif command == states.rcpt:
        print("RCPT TO: " + line[line.index('<'):].rstrip('\n'))
    elif command == states.data:
        print("DATA")
    return command


def response_check(line, command):
    response = raw_input()
    print >> sys.stderr, response.rstrip('\n')
    if command == states.data and response.startswith("354"):
        print(line.rstrip('\n'))
        return states.message
    elif response.startswith("250"):
        return states.start if command == states.message else command + 1
    return states.start


def process_email(): # process input and output
    state = states.start
    for line in fileinput.input():
        print >> sys.stderr, line.rstrip('\n')
        state = state_check(line, state, command_check(line))
    if state == states.message:
        print(".")


process_email()
