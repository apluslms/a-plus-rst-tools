import re
from typing import Any, Dict, Optional

from sphinx.errors import SphinxError


# Valid date formats are the same as in function parse_date() in
# toc_config.py:
# 1. 'YYYY-MM-DD [hh[:mm[:ss]]]'
# 2. 'DD.MM.YYYY [hh[:mm[:ss]]]'
date_format = re.compile(
    r"^(\d\d\d\d-\d\d-\d\d|\d\d.\d\d.\d\d\d\d)" # YYYY-MM-DD or DD.MM.YYYY
    "( \d\d(:\d\d(:\d\d)?)?)?$")                # [hh[:mm[:ss]]]


# A delay string consists of 3 parts:
# 1. Plus sign
# 2. Number
# 3. Unit: [d]ay, [h]our, [m]inute/[min]ute
# With optionally spaces between the parts
delay_format = re.compile(
    r"^\+ ?(?P<number>\d+) ?(?P<unit>d|h|m|min)$"
)


def parse_reveal_rule(
        rule_str: Optional[str],
        source: Optional[str],
        line: Optional[int],
        opt: Optional[str]
        ) -> Optional[Dict[str, Any]]:
    def reveal_rule_error(msg: str):
        base_msg_parts = []
        if source is not None:
            base_msg_parts.append(source)
        if line is not None:
            base_msg_parts.append(f"line {line}")
        if opt is not None:
            base_msg_parts.append(f"option '{opt}'")
        base_msg = ", ".join(base_msg_parts) + ":\n"
        raise SphinxError(base_msg + msg)

    if rule_str is None:
        return None

    rule_str = rule_str.strip()
    space_index = rule_str.find(' ')
    if space_index > -1:
        trigger = rule_str[:space_index]
        argument = rule_str[(space_index + 1):].strip()
    else:
        trigger = rule_str
        argument = None

    result: Dict[str, Any] = {'trigger': trigger}

    if trigger in ['immediate', 'manual', 'completion']:
        if argument is not None:
            reveal_rule_error(
                "Unexpected argument in reveal rule. When using the 'manual', 'immediate' or\n"
                "'completion' mode, no arguments are expected after the mode name.\n"
            )

    elif trigger == 'time':
        if argument is None:
            reveal_rule_error(
                "Reveal time was not provided. When using the 'time' reveal mode, a time must be\n"
                "provided after the mode name.\n"
            )
        if date_format.match(argument):
            result['time'] = argument
        else:
            reveal_rule_error(
                "Reveal time was formatted incorrectly. When using the 'time' reveal mode, use\n"
                "one of the following formats:\n"
                "1. 'YYYY-MM-DD [hh[:mm[:ss]]]', e.g., '2020-01-16 16:00'\n"
                "2. 'DD.MM.YYYY [hh[:mm[:ss]]]', e.g., '16.01.2020 16:00'\n"
            )

    elif trigger in ['deadline', 'deadline_all']:
        if argument is not None:
            match = delay_format.match(argument)
            if match:
                number = int(match.group('number'))
                unit = match.group('unit')
                if unit == 'd':
                    minutes = 24 * 60 * number
                elif unit == 'h':
                    minutes = 60 * number
                else:
                    minutes = number
                result['delay_minutes'] = minutes
            else:
                reveal_rule_error(
                    "Delay was formatted incorrectly. When using the 'deadline' or 'deadline_all'\n"
                    "reveal mode, a delay can optionally be provided after the mode name. Format the\n"
                    "delay like this:\n"
                    "'+<number><unit>', where unit is 'd' (days), 'h' (hours) or 'm'/'min' (minutes)\n"
                    "e.g., '+1d', '+2h', '+30m', '+30min'\n"
                )

    else:
        reveal_rule_error(
            "Unexpected reveal mode. Supported modes are 'manual', 'immediate', 'time',\n"
            "'deadline', 'deadline_all' and 'completion'.\n"
        )

    return result
