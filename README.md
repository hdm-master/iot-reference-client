# Quick Start
Prerequisites: 
- Zaikio User account for the test or live directory

1. git clone -b master https://gitlab.prinect-lounge.com/iot/iot-reference-client.git
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


Open the debug monitoring tool du verify your message: \
    [Test environment](http://monitor.iot.stg.connectprint.cloud) \
    [Live environment](https://monitor.iot.connectprint.cloud) 



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

![Architectural Overview](iot_reference_client_class_diagram.png)
Check comments in classes for further information

#### Telemetry
##### Topic
The topic used for telemetry messages is
"$aws/rules/iot_data_platform_telemetry_{env}/{YOUR_ORD_ID}/{YOUR_CLIENT_ID}"

#### Shadow Service
Info: Currently the shadow functionality is not supported by the iot platform.
##### Reference Client implementation of shadow state sync
The ShadowHandler implements updating the device state via the AWS
Shadow Service. The ShadowHandler updates the device state as soon as the
IoTClient connects the device successfully. It takes care of listening for
updates (desired states) and publishing of state changes (reported states).

## Licenses
Show [Licenses](licenses.txt) or generate them with the command ``pip-licenses`` in the pipenv environment