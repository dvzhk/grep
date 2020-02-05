
import argparse
import sys
import re
from collections import deque

def pattern_prepare(params):
    """Preparing pattern for using in RE"""
    modified_pattern = (params.pattern.replace("?", ".")).replace("*", ".*")
    flags = 0
    if params.invert:
        modified_pattern = "^((?!" + modified_pattern + ").)*$"
    if params.ignore_case:
        flags = re.I
    return re.compile(modified_pattern, flags)


def line_number_addition(line, params, line_number, result=0):
    """"Adding line number to string? using special separator, if -n in params, otherwise return input"""
    if params.line_number:
        if result:
            separation_symbol = ":"
        else:
            separation_symbol = "-"
        return str(line_number) + separation_symbol + line
    return line


def context_definition(params):
    """Context variables definition and combining"""
    context_after = 0
    context_before = deque([],maxlen=0)

    if params.context:
        context_before = deque([], maxlen=params.context)
        context_after = params.context

    if params.before_context:
        context_before = deque([], maxlen=params.before_context)

    if params.after_context:
        context_after = params.after_context

    return context_before, context_after

def context_output(context):
    """"Line-by-line context output"""
    for line in context:
        output(line)


def output(line):
    print(line)


def grep(lines, params):

    pattern = pattern_prepare(params)
    counted_lines = 0
    line_number = 0
    after_context_active = 0
    context_before, context_after = context_definition(params)

    for line in lines:
        line = line.rstrip()
        line_number += 1

        if pattern.search(line):
            # Code running if line match pattern
            if params.count:
                counted_lines += 1

            elif params.after_context or params.before_context or params.context:
                context_output(context_before) # output context_before if present
                context_before.clear()

                after_context_active = context_after # amount of lines to output in context_after

                output(line_number_addition(line, params, line_number, 1))
            else:
                #Output line if not context ol line count specified
                output(line_number_addition(line, params, line_number,1))
        else:
            if params.before_context or params.context:
                if not after_context_active:
                    context_before.append(line_number_addition(line, params, line_number))

            if params.after_context or params.context:
                if after_context_active:
                    output(line_number_addition(line, params, line_number))
                    after_context_active -= 1

    if params.count:
        output(str(counted_lines))


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
