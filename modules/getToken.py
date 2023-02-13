import requests
import json
    
def GetToken(uid : int,token : int):
    """_summary_

    Args:
        uid (int): uid of your account
        token (str): token of your account

    Returns:
        Dict: Dict of response. accessToken is in returns["accessToken"]
    """
    uid = str(uid);
    token = token;
    devicdId = "web|"+str(uid);
    url="https://passport.mahjongsoul.com/user/login";
    data={
        "uid": uid,
        "token": token,
        "deviceId": devicdId
    }
    response=requests.post(url,data=data);
    
    return json.loads(response.text);
        