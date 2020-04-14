# Quick Start
Prerequisites: 
- Zaikio User account for the test or live directory
    - [Zaikio Test](https://directory.sandbox.zaikio.com)
    - [Zaikio Live](https://directory.zaikio.com)
1. git clone -b master https://github.com/hdm-master/iot-reference-client.git
2. cd into iot-reference-client
3. pipenv install
4. set the environment variables for test or live environment. Utilize pipenv to do so: ```export
 PIPENV_DOTENV_LOCATION=./env.test```
5. run the demo: ```pipenv run python samples/run_telemetry_demo.py```   


### Setup
The reference client is based on python 3.7 and [pipenv](https://pipenv-fork.readthedocs.io/en/latest/)
as a virtual environment and dependency management tool.

**{PROJECT_ROOT}** is the place holder for the path where you stored / cloned the reference-client project
        
    pip install pipenv
    cd {PROJECT_ROOT} 
    pipenv install

### Authentication
The class Zaikio Manager will connect you with the directory and will utilize the "device auth flow" to
establish a OAuth connection with the relevant provisioning service to provide a valid access token

### Run the demo   
Make sure to set environment variables before you start the demo.
You will have a env.* file for each environment (test and live)
We will use our virtual environment (pipenv) to set the environment variables.


Mac / Linux user: 

    cd {PROJECT_ROOT} 
    export PIPENV_DOTENV_LOCATION=./env.test  
    
Windows user: 

    cd {PROJECT_ROOT} 
    set PIPENV_DOTENV_LOCATION=.\env.test  


Then start the virtual environment with

    pipenv shell
    
        
*We recommend you to run the reference client against our stage (env.test) environment 
since the development environment is under heavy development and you don't want to clutter your live environment 


#### Telemetry demo

Send telemetry messages and sync the state by running:

    python ./src/run_telemetry_demo.py


Open the debug monitoring tool du verify your message:
 - [Test environment](http://monitor.iot.stg.connectprint.cloud) 
 - [Live environment](https://monitor.iot.connectprint.cloud) 



#### Further explanations

##### Authentication store

The connection is secured by X.509 certificates (both ways). The client verifies the
server by it's server certificate and the server authenticates the client by
it's individual signed client certificate.


**Please be aware that this process is only for demo purposes. You should store the data securely** 
If you run the demo for the first time the certificates, keys and properties will be created, downloaded and stored
 for you in the folder ```certificate_store``` in ```{PROJECT_ROOT}```. 
On the next run the certs will be reused.
Please be aware that for every provisioning call new assets will be created in the backend.

The IoT Core certificate is signed by an Amazon Root Certificate and has to be
present as "AmazonRootCA1.pem".

The ```certificate_store``` folder should have these files:

Please be aware the files in the certificate_store are **environment depended**.

- amazonRootCA1.pem -> Sever certificate (provided by the Onboarding Manager)
- devicePrivateKey.pem -> Private Key of the device (created by the client itself)
- deviceCert.pem -> Device Cert (provided by the Onboarding Manager)
- properties.json -> json file with relevant properties (provided by the Onboarding Manager)

      {
      "mqtt_endpoint": Iot mqtt endpoint,
      "mqtt_port": standard IoT MQTT port,
      "machine_region": machine region of IoT cloud,
      "telemetry_topic": The mqtt telemetry topic,
      "client_id": The name of your IoT device,
      "org_id": Your organization id of the directory,
      "machine_id": The generated machine id in the directory,
      "site_id": The assigned site id of your machine provsioned in the directory
      }



One sender can only have one connection to the IoT Core at the same time.

### Unit Tests

The unit tests are integrated into the top level testing package:

    cd {PROJECT_ROOT}
    pipenv run python -m unittest discover src
    
or    
    
    cd {PROJECT_ROOT}
    pipenv shell
    python -m unittest discover src


### Architecture
![Class Diagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.github.com/hdm-master/iot-reference-client/master/docs/cd-iot_assets.puml)
#### Telemetry
There is a dedicated topic for telemetry data. You will get the topic name from the configuration service. 
Check the following method: ```ProvisioningManager._fetch_configuration()``

Additionally, you have to add your ord_id and your client_id to the topic structure

eg. "{Telemetry_Topic_name}/{YOUR_ORD_ID}/{YOUR_CLIENT_ID}"
check method ```Sender.publish_telemetry()``` for more details.

#### Shadow Service

We are using the aws shadow service to synchronize device state and cloud state.
Device Shadow is a persistent virtual ‘shadow’ of a Thing defined in AWS IoT Registry. 
Basically, it’s a JSON State Document that is used to store and retrieve current state information for a thing. 
You can interact with a Device Shadow using MQTT Topics or REST API calls. 
The main advantage of Shadows is that you can interact with it, 
regardless of whether the thing is connected to the Internet or not. 

####Reference Client Implementation 

![Ref Client State Handling](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.github.com/hdm-master/iot-reference-client/master/docs/sq-state-handling.puml)

####Shadow sync flow

Update topic creates a thing shadow if it doesn’t exist, 
or updates the content of a thing shadow with the “desired” or “reported” state data provided in the request. 
Messages are sent to all subscribers with the difference between “desired” or “reported” state (using delta topic).

#####Links
See the following aws documentation for further details:
- https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-data-flow.html
- https://iotbytes.wordpress.com/device-shadows-part-1-basics/

####Thing State Object:

######SendTelemetryData
This attribute is set during provisioning by the provisioning service and indicates the senders "permission" to send 
telemetry data. 
Please check this state property **before** sending telemetry data.
check method ```Sender.publish_telemetry()``` for more details.
e.g.

        {sendTelemetryData: True}


## Licenses
Show ![Licenses](./docs/licenses.txt) or generate them with the command ``pip-licenses`` in the pipenv environment

