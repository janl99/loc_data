h1 Project Name: loc_data

h2 Receive Data

Project will receive loc data from  location service, android client,location device ...
Project will receive loc data by http protocol on  POST method.

Project will receive loc data and save its into MongoDB for two colles :
last_postion and history_postion.

last_postion only on record for where one kid: appid:userid,when newly loc data received update it ,if not exist insert it.

history_postion insert for kid at time data.


h2 Get Data

Application Get loc data from this site by http protocol on GET method.

Application Get interface for get_last_loc_data,get_history_loc_data.

get_last_loc_data(appid,[useid]) return loc data list.

get_history_loc_data(appid,userid,starttime,endtime) return loc data list.


