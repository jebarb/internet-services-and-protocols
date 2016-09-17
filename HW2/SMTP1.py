import fileinput
import re

# define regex strings
nullspace = "( |    )*"
whitespace = "( |   )+"
mail_from = "^MAIL( |   )+FROM:.*$"
rcpt_to = "^RCPT" + whitespace + "TO:.*$"
path = "^" + nullspace + "<[^\s<>()[\]\.,;:@\"]+" + \
        "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>" + nullspace + "\n$"
data = "^DATA" + nullspace + "\n$"
end_data = "^<CRLF>.<CRLF>$"

# define states
start_state = 0      # beginning state, accept MAIL FROM
rcpt_state = 1       # accept RCPT TO
rcpt_data_state = 2  # accept DATA or RCPT TO
data_state = 3       # accept data string or termination sequence
invalid_state = -1   # indicates invalid input
bad_arg_state = -2   # indicates invalid argument


def command_check(line):  # validate command, return state that accepts it
    if re.match(mail_from, line, flags=re.I):
        return start_state if argument_check(line) else bad_arg_state
    elif re.match(rcpt_to, line, flags=re.I):
        return rcpt_state if argument_check(line) else bad_arg_state
    elif re.match(data, line, flags=re.I):
        return data_state
    else:
        return invalid_state


# validate command argument
def argument_check(line):
    if re.match(path, line[line.index(':')+1:len(line)], flags=re.I):
        return True
    else:
        return False


# check incorrect state
def bad_state(command):
    if command == invalid_state:
        print("500 Syntax error: command unrecognized")
    elif command == bad_arg_state:
        print("501 Syntax error in parameters or arguments")
    else:
        print("503 Bad sequence of commands")
    return start_state


# ensure state aligns with input command
def state_check(line, state):
    command = command_check(line)
    if state == command == start_state:
        print("250 OK")
        return rcpt_state
    elif state == command == rcpt_state:
        print("250 OK")
        return rcpt_data_state
    elif state == rcpt_data_state and command == rcpt_state:
        print("250 OK")
        return rcpt_data_state
    elif state == rcpt_data_state and command == data_state:
        print("354 Start mail input; end with <CRLF>.<CRLF>")
        return data_state
    return bad_state(command)


def write_to_file(sender, recipients, email_text):
    for address in recipients:
        address = "forward/" + address[1:len(address)-1].strip()
        out = open(address, "a+")
        out.write("From: " + sender + '\n')
        for r in recipients:
            out.write("To: " + r + '\n')
        out.write(email_text)


def process():
    # store sender, recipients, email text
    sender = ""
    recipients = []
    email_text = ""
    state = start_state
    for line in fileinput.input():
        print(line.rstrip('\n'))
        if state == data_state:
            if re.match(end_data, line.rstrip(), flags=re.I):
                print("250 OK")
                write_to_file(sender, recipients, email_text)
                state = start_state
                sender = ""
                recipients = []
                email_text = ""
            else:
                email_text += line
        else:
            state = state_check(line, state)
            if state == rcpt_state:
                sender = line[line.index(':')+1:len(line)].strip()
            elif state == rcpt_data_state:
                recipients.append(line[line.index(':')+1:len(line)].strip())

process()
