#!/bin/bash
# run_tests.sh -- created 2016-04-28, Renato Alves
source bash_colors.sh
export TOP_PID=$$

# If a command in a pipe fails, the whole command fails
set -o pipefail

REAL=true

function run {
    clr_bold " $@"
    if [ $REAL == true ]; then
        eval $@ || (clr_red "ERRORS FOUND!" && exit 1)
    fi
    }

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
        # NOTE Not sure why this isn't working anymore.
        # It should send a non-zero exit code but it always reports 0
        # which is super bad because it silences errors in the testsuite
        #kill -s TERM $TOP_PID
        # We workaround using exit and the exitcode seen by handle_error
        exit "$1"
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
        clr_green ">>> Downloading miniconda... "
        run "wget -nv https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh 2>&1 | tee -a ${LOG}"
        handle_error "$?" "ERROR: Failed to download miniconda installation script" "$wget_output"
        clr_green "DONE"

        clr_green ">>> Installing miniconda... "
        run "bash miniconda.sh -b -p "${CONDA}" 2>&1 | tee -a ${LOG}"
        handle_error "$?" "ERROR: Failed to install miniconda" "$install_output"
        clr_green "DONE"

        clr_green ">>> Updating miniconda packages and package information... "
        run "${CONDA}/bin/conda update -q -y conda 2>&1 | tee -a ${LOG}"
        handle_error "$?" "ERROR: Failed to update conda packages" "$conda_update_output"
        clr_green "DONE"

        clr_green ">>> Cleaning up miniconda installation files... "
        run "rm -f miniconda.sh 2>&1 | tee -a ${LOG}"
        handle_error "$?" "ERROR: Failed to remove miniconda.sh" "$clean_output"
        clr_green "DONE"

    fi

    clr_green ">>> Collecting information about conda... "
    run "${CONDA}/bin/conda info -a 2>&1 | tee -a ${LOG}"
    handle_error "$?" "ERROR: Failed to collect information about conda" "$info_output"
    clr_green "DONE"
}

create_env() {
    env_output=$("${CONDA}/bin/conda" env list | grep "test_${VERSION}")
    if [ $? == 0 ]; then
        # Env already created. Nothing to do
        echo >&2 "### Using existing conda environment test_${VERSION}."
        return 0
    fi
    
    clr_green ">>> Creating test environment for version ${VERSION}... "
    run "${CONDA}/bin/conda create -q -y -n test_${VERSION} python=${VERSION} pip pyqt=4 setuptools numpy six lxml coverage scikit-bio biopython scipy 2>&1 | tee -a ${LOG}"
    handle_error "$?" "ERROR: Failed to create a new conda environment for python ${VERSION}" "$create_output"
    clr_green "DONE"
}

install_external_apps() {
    if [ "$EXTERNAL_APPS" == "1" ]; then
        clear_green ">>> Installing external packages in environment test_${VERSION}... "
        run "${CONDA}/bin/activate test_${VERSION} 2>&1 && ${CONDA}/bin/conda install -c etetoolkit ete3_external_apps -y 2>&1 | tee -a ${LOG}"
        handle_error "$?" "ERROR: Failed to install ete3 external apps in the conda environment" "$external_apps_output"
        clear_green "DONE"
    fi
}

update_env() {
    ## conda update installs latest version of qt5, so tests are not passing
 
    #clr_green ">>> Updating conda packages in environment test_${VERSION}... "
    #run "source ${CONDA}/bin/activate test_${VERSION} 2>&1 && ${CONDA}/bin/conda update -y --all 2>&1 | tee -a ${LOG}"
    #handle_error "$?" "ERROR: Failed to update packages in the conda environment" "$update_conda_output"
    #clr_green "DONE"

    clr_green ">>> Installing latest ete in test environment... "
    run "source ${CONDA}/bin/activate test_${VERSION} 2>&1 && python setup.py install --donottrackinstall 2>&1 | tee -a ${LOG}"
    handle_error "$?" "ERROR: Failed to install/update ete to the latest commit on test_${VERSION}" "$update_output"
    clr_green "DONE"
}


showlog() {
    if [ "$SHOWLOG" == "1" ]; then
        echo -e ">>> Showing contents of test log:\n"
        [ -f "${LOG}" ] && cat "${LOG}"
    fi
}

run_tests() {
    #clr_green ">>> Obtaining deployed python version... "
    #run "${CONDA}/bin/activate test_${VERSION} &>/dev/null && python --version 2>&1"
    #handle_error "$?" "ERROR: couldn't obtain python version" "$py_version_output"
    #echo "DONE"

    clr_green ">>> Obtaining ete3 version... "
    run "source ${CONDA}/bin/activate test_${VERSION} &>/dev/null && ete3 version 2>&1"
    handle_error "$?" "ERROR: couldn't obtain ete3 version" "$ete_version_output"
    echo "DONE"

    clr_green ">>> Running tests on ete ${ete_version_output} using ${py_version_output}... "
    run "source ${CONDA}/bin/activate test_${VERSION} 2>&1 && coverage run -m ete3.test.test_${TESTSET}"
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

VERSION="$(valid_version "${VERSION}" 3.5)"
TESTSET="$(optional "$1" api)"
DISPLAY=":$(find_free_servernum)"
export DISPLAY
SLEEP=2  # Time to wait for xvfb to start and be functional

[ ! -f "ete3/test/test_${TESTSET}.py" ] && usage && handle_error "1" "ERROR: Invalid testset selected ${TESTSET}"

if [ "${LOG}" == "${NULL_LOG}" ]; then
    echo "### Running ${TESTSET} tests with Python ${VERSION}"
else
    echo "### Running ${TESTSET} tests with Python ${VERSION} and logging to ${LOG}"
fi

# Empty logfile
echo -n > "${LOG}"

# At any of these signals conditionally show the contents of the logfile
trap 'exitcode=$? ; showlog ; exit $exitcode' EXIT HUP INT QUIT TERM

if [ "${SETUP}" == "1" ]; then
    setup_miniconda
    create_env
    install_external_apps
    update_env
fi
if [ "${TEST}" == "1" ]; then
    run_tests
fi
showlog


