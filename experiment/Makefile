include .env

predict-img:
	python flow/predict_local.py -t 'image' -m${model_path} -d${detector_path} -i ${input_path_img} -o ${output_path_img}

predict-vid:
	python flow/predict_local.py -t 'video' -m ${model_path} -d ${detector_path} -i ${input_path_vid}'' -o ${output_path_vid}

predict-live:
	python flow/predict_local.py -t 'live' -m ${model_path} -d ${detector_path} -i '' -o ${output_path_vid}

predict-img-lite:
	python flow/predict_prod_lite.py -t 'image' -m${model_path_lite} -d${detector_path} -i ${input_path_img} -o ${output_path_img}

predict-vid-lite:
	python flow/predict_prod_lite.py -t 'video' -m ${model_path_lite} -d ${detector_path} -i ${input_path_vid}'' -o ${output_path_vid}

docker-run:
	docker run -d -i --rm -p 8080:8080 ${IMAGE_NAME}

docker-build:
	docker build -f ./docker/base.Dockerfile -t baseimage .
	docker build -f ./docker/model.Dockerfile -t ${CONTAINER_NAME}.azurecr.io/${IMAGE_NAME} .

docker-tag:
	docker tag ${CONTAINER_NAME}.azurecr.io/${IMAGE_NAME}

az-login:
	az login	

docker-push:
	docker push ${CONTAINER_NAME}.azurecr.io/${IMAGE_NAME}

docker-prune:
	docker system prune --force

dockerdeploy:
	az acr login --name ${CONTAINER_NAME}
	docker push ${CONTAINER_NAME}.azurecr.io/${CONTAINER_IMAGE}${IMAGE_NAME}

# Terraform
infra-setup:
	terraform -chdir=./infra init 
	terraform -chdir=./infra plan -var-file=variables.tfvars

infra-down-p:
	terraform -chdir=./infra plan -destroy -var-file=variables.tfvars

infra-down-c:
	terraform -chdir=./infra destroy -var-file=variables.tfvars -auto-approve

infra-create:
	terraform -chdir=./infra apply -var-file=variables.tfvars -auto-approve

infra-output:
	# EVENT_HUB_CONNECTION_PRODUCER_SEND_KEY
	terraform -chdir=./infra output  -raw eventhub_producer_send_auth_rule
    
	echo
	#------------------
	# EVENT_HUB_CONNECTION_PRODUCER_LISTEN_KEY
	terraform -chdir=./infra output  -raw eventhub_producer_listen_auth_rule

	echo
	#------------------
	# EVENT_HUB_CONNECTION_CONSUMER_LISTEN_KEY
	terraform -chdir=./infra output  -raw eventhub_consumer_listen_auth_rule

	echo
	#------------------
	# EVENT_HUB_CONNECTION_CONSUMER_SEND_KEY
	terraform -chdir=./infra output  -raw eventhub_consumer_send_auth_rule

	echo
	#------------------
	# BLOB_STORAGE_CONNECTION_PRODUCER
	terraform -chdir=./infra output  -raw consumer_connection_string

	echo
	#------------------
	# BLOB_STORAGE_CONNECTION_CONSUMER
	terraform -chdir=./infra output  -raw predict_connection_string
	
	echo
	#------------------

infra-config:
	az login

prerequisite:
	pip install -r  requirement.txt