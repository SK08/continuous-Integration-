#   THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
#   FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.

from java.lang import Thread

def checkProxies():
  try:
    proxies
    return True
  except NameError:
    return False

def printSteps(taskInfo, verbose=False):
  if not checkProxies():
    print 'INFO: This function requires proxies. Start the cli using -expose-proxies.'
    return
    
  for i in range(taskInfo.nrOfSteps):
    info = proxies.taskRegistry.getStepInfo(taskInfo.id, i + 1, None).entity
    print '#' + str(i + 1) + '  ' + info.state + '\t' + info.description
    if verbose: 
      print info.log

def startUpgrade(appName, newVersion, targetEnvironment):
  envId = "Environments/" + targetEnvironment
  if not repository.exists(envId):
    print "ERROR: No environment named '%s' found" % (envId)
    return
  currentDeployment = None
  
  # find current deployment
  for deployedApps in repository.search("udm.DeployedApplication", envId):
    deployedAppName = deployedApps.replace(envId + '/', '')
    if deployedAppName == appName:
      currentDeployment = deployedApps

  if currentDeployment is None:
    print "ERROR: No existing deployment of '%s' to '%s'" % (appName, targetEnvironment)
    return
  
  print "Upgrading existing deployment '%s'" % (currentDeployment)
  upgrade = deployment.prepareUpgrade("Applications/%s/%s" % (appName, newVersion), currentDeployment)
  
  print "Validating deployment"
  deployment.validate(upgrade)
  taskInfo = deployment.deploy(upgrade)

  print "Starting deployment '%s' (ID: '%s')" % (taskInfo.label, taskInfo.id)
  deployit.startTask(taskInfo.id)
  taskState = 'EXECUTING'
  
  while taskState == 'EXECUTING':
    Thread.sleep(5000)
    taskInfo = deployit.retrieveTaskInfo(taskInfo.id)
    taskState = taskInfo.state
    currentStep = taskInfo.currentStepNr
    print "Task now at step %s of %s. State: %s" % (currentStep, taskInfo.nrOfSteps, taskState)
        
  taskInfo = deployit.retrieveTaskInfo(taskInfo.id)
  print "Final task state: %s after %s of %s steps" % (taskInfo.state, min(currentStep + 1, taskInfo.nrOfSteps), taskInfo.nrOfSteps)
  printSteps(taskInfo, True)
  if taskInfo.state != 'DONE':
    print "WARN: Deployment was not completed successfully. Please log in to Deployit to review the deployment or contact a Deployit administrator"
  return
