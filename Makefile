include .env

predict-img:
	python flow/predict_local.py -t 'image' -m${model_path} -d${detector_path} -i ${input_path_img} -o ${output_path_img}

predict-vid:
	python flow/predict_local.py -t 'video' -m ${model_path} -d ${detector_path} -i ${input_path_vid} -o ${output_path_vid}

predict-live:
	python flow/predict_local.py -t 'live' -m ${model_path} -d ${detector_path} -i '' -o ${output_path_vid}

predict-img-lite:
	python flow/predict_prod_lite.py -t 'image' -m_m ${model_path_lite_mood} -m_a ${model_path_lite_age} -d${detector_path} -i ${input_path_img} -o ${output_path_img}

predict-vid-lite:
	python flow/predict_prod_lite.py -t 'video' -m_m ${model_path_lite_mood} -m_a ${model_path_lite_age} -d ${detector_path} -i ${input_path_vid} -o ${output_path_vid}

predict-live-lite:
	python flow/predict_prod_lite.py -t 'live' -m_m ${model_path_lite_mood} -m_a ${model_path_lite_age} -d ${detector_path} -i '' -o ${output_path_vid}

predict-img-prod:
	python flow/predict_prod_func.py -i ${input_path_img} -o ${output_path_img} -m 'img' -u ${URL}

predict-vid-prod:
	python flow/predict_prod_func.py -i ${input_path_vid} -o ${output_path_vid} -m 'vid' -u ${URL}

docker-run:
	docker run -d -i --rm -p 8080:8080 ${IMAGE_NAME}

docker-build:
	# docker build -f ./docker/base.Dockerfile -t baseimage .
	docker build -f ./docker/model.Dockerfile -t ${CONTAINER_NAME}.azurecr.io/${IMAGE_NAME} .

docker-tag:
	docker tag ${CONTAINER_NAME}.azurecr.io/${IMAGE_NAME}

az-login:
	az login -o None

docker-push:
	docker push ${CONTAINER_NAME}.azurecr.io/${IMAGE_NAME}

docker-prune:
	docker system prune --force

docker-deploy:
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

infra-create-regis:
	terraform -chdir=./infra apply -target=module.resourcegroup -target=module.dockerregis -var-file=variables.tfvars -auto-approve

infra-create-func:
	terraform -chdir=./infra apply -target=module.blob -target=module.function -var-file=variables.tfvars -auto-approve

infra-config:
	az login

infra-output:
	terraform -chdir=./infra output  -raw function_endpoint

prerequisite:
	pip install -r  requirement/requirements-train.txt

