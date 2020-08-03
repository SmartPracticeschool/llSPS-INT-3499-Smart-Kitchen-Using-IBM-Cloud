import time
import sys
import ibmiotf.application
import ibmiotf.device
import requests 
url = "https://www.fast2sms.com/dev/bulk"

#my iot platform device's credentials to connect the device and the platform
organization= "x4v4cr"
deviceType= "raspberrypi"
deviceId= "12345678"
authMethod= "token"
authToken="12345678"

def myCommandCallback(cmd):
        print("Command recevied : %s !" % cmd.data)


try:
    deviceOptions={"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken,}
    deviceCli= ibmiotf.device.Client(deviceOptions)
except Exception as e:
    print("Caught exception connection device: %s" % str(e))
    sys.exit()

deviceCli.connect()
#  since we are not using actual hardware to demonstarte.we assume a scenario which contains all the possible outputs
#  we assume weight of the jar to be 1500 grams
#  we know the weight of full cylinder is 30kgs.but we must colibrate our device such that it only takes the weight of
#the gas inside the cylinder and let us know if its empty.so we take the weight of the cylinder to be 15kgs(gas weight)

jar_weight=1500
cylinder_weight=15
Fan= "OFF"
leak="OFF"
i=0

#  variables cyl_empty are used as flogs.this is to be make sure that when we send the alerts sms,the alert is send
# only once until resets.so this prevents resending messages everytime the sensor detects empty in the loop
cyl_empty=0;
jar_empty=0

while True:
    #we assume the cylinder to be used 0.01 times in every loop.so we can demonstrate the stages of the cylinder and its stored   
    cylinder_weight=cylinder_weight-0.1;
    # one table spoon is 14 grams.hence we reduce 14 grams everytime to simulate takes sugar out of a jar with a tablespoon
    jar_weight=jar_weight-14;

    # Depending on the weight of the cylinder in kgs. the The current status of the gas is sent to the user.The condition is below
    
    if(cylinder_weight >0 and cylinder_weight<=5):
        status="LOW"
        time.sleep(0.1)
    elif(cylinder_weight >5 and cylinder_weight<=10):
        status="MEDIUM"
    elif(cylinder_weight >10 and cylinder_weight<=15):
        status="HIGH"
    else:
        cylinder_weight=0
        status="EMPTY"

        #If the cylinder goes empty,we alert the user by sending an sms that the cylinder has gone empty using FAST2SMS
        if(cyl_empty==0):
            payload ="sender_id-FSTSMS&message-the cyliner is empty!book new one.!&language-english&route-qt&numbers-7075714754"
            headers = {'authorization':"Btl4pw8vaiJ1hXYq3UHsIZDbFf5orOTymGSV2NMWLK7xCEcednx7LvdB3jHOhsRmCnJyXMQpaD02btG5",'context type' : "application/x-www.form-urlencoded",'cache-control': "no-cache",}
            response = requests.request("POST", url,data=payload,headers=headers)
            print(response.text)
            print("the cylinder is empty")
            # cyl_empty flog is changed toprevent repeating the sms until reset
            cyl_empty=1;

    # Depending on the weight of the cylinder in kgs. the The current status of the gas is sent to the user.The condition is below        

    if(jar_weight <300 and jar_weight>=0):  
         jar_status="LOW"
         time.sleep(0.1)
    elif(jar_weight >=300 and jar_weight<1000):
        jar_status="MEDIUM"
    elif(jar_weight >=1000 and jar_weight<=1500):
      jar_status="HIGH"
    else:
         jar_weight=0
         jar_status="EMPTY"
         if(jar_empty==0):
             print= ("The JAR is empty!")
             payload = "sender_id-FSTSMS&message-The content in the jar is empty!. refil to continue usage.&language-english&route-qt&numbers-7075714754,"
             headers ={'authorization': "Btl4pw8vaiJ1hXYq3UHsIZDbFf5orOTymGSV2NMWLK7xCEcednx7LvdB3jHOhsRmCnJyXMQpaD02btG5",'context type': "application/x-www.form-urlencoded"  ,'cache-control': "no-cache"}
             response = requests.request("POST", url ,data=payload, headers=headers)
             print(response.text)
             #cyl_empty flog is changes to 1 to prevent reporting the sms until reset
             jar_empty=1;

     #snce we are not using hardware to detect the gas leak,we simulate to show this condition is also taken care
     #we assume that after 50 loops,the gas starts leaking and we alert the user by sending on sms
    i=i+1
    if(i==50):
        print("Gas leakage is detected!check immediately!")
        payload = "sender_id-FSTSMS &message-The content in the jar is empty!. refil to continue usage.&language-english&route-qt&numbers-7075714754"
        headers ={'authorization':"Btl4pw8vaiJ1hXYq3UHsIZDbFf5orOTymGSV2NMWLK7xCEcednx7LvdB3jHOhsRmCnJyXMQpaD02btG5",'context type': "application/x-www.form-urlencoded",'cache-control': "no-cache" }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        
        #if there is gas leak, we turn on the exhaust fan
        fan="ON"
        leak="ON"

    #we store all our data collected i JSON format in as "data"    

    data= {'cylinder_weight' : round(cylinder_weight,2), 'status': status, 'leak':leak, 'jar_weight':jar_weight, 'jar_status':jar_status}

    #function to show if the data is published in our iot platform
    def myOnPublishCallback():
        print(" publish Cylinder_weight - %s " %round(cylinder_weight,2), "Cylinder_status-%s " %status,"Gas leakage_%s " %leak )

    #if we couldnt connect to the IBM platform, not connected to IOTF is printed.   
    success = deviceCli.publishEvent("Smart Kitchen","json", data ,qos=0, on_publish=myOnPublishCallback)
    
    if not success:
        print("not connected to IOTF")
    time.sleep(0.6)
    deviceCli.commandCallback= myCommandCallback
deviceCli.disconnect()



               
                
              
         
     
     
     
        
        
        
        
        
        
