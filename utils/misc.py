
from subprocess import Popen, PIPE, STDOUT

def get_ip_netcard(netcard='lo'):
    command = "ip addr show " + netcard + " | grep 'inet ' | sed 's/^[ \t]*//g' | awk -F'[/ ]' '{print $2}'"
    child = Popen(command, shell=True, close_fds=True, bufsize=-1, stdout=PIPE, stderr=STDOUT)
    output = child.stdout.read().decode().strip()
    return output
