import argparse
import pytest
import sys
from dataclasses import dataclass, field
from typing import Optional
from z3 import *


@dataclass
class Command:
    i: Optional[int] = field(default=None)
    fp: Optional[float] = field(default=None)
    bool1: Optional[bool] = field(default=False)
    bool2: Optional[bool] = field(default=False)
    more: Optional[list] = field(default=None)


def check_constraints(comm: Command) -> bool:
    return comm.i > 10 and comm.fp < comm.i and (comm.bool1 ^ comm.bool2)


def check_constraints_z3(comm: Command):
    s = Solver()

    # types
    i = Int("i")
    fp = Real("fp")
    bool1 = Bool("bool1")
    bool2 = Bool("bool2")

    # constraints
    s.add(i > 10)
    s.add(fp < i)
    s.add(bool1 ^ bool2)

    # actual values passed in
    s.add(i == comm.i)
    s.add(fp == comm.fp)
    s.add(bool1 == comm.bool1)
    s.add(bool2 == comm.bool2)

    return s.check() == sat


def verify():
    parser = argparse.ArgumentParser(description="Sample program")

    subparsers = parser.add_subparsers(dest="command")

    # Subcommand for integer argument
    parser_integer = subparsers.add_parser("integer", help="Set an integer value")
    parser_integer.add_argument("value", type=int, help="The integer value")

    # Subcommand for boolean argument 1
    parser_bool1 = subparsers.add_parser("bool1", help="Set boolean 1 to True")
    parser_bool1.add_argument(
        "--no-bool1", action="store_true", help="Set boolean 1 to False"
    )

    # Subcommand for boolean argument 2
    parser_bool2 = subparsers.add_parser("bool2", help="Set boolean 2 to True")
    parser_bool2.add_argument(
        "--no-bool2", action="store_true", help="Set boolean 2 to False"
    )

    # Subcommand for float argument
    parser_float = subparsers.add_parser("float", help="Set a float value")
    parser_float.add_argument("value", type=float, help="The float value")

    # Subcommand for list argument
    parser_list = subparsers.add_parser("list", help="Set a list of values")
    parser_list.add_argument("values", nargs="+", type=str, help="The list of values")

    args, unknown = parser.parse_known_args()
    commands = Command()

    while args.command:
        c = args.command
        if c == "integer":
            print(f"Integer: {args.value}")
            commands.i = args.value
        elif c == "bool1":
            print(f"Boolean 1: {not args.no_bool1}")
            commands.bool1 = True
        elif c == "bool2":
            print(f"Boolean 2: {not args.no_bool2}")
            commands.bool2 = True
        elif c == "float":
            print(f"Float: {args.value}")
            commands.fp = args.value
        elif c == "list":
            commands.more = args.values
            print(f"List: {args.values}")

        # Parse the remaining arguments
        args, unknown = parser.parse_known_args(unknown)

    return check_constraints_z3(commands)


@pytest.mark.parametrize(
    "argv, expected",
    [
        (["cmd", "integer", "10", "float", "2.3"], False),
        (["cmd", "integer", "12", "float", "2.3", "bool1"], True),
    ],
)
def test_args(argv, expected):
    sys.argv = argv
    assert verify() == expected


if __name__ == "__main__":
    verify()
