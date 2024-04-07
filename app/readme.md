# Installation Guide 
This installation guide has been written to work through WSL Ubuntu

### Starting the minikube instance:
```sh
minikube start
```

### Execute the following command to make sure the usage of local images is possible:
```sh
eval $(minikube -p minikube docker-env)
```

### Build the docker image for the webapp
```sh
docker build -t webapp ./webapp/
``` 

### Installation of the deployment
```sh
helm dependency update
helm dependency build
helm install e-corp ./e-corp/
``` 

### Enable ingress-nginx on minikube
```sh 
minikube addons enable ingress
``` 

### Accessing the application
After a minute or so, the ingress will have received an IP address, you can check this using `kubectl get ingress`. \
When the ingress has received an IP address, use the command `minikube tunnel` to tunnel your wsl minikube to your windows machine. (sudo permission is required)

### Adding address to /etc/hosts
It is important to add the following entry to your /etc/hosts file in windows:
> 127.0.0.1 e-corp.info 

The file should be located in the following directory:
> C:\Windows\System32\drivers\etc

Now that this is completed, you should be abled to access the webapplication by typing in e-corp.info as the URL.