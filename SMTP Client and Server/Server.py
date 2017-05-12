import socket
import re
import sys


conn = socket.socket.type  # initialize global variable for socket


class smtp:  # define regex
    mail_from = re.compile("^MAIL( |\t)+FROM:.*$")
    rcpt_to = re.compile("^RCPT(\s|\t)+TO:.*$")
    path = re.compile("^( |\t)*<[^\s<>()[\]\.,;:@\"]+" +
                      "@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>( |\t)*\n$")
    data = re.compile("^DATA( |\t)*\n$")
    end_data = re.compile("^\.\n$")
    domain = re.compile("^[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*$")


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
        print("500 Syntax error: command unrecognized")
    elif command is states.bad_arg:
        conn.send("501 Syntax error in parameters or arguments".encode())
        print("501 Syntax error in parameters or arguments")
    else:
        conn.send("503 Bad sequence of commands".encode())
        print("503 Bad sequence of commands")
    return states.bad_cmd


def write_to_file(recipients, email_text):  # write email to file
    domains = []
    for address in recipients:
        domains.append(address[address.index('@')+1:address.index('>')])
    domains = list(set(domains))  # remove duplicates
    for domain in domains:
        out = open("forward/" + domain.strip(), "a+")
        out.write(email_text)


def process_smtp():  # process input and output
    # Validate command line args
    # argv[1] is port
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        print("TCP port absent or invalid")
        return
    if int(sys.argv[1]) < 0 or int(sys.argv[1]) > 65536:
        print("TCP port out of range")
        return
    port = int(sys.argv[1])
    email_text = ""
    recipients = []
    state = states.start
    hostname = socket.gethostname()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)
    global conn
    # always accept connections
    while True:
        conn, address = server_socket.accept()
        conn.send(("220 " + hostname).encode())
        line = conn.recv(4096).decode()
        if line.startswith("HELO"):
            line = line.split(' ')
            if len(line) < 2:
                conn.send(("250 Hello, pleased to meet you").encode())
            else:
                conn.send(("250 Hello " + line[1] + ", pleased to meet you")
                          .encode())
        else:
            continue
        # Process SMTP
        while True:
            line = conn.recv(4096).decode()
            if state is states.start:
                email_text = ""
                recipients = []
            if state is states.body or not line.startswith("QUIT"):
                state = state_check(state, command_check(line))
                if state is states.data:
                    recipients.append(line[line.index(':')+1:].strip())
                if state is states.body or state is states.finish:
                    email_text += line
            if state is states.bad_cmd:  # close on error
                conn.close()
                break
            if state is states.finish:  # write email to file
                email_text = email_text.lstrip()[5:]  # rem DATA
                if email_text.endswith("\n.\n"):
                    email_text = email_text[:-2]  # rem '.\n'
                write_to_file(recipients, email_text)
                state = states.start
            if line.startswith("QUIT"):  # close on complete
                conn.close()
                break


process_smtp()
