import fileinput
import re

for line in fileinput.input():
    print(line.strip())
    if not re.match("^MAIL( |    )+FROM:.*$", line, flags=re.I):
        print("thing")
    elif not re.match("^( |  )*<[^\s<>()[\]\.,;:@\"]+@[a-z][a-z0-9]+(\.[a-z][a-z0-9]+)*>( |  )*\n$", line[line.index(':')+1:len(line)], flags=re.I):
        print("broke")
    else:
        print("Sender ok")
