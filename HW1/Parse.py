import fileinput
import re

for line in fileinput.input():
    print(line.rstrip('\n'))
    if not re.match("^MAIL.*$", line, flags=re.I):
        print("ERROR -- MAIL")
    elif not re.match("^( |\t).*$", line[4:], flags=re.I):
        print("ERROR -- whitespace")
    elif not re.match("^FROM:.*$", line[4:].strip(), flags=re.I):
        print("ERROR -- FROM:")
    elif not re.match("^<.*>$", line[line.index(':')+1:].strip(), flags=re.I):
        print("ERROR -- reverse-path")
    elif not re.match("^\S+@\S+$", line[line.index('<')+1:line.index('>')], flags=re.I):
        print("ERROR -- mailbox")
    elif not re.match("^[^\s<>()[\]\.,;:@\"]+$", line[line.index('<')+1:line.index('@')], flags=re.I):
        print("ERROR -- local-part")
    elif not re.match("^[a-z][a-z0-9]+(\.[a-z][a-z0-9]*)*$", line[line.index('@')+1:line.index('>')], flags=re.I):
        print("ERROR -- domain")
    elif not re.match("\n", line[-1], flags=re.I):
        print("ERROR -- CRLF")
    else:
        print("Sender ok")
