
from dotenv import dotenv_values, find_dotenv
import os
import sys
from typing import Dict, Set, List, Any


def check_required_env_vars(config: Dict[str, str], required_vars: List[str]) -> None:
    """Ensure that the env variables required for a function are present either in \
        the .env file, or in the system's environment variables.

    Args:
        config (Dict[str, str]): the env_config variable that contains values from the .env file
        required_vars (List[str]): the env variables required for a function to successfully function
    """

    dotenv_missing_vars: Set[str] = set(required_vars) - set(config.keys())
    osenv_missing_vars: Set[str] = set(required_vars) - set(os.environ)
    missing_vars = dotenv_missing_vars | osenv_missing_vars

    if dotenv_missing_vars and osenv_missing_vars:
        print(f'[!] Error: missing required environment variables: {", ".join(missing_vars)}. '
              'Please ensure these are present either in your .env file, or in the '
              'system\'s environment variables.', file=sys.stderr)
        sys.exit(1)

def combine_env_configs() -> Dict[str, Any]:
    """Find a .env file if it exists, and combine it with system environment
        variables to form a "combined_config" dictionary of environment variables

    Returns:
        Dict: a dictionary containing the output of a .env file (if found), and
        system environment variables
    """

    env_config: Dict[str, Any] = dict(dotenv_values(find_dotenv()))

    combined_config: Dict[str, Any] = {**env_config, **dict(os.environ)}

    return combined_config