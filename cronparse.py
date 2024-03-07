# pyright: strict
import re
import pytest

def parse_cron_schedule(cron_schedule: str) -> dict[str, list[int]]:
    """
    Parse a cron schedule and return a dictionary with individual components.
    """
    components: list[str] = cron_schedule.split()

    if len(components) != 5:
        raise ValueError("Invalid cron schedule format. Must have 5 components.")

    minute, hour, day_of_month, month, day_of_week = components

    return {
        'minute': parse_cron_component(minute, list(range(60))),
        'hour': parse_cron_component(hour, list(range(24))),
        'day_of_month': parse_cron_component(day_of_month, list(range(1,32))),
        'month': parse_cron_component(month, list(range(1,13))),
        'day_of_week': parse_cron_component(day_of_week, list(range(7))),
    }

def parse_cron_component(component: str, options: list[int]) -> list[int]:
    """
    Parse a single cron component (minute, hour, etc.) and return a list of values.
    """
    # Check the simplest case
    if component=='*':
        return options

    # Check for dash operator
    dash_matches = re.search(r"^(\d{1,2})-(\d{1,2})$", component)
    if dash_matches is not None:
        mini, maxi = int(dash_matches.group(1)), int(dash_matches.group(2))
        if mini < min(options) or maxi > max(options) or mini >= maxi:
            raise ValueError(f"Invalid dash operator {component} for {options}") 
        return list(range(mini, maxi + 1))

    # Check for comma seperated values
    comma_matches = re.findall(r"^\d{1,2}(?:,\d{1,2})*$", component)
    if comma_matches:
        print(f"commacase for {component}")
        return [ int(x) for x in comma_matches[0].split(",") ]

    # Check for slash operator
    interval_matches = re.search(r"^(\*|\d{1,2}-\d{1,2})/(\d{1,2})$", component)
    if interval_matches:
        new_options = parse_cron_component(
            interval_matches.group(1),  
            options  
        )
        interval = int(interval_matches.group(2))
        return new_options[::interval]  # [1, 3, 5]


    raise ValueError(f"Could not evaluate cron expression {component}")


# Example usage:
if __name__ == "__main__":
    cron_schedule = "1 2,5 1-10 */2 1,3"
    print("Example:")
    print(cron_schedule)
    parsed_schedule = parse_cron_schedule(cron_schedule)
    print(parsed_schedule)

@pytest.mark.parametrize("schedule,expanded", [
    (
        "* * * * *",
        {
            'minute': list(range(60)),
            'hour': list(range(24)), 
            'day_of_month': list(range(1,32)),
            'month': list(range(1,13)), 
            'day_of_week': list(range(7)), 
        }
    ),
    (
        "1 * * * *",
        {
            'minute': [1],
            'hour': list(range(24)), 
            'day_of_month': list(range(1,32)),
            'month': list(range(1,13)), 
            'day_of_week': list(range(7)), 
        }
    ),
    (
        "30 1,5 20-30 */2 1,3,5",
        {
            'minute': [30],
            'hour': [1,5], 
            'day_of_month': [20,21,22,23,24,25,26,27,28,29,30],
            'month': [1,3,5,7,9,11], 
            'day_of_week': [1,3,5], 
        }
    ),
    (
        "*/15 2,5 1-10 */2 1,3",
        {
            'minute': [0,15,30,45],
            'hour': [2,5], 
            'day_of_month': [1,2,3,4,5,6,7,8,9,10],
            'month': [1,3,5,7,9,11], 
            'day_of_week': [1,3], 
        }
    ),
])
def test_cron_parser(schedule: str, expanded: dict[str, list[int]]):
    parsed_schedule = parse_cron_schedule(schedule)
    assert parsed_schedule == expanded 

def test_value_error():
    with pytest.raises(ValueError):
        parse_cron_schedule("3-2 * * * *")
        parse_cron_schedule("* * * * * *")
    
