import requests
import json
import random
    
def GetToken(uid : str,token : str):
    """_summary_

    Args:
        uid (str): uid of your account
        token (str): token of your account

    Returns:
        Dict: Dict of response. accessToken is in returns["accessToken"]
    """
    
    devicdId = "web|"+uid;
    url="https://passport.mahjongsoul.com/user/login";
    data={
        "uid": uid,
        "token": token,
        "deviceId": devicdId
    }
    response=requests.post(url,data=data);
    
    return json.loads(response.text);


def GetVersion():
    """_summary_

    Returns:
        Dict: Dict of response. key include version, force_version, code
    """
    randv=random.randrange(1,10000000000000000);
    url="https://game.mahjongsoul.com/version.json"
    params={
        "randv": randv
    }
    response=requests.get(url,params=params);
    
    return json.loads(response.text);