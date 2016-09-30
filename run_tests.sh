#!/bin/bash
# run_tests.sh -- created 2016-04-28, Renato Alves

export TOP_PID=$$

# If a command in a pipe fails, the whole command fails
set -o pipefail

usage() {
    echo >&2 ""
    echo >&2 "This script runs the test suite provided with ete3."
    echo >&2 "Without any optional parameters it defaults to running the api tests"
    echo >&2 "on a Python 3.5 environment."
    echo >&2 ""
    echo >&2 "Usage:"
    echo >&2 "    $0 [option] [-v version] [testset]"
    echo >&2 ""
    echo >&2 "Optional parameters:"
    echo >&2 "       -h --help    = shows the current information"
    echo >&2 "       --setup-only = configures and updates the testing environment but skips tests"
    echo >&2 "       --test-only  = skips configuration of environment and runs tests"
    echo >&2 "       -l           = enable logging to tests.log"
    echo >&2 "       -s           = show the content of tests.log at the end of execution (implies -l)"
    echo >&2 "       -x           = install ete3 external apps in the test environment"
    echo >&2 "       -v           = python version to use for running tests. (default: 3.5)"
    echo >&2 "       testset      = set of tests to run. (default: api) (for full testsuite use all)"
    echo >&2 ""
}

valid_version() {
    if [ -z "$1" ]; then
        echo "$2"  # No version was specified

    else
        if ! [[ $1 =~ ^[2-3](\.[0-9]|\.[1-9][0-9]){0,2}$ ]]; then
            echo >&2 -e "\nERROR: Python version should be in one of the following formats: 3, 3.5, 3.5.12 not $1"
            usage
            kill -s TERM $TOP_PID
        else
            echo "$1"
        fi
    fi
}

handle_error() {
    if [ "$1" != "0" ]; then
        echo >&2 -e "\n$2"
        echo >&2 "$3"
        kill -s TERM $TOP_PID
    fi
}

optional() {
    if [ "x$1" == "x" ]; then
        echo "$2"
    else
        echo "$1"
    fi
}

setup_miniconda() {
    if ! [ -f "${CONDA}/bin/conda" ]; then
        echo -n ">>> Downloading miniconda... "
        wget_output=$(wget -nv https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh 2>&1 | tee -a ${LOG})
        handle_error "$?" "ERROR: Failed to download miniconda installation script" "$wget_output"
        echo "DONE"

        echo -n ">>> Installing miniconda... "
        install_output=$(bash miniconda.sh -b -p ${CONDA} 2>&1 | tee -a ${LOG})
        handle_error "$?" "ERROR: Failed to install miniconda" "$install_output"
        echo "DONE"

        echo -n ">>> Updating miniconda packages and package information... "
        conda_update_output=$(${CONDA}/bin/conda update -q -y conda 2>&1 | tee -a ${LOG})
        handle_error "$?" "ERROR: Failed to update conda packages" "$conda_update_output"
        echo "DONE"

        echo -n ">>> Cleaning up miniconda installation files... "
        clean_output=$(rm -f miniconda.sh 2>&1 | tee -a ${LOG})
        handle_error "$?" "ERROR: Failed to remove miniconda.sh" "$clean_output"
        echo "DONE"

    fi

    echo -n ">>> Collecting information about conda... "
    info_output=$(${CONDA}/bin/conda info -a 2>&1 | tee -a ${LOG})
    handle_error "$?" "ERROR: Failed to collect information about conda" "$info_output"
    echo "DONE"
}

create_env() {
    env_output=$(${CONDA}/bin/conda env list | grep test_${VERSION})
    if [ $? == 0 ]; then
        # Env already created. Nothing to do
        echo >&2 "### Using existing conda environment test_${VERSION}."
        return 0
    fi

    echo -n ">>> Creating test environment for version ${VERSION}... "
    create_output=$(${CONDA}/bin/conda create -q -y -n test_${VERSION} python=${VERSION} pip pyqt=4 numpy six lxml coverage scikit-bio biopython scipy 2>&1 | tee -a ${LOG})
    handle_error "$?" "ERROR: Failed to create a new conda environment for python ${VERSION}" "$create_output"
    echo "DONE"
}

install_external_apps() {
    if [ "$EXTERNAL_APPS" == "1" ]; then
        echo -n ">>> Installing external packages in environment test_${VERSION}... "
        external_apps_output=$(source ${CONDA}/bin/activate test_${VERSION} 2>&1 && ${CONDA}/bin/conda install -c etetoolkit ete3_external_apps -y 2>&1 | tee -a ${LOG})
        handle_error "$?" "ERROR: Failed to install ete3 external apps in the conda environment" "$external_apps_output"
        echo "DONE"
    fi
}

update_env() {
    echo -n ">>> Updating conda packages in environment test_${VERSION}... "
    update_conda_output=$(source ${CONDA}/bin/activate test_${VERSION} 2>&1 && ${CONDA}/bin/conda update -y --all 2>&1 | tee -a ${LOG})
    handle_error "$?" "ERROR: Failed to update packages in the conda environment" "$update_conda_output"
    echo "DONE"

    echo -n ">>> Installing latest ete in test environment... "
    update_output=$(source ${CONDA}/bin/activate test_${VERSION} 2>&1 && python setup.py install --donottrackinstall 2>&1 | tee -a ${LOG})
    handle_error "$?" "ERROR: Failed to install/update ete to the latest commit on test_${VERSION}" "$update_output"
    echo "DONE"
}

