import requests
import json
    
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
        
