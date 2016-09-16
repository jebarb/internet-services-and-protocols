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

# define states
# 0 = beginning state, accept MAIL FROM
# 1 = accepting RCPT TO
# 2 = accepting DATA
# 3 = accepting data string or termination sequence
state = 0
start_state = 0
rcpt_state = 1
rcpt_data_state = 2
data_state = 3
invalid_state = -1

def command_check(line):
    if re.match(mail_from, line, flags=re.I):
        return start_state
    elif re.match(rcpt_to, line, flags=re.I):
        return rcpt_state
    elif re.match(data, line, flags=re.I):
        return data_state
    else:
        return invalid_state

def argument_check(line, command):
    if command == data_state:
        return True
    return re.match(path, line[line.index(':')+1:len(line)], flags=re.I)

def state_check(line):
    global state
    command = command_check(line)
    if command == data_state and state == rcpt_data_state:
        print("354 Start mail input; end with <CRLF>.<CRLF>")
        return command
    elif command == state:
        if argument_check(line, command):
            print("250 OK")
            return command + 1
        else:
            print("501 Syntax error in parameters or arguments")
            return start_state
    elif command == rcpt_state and state == rcpt_data_state:
        if argument_check(line, command):
            print("250 OK")
            return state
        else:
            print("501 Syntax error in parameters or arguments")
            return start_state
    else:
        if command == invalid_state:
            print("500 Syntax error: command unrecognized")
        elif argument_check(line, command):
            print("503 Bad sequence of commands")
        return start_state

def write_to_file(sender, recipients, email_text):
    for address in recipients:
        address = address[1:len(address)-1].strip()
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
    global state
    for line in fileinput.input():
        print(line.rstrip())
        if state == data_state:
            if re.match(end_data, line.rstrip(), flags=re.I):
                write_to_file(sender, recipients, email_text)
                state = start_state
                sender = ""
                recipients = []
                email_text = ""
            else:
                email_text += line
        else:
            state = state_check(line)
            print(state)
            if state == rcpt_state:
                sender = line[line.index(':')+1:len(line)].strip()
            elif state == rcpt_state or state == rcpt_data_state:
                recipients.append(line[line.index(':')+1:len(line)].strip())

process()