# Find a free X server number by looking at .X*-lock files in /tmp.
find_free_servernum() {
    # Start on display 99
    i=99
    while [ -f /tmp/.X$i-lock ]; do
        i=$(($i + 1))
    done
    echo $i
}

start_xvfb() {
    echo -n ">>> Starting Xvfb on display ${DISPLAY}... "
    # NOTE -noreset is needed in some versions of Xvfb.
    # The default is -reset but this causes the server to crash when the last client disconnects
    Xvfb ${DISPLAY} -noreset -screen 0 1280x800x16 &>> ${LOG} &
    # Giving xvfb some time to start
    sleep $SLEEP

    # Checking if Xvfb is still running
    kill -0 $!
    handle_error "$?" "ERROR: Xvfb didn't start properly" "Please re-run the test script with option -l and check the log file"
    echo "DONE"
}

shutdown_xvfb() {
    # Don't trap exit codes any longer
    trap - EXIT HUP INT QUIT TERM KILL

    if [ "$!" != "0" ] && [ "x$!" != "x" ]; then
        echo -n ">>> Stopping Xvfb... "

        xvfb_stop_output=$(kill $! 2>&1 | tee -a ${LOG})
        handle_error "$?" "ERROR: Failed to stop Xvfb" "$xvfb_stop_output"
        echo "DONE"
    fi
}

showlog() {
    if [ "$SHOWLOG" == "1" ]; then
        echo -e ">>> Showing contents of test log:\n"
        [ -f "${LOG}" ] && cat ${LOG}
    fi
}

run_tests() {
    echo -n ">>> Obtaining deployed python version... "
    py_version_output=$(source ${CONDA}/bin/activate test_${VERSION} &>/dev/null && python --version 2>&1 | tee -a ${LOG})
    handle_error "$?" "ERROR: couldn't obtain python version" "$py_version_output"
    echo "DONE"

    echo -n ">>> Obtaining ete3 version... "
    ete_version_output=$(source ${CONDA}/bin/activate test_${VERSION} &>/dev/null && ete3 version 2>&1 | tee -a ${LOG})
    handle_error "$?" "ERROR: couldn't obtain ete3 version" "$ete_version_output"
    echo "DONE"

    echo -n ">>> Running tests on ete ${ete_version_output} using ${py_version_output}... "
    tests_output=$(source ${CONDA}/bin/activate test_${VERSION} 2>&1 && coverage run -m ete3.test.test_${TESTSET} 2>&1 | tee -a ${LOG})
    handle_error "$?" "ERROR: One or more tests failed on test_${VERSION}" "$tests_output"
    echo "DONE"

    echo "### All tests passed successfully"
}

# Location of current script
FILEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONDA="${FILEDIR}/test_tmp/miniconda"
EXTERNAL_APPS=0
SETUP=1
TEST=1

# Logfile
NULL_LOG="/dev/null"
LOG="${NULL_LOG}"
DEFAULT_LOG="${FILEDIR}/tests.log"
SHOWLOG=0

# Parse args using getopt (instead of getopts) to allow arguments before options
ARGS="$(getopt -o v:lshx -l help,test-only,setup-only -n "$0" -- "$@" 2>/dev/null)"
if [ "$?" != "0" ]; then
    usage
    handle_error "1" "ERROR: Check the arguments passed. At least one was not valid."
fi

# reorganize arguments as returned by getopt
eval set -- "$ARGS"

while true; do
    case "$1" in
        # Shift before to throw away option
        # Shift after if option has a required positional argument
        -l)
            shift
            LOG="${DEFAULT_LOG}"
            ;;
        -s)
            shift
            SHOWLOG=1
            LOG="${DEFAULT_LOG}"
            ;;
        -v)
            shift
            # Validate provided python version to use for tests
            VERSION="$1"
            shift
            ;;
        -x)
            shift
            EXTERNAL_APPS=1
            ;;
        --setup-only)
            shift
            TEST=0
            ;;
        --test-only)
            shift
            SETUP=0
            ;;
        -h|--help)
            usage
            exit
            ;;
        --)
            shift
            break
            ;;
    esac
done

VERSION="$(valid_version ${VERSION} 3.5)"
TESTSET="$(optional $1 api)"
export DISPLAY=":$(find_free_servernum)"
SLEEP=2  # Time to wait for xvfb to start and be functional

[ ! -f "ete3/test/test_${TESTSET}.py" ] && usage && handle_error "1" "ERROR: Invalid testset selected ${TESTSET}"

if [ "${LOG}" == "${NULL_LOG}" ]; then
    echo "### Running ${TESTSET} tests with Python ${VERSION}"
else
    echo "### Running ${TESTSET} tests with Python ${VERSION} and logging to ${LOG}"
fi

# Empty logfile
echo -n > ${LOG}

# At any of these signals shutdown xvfb first and conditionally show the
# contents of the logfile
trap 'exitcode=$? ; shutdown_xvfb ; showlog ; exit $exitcode' EXIT HUP INT QUIT TERM KILL

if [ "${SETUP}" == "1" ]; then
    setup_miniconda
    create_env
    install_external_apps
    update_env
fi
if [ "${TEST}" == "1" ]; then
    start_xvfb
    run_tests
    shutdown_xvfb
fi
showlog

# vi: 
