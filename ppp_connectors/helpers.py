import sys
from typing import Dict, Set, List

def check_required_env_vars(config: Dict[str, str], required_vars: List[str]) -> None:
    """Ensure that the env variables required for a function are present in the .env file.

    Args:
        config (Dict[str, str]): the env_config variable that contains values from the .env file
        required_vars (List[str]): the env variables required for a function to successfully function
    """

    missing_vars: Set[str] = set(required_vars) - set(config.keys())
    if missing_vars:
        print(f"[!] Error: missing required environment variables: {', '.join(missing_vars)}. "
              "Please ensure these are present in your .env file.", file=sys.stderr)
        sys.exit(1)