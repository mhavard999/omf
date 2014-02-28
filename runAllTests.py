#TODO: walk the /omf/ directory, run _tests() in all modules.

import os, sys, subprocess

# Probably will eventually remove some of these,
# especially calibration
IGNORE_DIRS = [
    "calibration",
    "data",
    ".git",
    "static",
    "templates",
    "tests",
    "uploads",
    "venv",
    "scratch"
    ]

# Useful for debugging this script (runAllTests.py) specifically.
# milToGridlab.py, for example, usually does not fail, but running its tests
# takes a long time.
IGNORE_FILES = [
    #"milToGridlab.py", 
    # runAllTests.py will try to run itself in an infinite loop
    # because the file contains the string "def _tests():"
    "runAllTests.py",
]

def runAllTests(startingdir):
    os.chdir(startingdir)
    nextdirs = []
    the_errors = 0
    misfires = {}
    for item in os.listdir("."):
        if item not in IGNORE_FILES and item.endswith(".py") and "def _tests():" in open(item).read():
            p = subprocess.Popen(["python", item], stderr=subprocess.PIPE)
            p.wait()
            if p.returncode:
                the_errors += 1
                misfires[os.path.join(os.getcwd(), item)] = p.stderr.read()
        elif os.path.isdir(item) and item not in IGNORE_DIRS:
            nextdirs.append(os.path.join(os.getcwd(), item))
    for d in nextdirs:
        e, m = runAllTests(d)
        the_errors += e
        misfires.update(m)
    return the_errors, misfires

if __name__ == "__main__":
    os.chdir(sys.argv[1] if len(sys.argv) > 1 else ".") # You can just run tests in a specific dir if you want
    i, mis = runAllTests(os.getcwd())
    print "\n\n+------------------------+"
    print "\n\nTEST RESULTS"
    print "\n\n+------------------------+"
    print i, "tests failed:\n\n"
    for fname, err in mis.items():
        print fname
        print err, "\n\n"