import sys
import re
from rich import print
from collections import defaultdict

opre = re.compile(r"Operator ([a-z\-]+), statuses: \[(.*)\].*")
conditions = re.compile(r"\{(.+?)\}")
condition = re.compile(
    r"([A-Za-z]+) (False|True) ([0-9a-zA-Z\-]+ [0-9a-zA-Z\:]+ [0-9a-zA-Z\-\+]+ [A-Z]+) (.*)"
)


def parse(log):
    table = defaultdict(dict)
    for operator, status in opre.findall(log):
        for cond in conditions.findall(status):
            for name, result, timestamp, reason in condition.findall(cond):
                table[operator][name] = {
                    "result": result == "True",
                    "timestamp": timestamp,
                    "reason": reason,
                }

    return table


def filter_operators(
    table,
    required_conditions,
    aggr,
):
    return {
        operator_name: operator_conditions
        for operator_name, operator_conditions in table.items()
        if aggr(
            any(
                condition_values["result"] == required_condition_result
                for condition_name, condition_values in operator_conditions.items()
                if condition_name == required_condition_name
            )
            for required_condition_name, required_condition_result in required_conditions
        )
    }


def main():
    table = parse(sys.stdin.read())

    print(
        filter_operators(
            table,
            (
                ("Degraded", False),
                ("Available", True),
                ("Progressing", False),
            ),
            aggr=all,
        )
    )

    print(
        filter_operators(
            table,
            (
                ("Degraded", True),
                ("Available", False),
                ("Progressing", True),
            ),
            aggr=any,
        )
    )


if __name__ == "__main__":
    main()
