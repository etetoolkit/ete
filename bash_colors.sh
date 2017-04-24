#!/bin/bash
#
# Constants and functions for terminal colors.
# Author: Max Tsepkov <max@yogi.pw>

CLR_ESC="\033["

# All these variables has a function with the same name, but in lower case.
#
CLR_RESET=0             # reset all attributes to their defaults
CLR_RESET_UNDERLINE=24  # underline off
CLR_RESET_REVERSE=27    # reverse off
CLR_DEFAULT=39          # set underscore off, set default foreground color
CLR_DEFAULTB=49         # set default background color

CLR_BOLD=1              # set bold
CLR_BRIGHT=2            # set half-bright (simulated with color on a color display)
CLR_UNDERSCORE=4        # set underscore (simulated with color on a color display)
CLR_REVERSE=7           # set reverse video

CLR_BLACK=30            # set black foreground
CLR_RED=31              # set red foreground
CLR_GREEN=32            # set green foreground
CLR_BROWN=33            # set brown foreground
CLR_BLUE=34             # set blue foreground
CLR_MAGENTA=35          # set magenta foreground
CLR_CYAN=36             # set cyan foreground
CLR_WHITE=37            # set white foreground

CLR_BLACKB=40           # set black background
CLR_REDB=41             # set red background
CLR_GREENB=42           # set green background
CLR_BROWNB=43           # set brown background
CLR_BLUEB=44            # set blue background
CLR_MAGENTAB=45         # set magenta background
CLR_CYANB=46            # set cyan background
CLR_WHITEB=47           # set white background


# check if string exists as function
# usage: if fn_exists "sometext"; then ... fi
function fn_exists
{
    type -t "$1" | grep -q 'function'
}

# iterate through command arguments, o allow for iterative color application
function clr_layer
{
    # default echo setting
    CLR_ECHOSWITCHES="-e"
    CLR_STACK=""
    CLR_SWITCHES=""
    ARGS=("$@")

    # iterate over arguments in reverse
    for ((i=$#; i>=0; i--)); do
        ARG=${ARGS[$i]}
        # echo $ARG
        # set CLR_VAR as last argtype
        firstletter=${ARG:0:1}

        # check if argument is a switch
        if [ "$firstletter" = "-" ] ; then
            # if -n is passed, set switch for echo in clr_escape
            if [[ $ARG == *"n"* ]]; then
                CLR_ECHOSWITCHES="-en"
                CLR_SWITCHES=$ARG
            fi
        else
            # last arg is the incoming string
            if [ -z "$CLR_STACK" ]; then
                CLR_STACK=$ARG
            else
                # if the argument is function, apply it
                if [ -n "$ARG" ] && fn_exists $ARG; then
                    #continue to pass switches through recursion
                    CLR_STACK=$($ARG "$CLR_STACK" $CLR_SWITCHES)
                fi
            fi
        fi
    done

    # pass stack and color var to escape function
    clr_escape "$CLR_STACK" $1;
}

# General function to wrap string with escape sequence(s).
# Ex: clr_escape foobar $CLR_RED $CLR_BOLD
function clr_escape
{
    local result="$1"
    until [ -z "${2:-}" ]; do
	if ! [ $2 -ge 0 -a $2 -le 47 ] 2>/dev/null; then
	    echo "clr_escape: argument \"$2\" is out of range" >&2 && return 1
	fi
        result="${CLR_ESC}${2}m${result}${CLR_ESC}${CLR_RESET}m"
	shift || break
    done

    echo "$CLR_ECHOSWITCHES" "$result"
}

function clr_reset           { clr_layer $CLR_RESET "$@";           }
function clr_reset_underline { clr_layer $CLR_RESET_UNDERLINE "$@"; }
function clr_reset_reverse   { clr_layer $CLR_RESET_REVERSE "$@";   }
function clr_default         { clr_layer $CLR_DEFAULT "$@";         }
function clr_defaultb        { clr_layer $CLR_DEFAULTB "$@";        }
function clr_bold            { clr_layer $CLR_BOLD "$@";            }
function clr_bright          { clr_layer $CLR_BRIGHT "$@";          }
function clr_underscore      { clr_layer $CLR_UNDERSCORE "$@";      }
function clr_reverse         { clr_layer $CLR_REVERSE "$@";         }
function clr_black           { clr_layer $CLR_BLACK "$@";           }
function clr_red             { clr_layer $CLR_RED "$@";             }
function clr_green           { clr_layer $CLR_GREEN "$@";           }
function clr_brown           { clr_layer $CLR_BROWN "$@";           }
function clr_blue            { clr_layer $CLR_BLUE "$@";            }
function clr_magenta         { clr_layer $CLR_MAGENTA "$@";         }
function clr_cyan            { clr_layer $CLR_CYAN "$@";            }
function clr_white           { clr_layer $CLR_WHITE "$@";           }
function clr_blackb          { clr_layer $CLR_BLACKB "$@";          }
function clr_redb            { clr_layer $CLR_REDB "$@";            }
function clr_greenb          { clr_layer $CLR_GREENB "$@";          }
function clr_brownb          { clr_layer $CLR_BROWNB "$@";          }
function clr_blueb           { clr_layer $CLR_BLUEB "$@";           }
function clr_magentab        { clr_layer $CLR_MAGENTAB "$@";        }
function clr_cyanb           { clr_layer $CLR_CYANB "$@";           }
function clr_whiteb          { clr_layer $CLR_WHITEB "$@";          }

# Outputs colors table
function clr_dump
{
    local T='gYw'

    echo -e "\n                 40m     41m     42m     43m     44m     45m     46m     47m";

    for FGs in '   0m' '   1m' '  30m' '1;30m' '  31m' '1;31m' \
               '  32m' '1;32m' '  33m' '1;33m' '  34m' '1;34m' \
               '  35m' '1;35m' '  36m' '1;36m' '  37m' '1;37m';
    do
        FG=${FGs// /}
        echo -en " $FGs \033[$FG  $T  "
        for BG in 40m 41m 42m 43m 44m 45m 46m 47m; do
            echo -en " \033[$FG\033[$BG  $T  \033[0m";
        done
        echo;
    done

    echo
    clr_bold "    Code     Function           Variable"
    echo \
'    0        clr_reset          $CLR_RESET
    1        clr_bold           $CLR_BOLD
    2        clr_bright         $CLR_BRIGHT
    4        clr_underscore     $CLR_UNDERSCORE
    7        clr_reverse        $CLR_REVERSE

    30       clr_black          $CLR_BLACK
    31       clr_red            $CLR_RED
    32       clr_green          $CLR_GREEN
    33       clr_brown          $CLR_BROWN
    34       clr_blue           $CLR_BLUE
    35       clr_magenta        $CLR_MAGENTA
    36       clr_cyan           $CLR_CYAN
    37       clr_white          $CLR_WHITE

    40       clr_blackb         $CLR_BLACKB
    41       clr_redb           $CLR_REDB
    42       clr_greenb         $CLR_GREENB
    43       clr_brownb         $CLR_BROWNB
    44       clr_blueb          $CLR_BLUEB
    45       clr_magentab       $CLR_MAGENTAB
    46       clr_cyanb          $CLR_CYANB
    47       clr_whiteb         $CLR_WHITEB
'
}

