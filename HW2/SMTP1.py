import fileinput
import re

# define regex strings
nullspace = "( |    )*"
whitespace = "( |   )+"
crlf = '\n'
mail_from = "^MAIL" + whitespace + "FROM:.*$"
rcpt_to = "^RCPT" + whitespace + "TO:.*$"
path = "^" + nullspace + "<[^\s<>()[\]\.,;:@\"]+" + "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>" + nullspace + crlf + "$"
data = "^DATA" + nullspace + crlf + "$"
end_data = "^<CRLF>.<CRLF>$"

def states(state):
# define states
# 0 = beginning state, accept MAIL FROM
# 1 = accepting RCPT TO
# 2 = accepting DATA
# 3 = accepting data string or termination sequence
    if state is "start_state":
        return 0
    elif state is "rcpt_state":
        return 1
    elif state is "rcpt_data_state":
        return 2
    elif state is "data_state":
        return 3
    elif state is "invalid_state":
        return -1

def command_check(line):
    if re.match(mail_from, line, flags=re.I):
        return states("start_state")
    elif re.match(rcpt_to, line, flags=re.I):
        return states("rcpt_state")
    elif re.match(data, line, flags=re.I):
        return states("data_state")
    else:
        return states("invalid_state")

def argument_check(line, command):
    if command == states("data_state"):
        return True
    return re.match(path, line[line.index(':')+1:len(line)], flags=re.I)

def state_check(state, line):
    command = command_check(line)
    if command == states("data_state") and state == states("rcpt_data_state"):
        print("354 Start mail input; end with <CRLF>.<CRLF>")
        return command
    elif command == state:
        if argument_check(line, command):
            print("250 OK")
            return command + 1
        else:
            print("501 Syntax error in parameters or arguments")
            return states("start_state")
    elif command == states("rcpt_state") and state == states("rcpt_data_state"):
        if argument_check(line, command):
            print("250 OK")
            return state
        else:
            print("501 Syntax error in parameters or arguments")
            return states("start_state")
    else:
        if command == states("invalid_state"):
            print("500 Syntax error: command unrecognized")
        elif argument_check(line, command):
            print("503 Bad sequence of commands")
        return states("start_state")

def write_to_file(sender, recipients, emails):
    return null

def main():
    # store sender, recipients, email text
    sender = ""
    recipients = []
    email_text = ""
    state = 0
    for line in fileinput.input():
        print(line.rstrip())
        if state == states("data_state"):
            if re.match(end_data, line.rstrip(), flags=re.I):
                state = states("start_state")
                sender = ""
                recipients = []
                email_text = ""
            else:
                email_text += line
        else:
            state = state_check(state, line)

main()
