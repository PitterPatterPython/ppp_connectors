from datetime import date, datetime
from typing import Dict, Any, List, Set, Union, Optional
from requests import Response
from requests.auth import HTTPBasicAuth
import sys
from .broker import make_request
from .helpers import check_required_env_vars, combine_env_configs, validate_date_string


env_config: Dict[str, Any] = combine_env_configs()

def twilio_lookup(phone_number: str, data_packages: list=[], **kwargs: Dict[str, Any]) -> Response:
    """query information on a phone number so that you can make a trusted interaction with your user.
        With this endpoint, you can format and validate phone numbers with the free Basic Lookup request
        and add on data packages to get even more in-depth carrier and caller information.

    Args:
        phone_number (str): The phone number to look up
        data_packages (list): A Python list of fields to return. Possible values are validation,
            caller_name, sim_swap, call_forwarding, line_status, line_type_intelligence, identity_match,
            reassigned_number, sms_pumping_risk, phone_number_quality_score, pre_fill.

    Returns:
        Response: requests.Response json response from the request
    """

    # Define required environment variables
    required_vars: List[str] = [
        'TWILIO_API_SID',
        'TWILIO_API_SECRET'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    # Valid set of data packages for Twilio. Compare the ones that the user passed in
    # to ensure that they've passed valid ones. Exit immediately if they didn't.
    valid_data_packages: Set = {'validation', 'caller_name', 'sim_swap',
                           'call_forwarding', 'line_status', 'line_type_intelligence',
                           'identity_match', 'reassigned_number', 'sms_pumping_risk',
                           'phone_number_quality_score', 'pre_fill'}
    data_packages_set: Set = set(data_packages)
    invalid_packages =  data_packages_set - valid_data_packages
    if len(invalid_packages) != 0:
        print(f'[!] Error: "{", ".join(invalid_packages)}" are not valid data packages. Valid '
              f'packages include {", ".join(valid_data_packages)}', file=sys.stderr)
        sys.exit(1)

    method: str = 'get'
    url: str = f'https://lookups.twilio.com/v2/PhoneNumbers/{phone_number}'

    auth = HTTPBasicAuth(env_config['TWILIO_API_SID'], env_config['TWILIO_API_SECRET'])

    params: Dict = {
        'Fields': ','.join(data_packages),
        **kwargs
    }

    result: Response = make_request(method=method, url=url, auth=auth, params=params)

    return result

def twilio_usage_report(start_date: Union[str, date],
                        end_date: Optional[Union[str, date]]=None) -> Response:
    """Return a usage report for all activities between the start_date and end_date.

    Args:
        start_date (Union[str, date]): Only include usage that has occurred on or after this
            date. Specify the date in GMT and format as YYYY-MM-DD
        end_date (Optional[Union[str, date]], optional): Only include usage that occurred on
            or before this date. Specify the date in GMT and format as YYYY-MM-DD. Defaults to None.

    Returns:
        Response: requests.Response json response from the request
    """

    # Define required environment variables
    required_vars: List[str] = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_API_SID',
        'TWILIO_API_SECRET'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    if end_date is None:
        end_date: str = datetime.now().strftime("%Y-%m-%d")

    if not validate_date_string(start_date) or not validate_date_string(end_date):
        print(f'[!] Error: One of your start date {start_date} or end date {end_date} '
              'does not match the format YYYY-MM-DD')
        sys.exit()


    method: str = 'get'
    url: str = f'https://api.twilio.com/2010-04-01/Accounts/{env_config["TWILIO_ACCOUNT_SID"]}/Usage/Records.json'

    auth = HTTPBasicAuth(env_config['TWILIO_API_SID'], env_config['TWILIO_API_SECRET'])

    params: Dict = {
        'StartDate': start_date,
        'EndDate': end_date
    }

    result: Response = make_request(method=method, url=url, auth=auth, params=params)

    return result