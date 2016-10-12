import socket
import re


conn = ""


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
    elif line.endswith("\n.\n") or smtp.end_data.match(line):
        return states.body
    return states.bad_cmd


def argument_check(line):  # validate command argument
    return smtp.path.match(line[line.index(':')+1:])


def state_check(state, command):  # ensure state+input align, send message
    if state is command is states.data:
        conn.send("354 Start mail input; end with <CRLF>.<CRLF>"
                  .encode())
        return states.body
    elif state is command or (state is states.data and command is states.rcpt):
        conn.send("250 OK".encode())
        return command + 1
    elif state is states.body:
        return states.body
    elif command in [states.bad_cmd, states.body]:
        conn.send("500 Syntax error: command unrecognized".encode())
    elif command is states.bad_arg:
        conn.send("501 Syntax error in parameters or arguments".encode())
    else:
        conn.send("503 Bad sequence of commands".encode())
    return states.start  # on error, reset to start state


def write_to_file(sender, recipients, email_text):  # write email to file
    for address in recipients:
        domain = address[address.index('@')+1:address.index('>')]
        out = open("forward/" + domain.strip(), "a+")  # remove <>
        out.write("From: " + sender + '\n')
        out.write("To: ")
        for i in range(0, len(recipients)):
            if i == len(recipients) - 1:
                out.write(recipients[i] + '\n')
            else:
                out.write(recipients[i] + ',')
        out.write(email_text)


# ADD PORT NUMBER AS COMMAND LINE ARG
def process_smtp():  # process input and output
    sender = email_text = ""
    recipients = []
    state = states.start
    hostname = socket.gethostname()
    port = 14615
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)
    global conn
    while True:
        conn, address = server_socket.accept()
        conn.send(("220 " + hostname).encode())
        response = conn.recv(1024).decode()
        print(response)
        if not response.startswith("HELO"):
            continue
        while True:
            line = conn.recv(1024).decode()
            print(repr(line))
            if state is states.start:
                sender = email_text = ""
                recipients = []
            if not line.startswith("QUIT"):
                state = state_check(state, command_check(line))
                if state is states.rcpt:
                    sender = line[line.index(':')+1:].strip()
                elif state is states.data:
                    recipients.append(line[line.index(':')+1:].strip())
                elif state is states.body:
                    email_text += line
            if state is states.finish:
                email_text = email_text[email_text.index('\n')+1:]  # rem DATA
                write_to_file(sender, recipients, email_text)
                state = states.start
            if line.startswith("QUIT"):
                break


process_smtp()
