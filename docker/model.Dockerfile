FROM mcr.microsoft.com/azure-functions/python:4-python3.9-appservice


ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY requirement/requirements.txt /
RUN pip install -r /requirements.txt

COPY ./cloud /home/site/wwwroot