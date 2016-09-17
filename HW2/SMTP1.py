import fileinput
import re

# define regex strings
mail_from = "^MAIL( |   )+FROM:.*$"
rcpt_to = "^RCPT( |    )+TO:.*$"
path = "^( |    )*<[^\s<>()[\]\.,;:@\"]+"\
        "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>( |    )*\n$"
data = "^DATA( |    )*\n$"
end_data = "^<CRLF>.<CRLF>$"

# define states
state_start = 0      # initial state, accept MAIL FROM
state_rcpt = 1       # accept RCPT TO
state_data = 2       # accept RCPT TO or DATA
state_body = 3       # accept message body or termination sequence
state_finish = 4     # indicates completed SMTP request
state_bad_cmd = -1   # indicates invalid command
state_bad_arg = -2   # indicates invalid argument


def command_check(line):  # validate command, return state that accepts it
    if re.match(mail_from, line):
        return state_start if argument_check(line) else state_bad_arg
    elif re.match(rcpt_to, line):
        return state_rcpt if argument_check(line) else state_bad_arg
    elif re.match(data, line):
        return state_data
    elif re.match(end_data, line.rstrip()):
        return state_body
    else:
        return state_bad_cmd


def argument_check(line):  # validate command argument
    return re.match(path, line[line.index(':')+1:])


def state_check(state, command):  # ensure state+input align, print message
    if state == command == state_data:
        print("354 Start mail input; end with <CRLF>.<CRLF>")
        return state_body
    elif state == command or state == state_data and command == state_rcpt:
        print("250 OK")
        return command + 1
    elif state == state_body:
        return state_body
    elif command == state_bad_cmd or command == state_body:
        print("500 Syntax error: command unrecognized")
    elif command == state_bad_arg: 
        print("501 Syntax error in parameters or arguments")
    else:
        print("503 Bad sequence of commands")
    return state_start  # on error, reset to start state


def write_to_file(sender, recipients, email_text):  # write email to file
    for address in recipients:
        out = open("forward/" + address[1:-1].strip(), "a+")
        out.write("From: " + sender + '\n')
        for r in recipients:
            out.write("To: " + r + '\n')
        out.write(email_text)


def process(): # process input and output
    sender = email_text = ""
    recipients = []
    state = state_start
    for line in fileinput.input():
        print(line.rstrip('\n'))
        if state == state_start:
            sender = email_text = ""
            recipients = []
        state = state_check(state, command_check(line))
        if state == state_rcpt:
            sender = line[line.index(':')+1:].strip()
        elif state == state_data:
            recipients.append(line[line.index(':')+1:].strip())
        elif state == state_body:
            email_text += line
        elif state == state_finish:
            write_to_file(sender, recipients, email_text)
            state = state_start

process()
