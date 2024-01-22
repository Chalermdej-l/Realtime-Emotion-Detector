# Realtime_Emotion_Detection

This project is the final project for [Machine Learning Zoomcamp](https://github.com/DataTalksClub/machine-learning-zoomcamp/tree/master) course. The project focuses on developing facial emotion detection using the [FER2013](https://www.kaggle.com/datasets/msambare/fer2013)  dataset from Kaggle. Employing a Convolutional Neural Network with VGG architecture, the model is adept at recognizing emotions in images, videos, or live webcam feeds. Offering both local and cloud deployment options, the model is Dockerized and deployed on Azure Container Registry, with an Azure Function webhook ensuring continuous updates. The Azure Function doubles as a frontend API endpoint, enabling users to submit images or videos and receive processed results with embedded emotion predictions, enhancing accessibility and usability.

## Table of Contents
- [Problem Statement](#problem-statement)
- [Tools Used](#tools-used)
- [Project Flow](#project-flow)
  - [1.Download Data and Train Model](#1-download-data-and-train-model)
  - [2.Preprocess and Containerize Model](#2-preprocess-and-containerize-model)
  - [3.Cloud Deployment and Frontend](#3-cloud-deployment-and-frontend)
  - [4.Frontend and Cloud Request](#4-frontend-and-cloud-request)
- [Reproducibility](#reproducibility)
- [Further Improvements](#further-improvements)

## Problem Statement
This project aims to develop a solution that empowers users to gain insights from their image or video data. Whether it's facilitating online meetings or conducting interviews, the model can provide valuable supplementary information about the individuals in the video, offering a deeper understanding of the emotional dynamics in the room. Moreover, it can be employed to analyze which topics or sessions evoke specific reactions from the audience, enabling users to assess and enhance future sessions. This tool acts as a catalyst for user-driven analysis and improvement in various interactive scenarios

## Tools Used

This project used the tool below.

- Infrastructure Setup: Terraform (for provisioning and managing infrastructure)
- Containerization: Docker and Docker-compose (for containerized deployment and management)
- Cloud Storage: Azure Blob Storage (for data storage)
- API Endpoint: Azure Function (for front-end deployment)
- Model registry: Azure Container registry (for model management)
- Reproducibility: Makefile (for ease of project reproducibility)
- Machine Learning: TensorFlow and Keras (for model prediction)

## Project Flow

![Project Flow](/image/other/projectflow.jpeg)

### 1. Download Data and Train Model

Begin by downloading the data from Kaggle and training the model; some of the experiments can be found in this [folder](/code). The project uses OpenCV to process the image and employs TensorFlow + Keras for model training. After the model is trained, we convert it into TensorFlow Lite to enhance performance in production

### 2. Preprocess and Containerize Model

Then use a [script](flow/predict_prod_lite.py) to preprocess the data. This script uses OpenCV for image processing and TensorFlow Lite for model inference. And a [script](cloud/predict/__init__.py) for cloud deployment. The project then gets dockerized as a [Docker container](/docker/model.Dockerfile).

### 3. Cloud Deployment and Frontend

Create essential resources, including an Azure Container Registry and an Azure Function, using [Terraform](infra/main.tf). The Docker image from step 2 then gets pushed to the container registry and creates a webhook to the Azure function for front-end deployment.

### 4. Frontend and Cloud Request

Users can interact with the deployed Azure Function from Step 2 by making requests and providing either image or video data inputs. Alternatively, they have the option to utilize the model locally using the [script](flow/predict_prod_lite.py) currently live web cam data only works with local deployment.

## Reproducibility

`Prerequisite`:
To reproduce this project you would need [Azure Account](https://azure.microsoft.com/en-us) account

You also need the below package

1. [Makefile](https://pypi.org/project/make/) `pip install  make`
2. [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
3. [Terraform](https://developer.hashicorp.com/terraform/downloads)
4. [Docker](https://www.docker.com/)

You will also need [package](requirement/requirements-train.txt) to train the model you can run
```
make prerequisite
```
to install the package required.

Once all package is installed please follow the step in [Reproducre](/other) to re-create the project

See the below video for the steps and use case of the project.

https://www.youtube.com/watch?v=aTsFIArZrRc

## Further Improvements
Improve model accuracy the current model achieves about 70 percent accuracy

Add additional analysis to the function like age and gender prediction.
