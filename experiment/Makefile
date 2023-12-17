include .env

predict-img:
	python flow/predict_local.py -t 'image' -m${model_path} -d${detector_path} -i ${input_path_img} -o ${output_path_img}

predict-vid:
	python flow/predict_local.py -t 'video' -m ${model_path} -d ${detector_path} -i ${input_path_vid}'' -o ${output_path_vid}

predict-live:
	python flow/predict_local.py -t 'live' -m ${model_path} -d ${detector_path} -i '' -o ${output_path_vid}
