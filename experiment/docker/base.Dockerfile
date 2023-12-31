#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------

# Build the runtime from source
ARG HOST_VERSION=4.27.3
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS runtime-image
ARG HOST_VERSION
EXPOSE 80

ENV PublishWithAspNetCoreTargetManifest=false

RUN BUILD_NUMBER=$(echo ${HOST_VERSION} | cut -d'.' -f 3) && \
    git clone --branch v${HOST_VERSION} https://github.com/Azure/azure-functions-host /src/azure-functions-host && \
    cd /src/azure-functions-host && \
    HOST_COMMIT=$(git rev-list -1 HEAD) && \
    dotnet publish -v q /p:BuildNumber=$BUILD_NUMBER /p:CommitHash=$HOST_COMMIT src/WebJobs.Script.WebHost/WebJobs.Script.WebHost.csproj -c Release --output /azure-functions-host --runtime linux-x64 && \
    mv /azure-functions-host/workers /workers && mkdir /azure-functions-host/workers && \
    rm -rf /root/.local /root/.nuget /src

RUN apt-get update && \
    apt-get install -y gnupg wget unzip && \
    EXTENSION_BUNDLE_VERSION_V4=4.9.0 && \
    EXTENSION_BUNDLE_FILENAME_V4=Microsoft.Azure.Functions.ExtensionBundle.${EXTENSION_BUNDLE_VERSION_V4}_linux-x64.zip && \
    wget https://functionscdn.azureedge.net/public/ExtensionBundles/Microsoft.Azure.Functions.ExtensionBundle/$EXTENSION_BUNDLE_VERSION_V4/$EXTENSION_BUNDLE_FILENAME_V4 && \
    mkdir -p /FuncExtensionBundles/Microsoft.Azure.Functions.ExtensionBundle/$EXTENSION_BUNDLE_VERSION_V4 && \
    unzip /$EXTENSION_BUNDLE_FILENAME_V4 -d /FuncExtensionBundles/Microsoft.Azure.Functions.ExtensionBundle/$EXTENSION_BUNDLE_VERSION_V4 && \
    rm -f /$EXTENSION_BUNDLE_FILENAME_V4 &&\
    find /FuncExtensionBundles/ -type f -exec chmod 644 {} \;

FROM mcr.microsoft.com/mirror/docker/library/python:3.9-slim-bullseye as python

FROM mcr.microsoft.com/dotnet/runtime-deps:6.0
ARG HOST_VERSION

COPY --from=runtime-image ["/azure-functions-host", "/azure-functions-host"]
COPY --from=runtime-image [ "/FuncExtensionBundles/Microsoft.Azure.Functions.ExtensionBundle/4.9.0", "/FuncExtensionBundles/Microsoft.Azure.Functions.ExtensionBundle/4.9.0" ]
COPY --from=runtime-image [ "/workers/python/3.9/LINUX", "/azure-functions-host/workers/python/3.9/LINUX" ]
COPY --from=runtime-image [ "/workers/python/worker.config.json", "/azure-functions-host/workers/python" ]
COPY --from=python [ "/usr", "/usr" ]
COPY --from=python [ "/lib", "/lib" ]
COPY --from=python [ "/lib64", "/lib64" ]

ENV LANG=C.UTF-8 \
    ACCEPT_EULA=Y \
    AzureWebJobsScriptRoot=/home/site/wwwroot \
    HOME=/home \
    FUNCTIONS_WORKER_RUNTIME=python \
    ASPNETCORE_URLS=http://+:80 \
    DOTNET_RUNNING_IN_CONTAINER=true \
    DOTNET_USE_POLLING_FILE_WATCHER=true \
    HOST_VERSION=${HOST_VERSION} \
    ASPNETCORE_CONTENTROOT=/azure-functions-host

ENV FUNCTIONS_WORKER_RUNTIME_VERSION=3.9

CMD [ "/azure-functions-host/Microsoft.Azure.WebJobs.Script.WebHost" ]