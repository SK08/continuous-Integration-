# continuous-Integration
#Building a package from properties files/dictionaries/command arguments
createdar.py builds a package in XL Deploy from properties which can be specified in and combination of 3 different locations:

File
XL Deploy dictionary
Command arguments
This will create a package with an arbitrary number of artifacts and is useful in situations where the build process does not feature a tool where there is an existing XL Deploy integration, such as with Jenkins. Optionally, this script can also deploy the package into an environment.

Before looking at the script execution, first lets take a look at the properties format. The following example will build a package with 2 artifacts, a WAR artifact and a JBoss datasource.

artifact.type=jee.War
artifact.fileLocation=/Users/tom/qb\_repo/builds/17/artifacts/dist/Cars\_Sample\_App.war
artifact.name=Cars\_Sample\_App
artifact.tags=['WAR']
datasource.type=jbossas.NonTransactionalDatasourceSpec
datasource.name=Tom\_Datasource
datasource.jndiName=jndi/tomsds
datasource.userName={{DB\_USERNAME}}
datasource.password={{DB\_PASSWORD}}
datasource.connectionUrl={{DB\_CONNECTION\_URL}}


 There are a number of items of note the the above example:

Keys are always in the format artifactID.property. Where artifactID is a identifier used by the script for each artifact and property is the property to set on that artifact.
All artifacts must have a name and type property.
When a fileLocation property is set, this must refer to the path of a file on the file system where the script is being executed.
When specifing something which is list type in XL Deploy, such as tags, then these must be specified using Python list literal format.
Placeholders can be used just as when creating artifacts in the XL Deploy UI.
The above format can be used to specify the properties in a XL Deploy dictionary. The dictionary must be stored in 'Environments/AppDictionaries/<AppName>' by convention.

Properties can also be set as a command line argument to the script. When using this approach these properties must be set using Python dict literal format. For example:

"{'webContent.type' : 'www.WebContent', 'webContent.name' : 'myWebContent', 'webContent.fileLocation' : '/Users/tom/scratch/PetPortal\_pages.zip'}"


To use the script:

cli.sh -host <XLDeployHost> -username <username> -password <password> -f $ScriptPath/createDar.py -- -n <appName> -b <buildID> -p <propertiesFile> -a <autoDeploy true|false> -e <deployEnv> -x <extraProperties>


For example:

cli.sh -username admin -password deploy -source /Users/tom/Documents/CreateDARCLI/createDAR.py -- -n TestApp -b 1.0-6 -p /Users/tom/builds/propertiesSample.properties -x "{'webContent.type' : 'www.WebContent', 'webContent.name' : 'myWebContent', 'webContent.fileLocation' : '/Users/tom/scratch/PetPortal\_pages.zip'}" -a true -e "MyEnvironment"


This will create a package called "1.0-6", from the build argument, for application "TestApp". It will also deploy this to "MyEnvironment"
