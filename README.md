![](https://github.com/cwendt94/espn-api/workflows/Espn%20API/badge.svg)
![](https://github.com/cwendt94/espn-api/workflows/Espn%20API%20Integration%20Test/badge.svg) [![codecov](https://codecov.io/gh/cwendt94/espn-api/branch/master/graphs/badge.svg)](https://codecov.io/gh/cwendt94/espn-api) [![Join the chat at https://gitter.im/ff-espn-api/community](https://badges.gitter.im/ff-espn-api/community.svg)](https://gitter.im/ff-espn-api/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![PyPI version](https://badge.fury.io/py/espn-api.svg)](https://badge.fury.io/py/espn-api)

# ff-espn-api -> espn-api
## ESPN API
## **ff_espn_api will be transitioning to espn_api! espn_api will have all of the features that ff_espn_api has just different import syntax and folder structure. espn_api will now be supporting multiple ESPN fantasy sports starting with basketball!**  
## **ff_espn_api version 1.8.9 will still be avaiable but will no longer be updated. To get the newest updates switch over to espn_api!**

This package uses ESPN's Fantasy API to extract data from any public or private league for **Fantasy Football and Basketball**.  
Please feel free to make suggestions, bug reports, and pull request for features or fixes!

This package was inspired and based off of [rbarton65/espnff](https://github.com/rbarton65/espnff).

## Installing
With Git:
```
git clone https://github.com/cwendt94/espn-api
cd espn-api
python3 setup.py install
```
With pip:
```
pip install espn_api
```

## Usage
```python
# Football API
from espn_api.football import League
# Basketball API
from espn_api.basketball import League
# Init
league = League(league_id=222, year=2019, username='username', password='password')
```
[For more usage and API details head over to the Wiki!](https://github.com/cwendt94/espn-api/wiki)

### Run Tests
```
python3 setup.py nosetests
```

## Issue Reporting
If you find a bug follow the steps below for reporting.

1. Open a [new issue](https://github.com/cwendt94/espn-api/issues) with a brief description of the bug for the title. In the title also add which sport (Football or Basketball)

2. Run the application in debug mode to view ESPN API request's and response's
    ```python
    # ... import statement above
    league = League(league_id=1245, year=2019, debug=True)
    ```
    The application will print all requests and the response from ESPN's API in the console. I would suggest piping the console output to a text file as it will be a lot of data.

3. Find the last log before the crash and copy it in the issue descrption with the line number of the crash or possible bug.

4. Submit the new issue!

I will try to comment on the issue as soon as possible with my thoughts and possible fix!