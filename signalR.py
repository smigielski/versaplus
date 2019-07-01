from requests import Session
from signalr import Connection
from urllib.parse import urlencode # python3
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
import websocket
import time

websocket.enableTrace(True)

def simple_get(session,url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(session.get(url, stream=True,timeout=60)) as resp:
            if is_good_response(resp):
                print(resp.headers)
                return resp.content
            else:
                print ("Bad response: " + str(resp.status_code) )
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    return resp.status_code == 200


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def build_url(uri,params,protocol="https"):
    base_url = protocol+"://mojaversa.pl"
    url= base_url+uri+"?"+urlencode(params)
    print("Build url: ",url)
    return url

#Configuration
mac = ""
id = ""
password = ""
with Session() as session:
    
    raw_html = simple_get(session,"http://mojaversa.pl/Home/Index")

    #print(raw_html is None)
    #time.sleep(10)
       #connect
    connectionStopped = False
    
    #create new chat topic handler
    def loading_redirect(action, data):
        print('REDIRECT: ', action, data)
        redirected = False
        while not redirected:
            raw_html2 = simple_get(session,build_url("/Home/"+action,{"hexCentralData":data,"connectionId":connectionId,"mac":mac,"id":id}))
            redirected = not raw_html2 is None
            print('Redirected: ',redirected)
           
    def loading_showNoAccess(action, data):
        print('SHOW NO ACCESS: ', action, data)
        
    def loading_error(msg):
        global connectionStopped
        print('ERROR: ', msg)
        connection.close()
        connectionStopped=True
        #TODO: reconnect?
        
    def loading_errorwithdata(msg, mac, serial):
        global connectionStopped
        print('ERROR WITH DATA: ', msg, mac, serial)
        connection.close()
        connectionStopped = True
        #TODO: reconnect?    
        
    def loading_update(message):
        print('UPDATE: ', message)
    
    def loading_setVersion(version):
        print('SET VERSION: ', version)
        
    def loading_writtenToServer():
        print('WRITTEN TO SERVER')

    
    def centralview_updatePartial(name):
        print("UPDATE PARTIAL: " , name)
        raw_html2 = simple_get(session,build_url("/Home/"+name,{"userId":connectionId}))
        print(raw_html2)
        
    def centralview_updateClearTrouble(status):
        print("UPDATE CLEAR TROUBLE: " , status)
        
    def centralview_initialDataFetched(zones, outputs):
        print("INITIAL DATA FETCHED: " , zones, outputs)
            
    def centralview_setUsername(username):
        print("SET USERNAME: " , username)
    
    def centralview_terminal1(title, lText, lDigit, rText, rDigit):
        print("terminal1: " , title, lText, lDigit, rText, rDigit)
        
    def centralview_terminal2(title, lText, lDigit, rText, rDigit):
        print("terminal2: " , title, lText, lDigit, rText, rDigit)
        
    def centralview_terminal3(title, Text, Digit):
        print("terminal3: " , title, Text, Digit)
        
    def centralview_finishedFetchingTopEvents():
        print("FINISHED FETCHING TOP EVENTS")
    
    def centralview_redirecting():
        print("REDIRECTING")

    def centralview_toggleTroublesInfo(exists):
        print("TOGGLE TROUBLES INFO: ",exists)

    def centralview_toggleTamperInfo(exists):
        print("TOGGLE TROUBLES INFO: ",exists)
        
    def centralview_toggleServiceInfo(exists):
        print("TOGGLE TROUBLES INFO: ",exists)
        
    def centralview_setVersion(version,name):
        print('SET VERSION: ', version+ name)
        
    #https://cntctbx.satel.pl:3030/
    #"AES/ECB/PKCS5Padding"
    #plainEncryptionKey
    
    connection = Connection("http://mojaversa.pl/signalr", session)

    loading = connection.register_hub('Loading')
        
    loading.client.on('redirect', loading_redirect)
    loading.client.on('showNoAccess', loading_showNoAccess)
    loading.client.on('error', loading_error)
    loading.client.on('errorwithdata', loading_errorwithdata)
    loading.client.on('update', loading_update)        
    loading.client.on('setVersion', loading_setVersion)    
    loading.client.on('writtenToServer',loading_writtenToServer)

    #get chat hub
    centralview = connection.register_hub('CentralView')
    
    centralview.client.on('updateClearTrouble',centralview_updateClearTrouble)
    centralview.client.on('initialDataFetched',centralview_initialDataFetched)
    centralview.client.on('setUsername',centralview_setUsername)
    centralview.client.on('updatePartial',centralview_updatePartial)
    centralview.client.on('terminal1',centralview_terminal1)
    centralview.client.on('terminal2',centralview_terminal2)
    centralview.client.on('terminal3',centralview_terminal3)
    centralview.client.on('finishedFetchingTopEvents',centralview_finishedFetchingTopEvents)
    centralview.client.on('redirecting',centralview_redirecting)
    centralview.client.on('toggleTroublesInfo',centralview_toggleTroublesInfo)
    centralview.client.on('toggleTamperInfo',centralview_toggleTamperInfo)
    centralview.client.on('toggleServiceInfo',centralview_toggleServiceInfo)    
    centralview.client.on('setVersion', centralview_setVersion)   
    
    
    connection.error += loading_error
    #start a connection
    connection.start()
    time.sleep(10)
    while not connection.started:
        print("connecting...")
        print(connection.id)

    connectionId = connection.id
   

    #create a connection
    raw_html = simple_get(session,build_url("/Home/SaveConnectionId",{"lang":"Pl","connectionId":connectionId,"mac":mac,"id":id,"password":password}))
    print(raw_html)


    if raw_html is None:
    #if connectionSaved:
        connection.close()
        connectionStopped = True
    

#    simple_get(build_url("/Home/GetUsername",{"userId":connectionId}))
    while not connectionStopped:
        time.sleep(1)
    
