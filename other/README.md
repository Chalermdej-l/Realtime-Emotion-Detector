
# Table of Contents

1. [Clone the Project and Download Data](#1-clone-the-project-and-download-data)
2. [Train Model and Infrastructure Initialization](#2-train-model-and-infrastructure-initialization)
3. [Dockerize Model and Infrastructure Initialization](#3-dockerize-model-and-infrastructure-initialization)
4. [Monitor the Event](#4-monitor-the-event)
5. [Clean up](#5-clean-up)

## 1. Clone the Project and Train Model

First, clone the project and navigate to the cloned directory:

```
git clone https://github.com/Chalermdej-l/Realtime-Emotion-Detector.git
cd Realtime-Emotion-Detector
```
Run the following command to install the required packages and train the model:

```
make prerequisite
```

Download the data from [FER2013](https://www.kaggle.com/datasets/msambare/fer2013)

After downloading the data, use the [code](code/mood-experiment.ipynb) to train the model. Note that training time may vary depending on your machine; however, with a GPU-equipped PC, training shouldn't take too long.

I have included the model in the following download links for
[Emotion detection](https://drive.google.com/file/d/1iTQrqv1XeZSz1rGgYEe5WADyVFPYRhz6/view?usp=drive_link) and [Face detection](https://drive.google.com/file/d/1uNAEKGE8q3WbcL6RkSL-K5E8wnViwZeb/view?usp=drive_link)

The face detection model is pretrained and sourced from this [Github](https://github.com/opencv/opencv/tree/master/data/haarcascades)

Once the model is trained, please place the model in this [Folder](cloud/model)

![](/image/setup/1.png)

## 2. Dockerize Model and Infrastructure Initialization

After placing the trained model in the correct folder, run the following command to dockerize the code and the model:

```
make docker-build
```

![](/image/setup/2.png)

Then run the following command to authenticate with Azure CLI:
```
make az-login
```
![](/image/setup/3.png)

After login, run the following command to initialize the Terraform project. Note that you can change the settings in this [file](infra/variables.tfvars) 

```
make infra-setup
```
![](/image/setup/4.png)



## 3. Infrastructure Create and Deploy

Then run the following command to create Azure Container Registry:

```
make infra-create-regis
```
![](/image/setup/5.png)

![](/image/setup/6.png)

Then run the following command to push our Docker image to the Container Registry:

```
make docker-deploy
```
![](/image/setup/7.png)

![](/image/setup/8.png)

After the image is pushed, we can now create the rest of the resources. Run the following code to create Azure Function and other necessary resources:

```
make infra-create-func
```
![](/image/setup/9.png)
![](/image/setup/10.png)

The function is already set up with a webhook with our container registry:

![](/image/setup/11.png)

And the image will be repulled every restart or update:
![](/image/setup/12.png)

## 4. Cloud Usage
After the function is created, run the following command to output the function URL:

```
make infra-output
```
![](/image/setup/13.png)

Please update the URL in the [.env](.env) file.

To call the function, you will need some sample images or videos in this [folder](input)

To process the image to the cloud, please run the following command:

```
make predict-img-prod
```

To process the video to the cloud, please run the following command:
```
make predict-vid-prod
```

The request will be processed by the function and returned to the caller:

![](/image/setup/15.png)

The file will be output in this [folder](output)

![](/image/setup/19.png)

## 5. Local Usage

You can call the model using the following code to process the data locally:

Image
```
make predict-img-lite
```
Video
```
make predict-vid-lite
```
Live Video
```
make predict-live-lite
```
Sample output 
![](/image/setup/16.png)
![](/image/setup/17.png)
![](/image/setup/18.png)

## 6. Clean up

After finishing with the reproduction, you can run the following command to plan the resource removal:

```
make  infra-down-p
```
![](/image/setup/20.png)

If there are no issues with the plan removal, run the following to remove all resources:
```
make  infra-down-c
```
![](/image/setup/21.png)
