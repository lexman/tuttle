import subprocess
import sys

version = "2.0.0"


def get_commit_id():
    try:
        log = subprocess.check_output(['git', 'show', '-q'])
        commit_id = log.split("\n")[0][7:]
        return commit_id
    except subprocess.CalledProcessError:
        return ""




def export_version(filename):
    with open(filename, 'w') as f:
        f.write("{}\n".format(version))
        f.write("{}\n".format(get_commit_id()))
        f.write("{}\n".format(sys.platform))
