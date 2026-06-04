from pydantic import BaseModel
from datetime import datetime

#usr_mac_id: the id of the machine from which we are getting the request
#usr_level: can be INFO or ERR
#usr_ts: time of the message GMT
#usr_msg: Actual text of the message

class User_log(BaseModel):
    usr_cl_name: str
    usr_level: str = "LOG", "ERR"
    usr_msg: str
    usr_cl_ts: datetime
