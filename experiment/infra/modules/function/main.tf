resource "azurerm_service_plan" "appservice_analysis" {
  name                = "analysisAppServicePlan"
  location            = var.resource_group_region
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  sku_name            = "B1"

}

resource "azurerm_linux_function_app" "function_app" {
  name                       = "analysis-prediction"
  location                   = var.resource_group_region
  resource_group_name        = var.resource_group_name

  storage_account_name        = var.storage_name
  storage_account_access_key  = var.storage_key
  service_plan_id             = azurerm_service_plan.appservice_analysis.id
  app_settings = {
    DOCKER_REGISTRY_SERVER_PASSWORD     = var.adminpw
    DOCKER_REGISTRY_SERVER_USERNAME     = var.adminuser
    DOCKER_REGISTRY_SERVER_URL          = "https://${var.container_regis_name}.azurecr.io"
    AzureWebJobsStorage                 = var.storage_con
    # AzureWebJobsFeatureFlags            = "EnableWorkerIndexing"
    # SCM_DO_BUILD_DURING_DEPLOYMENT      = true
  }
  site_config {
    application_stack {
        docker {
            registry_url = "${var.container_regis_name}.azurecr.io"
            image_name = var.container_image_name
            image_tag = "latest"
        }    
    }
    always_on = true
  }
}

# output "functionurl" {
#     value = azurerm_linux_function_app.function_app.outbound_ip_addresses
# }