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

docker-run
	docker run -d -i --rm -p 8080:8080 modelprod

docker-build
	docker build -f Dockerfile -t testdeploywow.azurecr.io/modelprod .

docker-tag
	docker tag testdeploywow.azurecr.io/modelprod

az-login
	az login
	az acr login --name testdeploywow

docker-push
	docker push testdeploywow.azurecr.io/modelprod