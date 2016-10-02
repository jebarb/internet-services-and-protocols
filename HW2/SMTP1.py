import fileinput
import re


class smtp:  # define regex
    mail_from = re.compile("^MAIL( |\t)+FROM:.*$")
    rcpt_to = re.compile("^RCPT(\s|\t)+TO:.*$")
    path = re.compile("^( |\t)*<[^\s<>()[\]\.,;:@\"]+" +
                      "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>( |\t)*\n$")
    data = re.compile("^DATA( |\t)*\n$")
    end_data = re.compile("^\.\n$")


class states:      # define states
    start = 0      # initial state, accept MAIL FROM
    rcpt = 1       # accept RCPT TO
    data = 2       # accept RCPT TO or DATA
    body = 3       # accept message body or termination sequence
    finish = 4     # indicates completed SMTP request
    bad_cmd = -1   # indicates invalid command
    bad_arg = -2   # indicates invalid argument


def command_check(line):  # validate command, return state that accepts it
    if smtp.mail_from.match(line):
        return states.start if argument_check(line) else states.bad_arg
    elif smtp.rcpt_to.match(line):
        return states.rcpt if argument_check(line) else states.bad_arg
    elif smtp.data.match(line):
        return states.data
    elif smtp.end_data.match(line):
        return states.body
    return states.bad_cmd


def argument_check(line):  # validate command argument
    return smtp.path.match(line[line.index(':')+1:])


def state_check(state, command):  # ensure state+input align, print message
    if state == command == states.data:
        print("354 Start mail input; end with <CRLF>.<CRLF>")
        return states.body
    elif state == command or (state == states.data and command == states.rcpt):
        print("250 OK")
        return command + 1
    elif state == states.body:
        return states.body
    elif command in [states.bad_cmd, states.body]:
        print("500 Syntax error: command unrecognized")
    elif command == states.bad_arg:
        print("501 Syntax error in parameters or arguments")
    else:
        print("503 Bad sequence of commands")
    return states.start  # on error, reset to start state


def write_to_file(sender, recipients, email_text):  # write email to file
    for address in recipients:
        out = open("forward/" + address[1:-1].strip(), "a+")  # remove <>
        out.write("From: " + sender + '\n')
        for r in recipients:
            out.write("To: " + r + '\n')
        out.write(email_text)


def process_smtp():  # process input and output
    sender = email_text = ""
    recipients = []
    state = states.start
    for line in fileinput.input():
        print(line.rstrip('\n'))
        if state == states.start:
            sender = email_text = ""
            recipients = []
        state = state_check(state, command_check(line))
        if state == states.rcpt:
            sender = line[line.index(':')+1:].strip()
        elif state == states.data:
            recipients.append(line[line.index(':')+1:].strip())
        elif state == states.body:
            email_text += line
        elif state == states.finish:
            email_text = email_text[email_text.index('\n')+1:]  # remove DATA
            write_to_file(sender, recipients, email_text)
            state = states.start


process_smtp()
