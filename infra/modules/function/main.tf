resource "azurerm_service_plan" "appservice_analysis" {
  name                = "analysisAppServicePlan"
  location            = var.resource_group_region
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  sku_name            = "B3"

}
resource "azurerm_application_insights" "app_insights" {
  name                = "analysis-app-insights"
  resource_group_name = var.resource_group_name
  location            = var.resource_group_region
  application_type    = "web"
}

resource "azurerm_monitor_action_group" "monitor_group" {
  name                = "analysis-monitor"
  resource_group_name = var.resource_group_name
  short_name          = "aysano" 
  
}
resource "azurerm_application_insights_smart_detection_rule" "detector_rule" {
  name                    = "Slow server response time"
  application_insights_id = azurerm_application_insights.app_insights.id
  enabled                 = false
}

resource "azurerm_monitor_smart_detector_alert_rule" "failure_anomalies" {
  name                = "Failure Anomalies - analysis"
  resource_group_name = var.resource_group_name
  detector_type       = "FailureAnomaliesDetector"
  scope_resource_ids  = [azurerm_application_insights.app_insights.id]
  severity            = "Sev0"
  frequency           = "PT1M"
  depends_on = [ azurerm_application_insights_smart_detection_rule.detector_rule ]
  action_group {
    ids = [azurerm_monitor_action_group.monitor_group.id]
  }
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
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = false

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
    application_insights_connection_string = azurerm_application_insights.app_insights.connection_string
    app_service_logs {
      disk_quota_mb = 35
      retention_period_days = 7
    }
  }
}

data "azurerm_function_app_host_keys" "hostkey" {
  name                = azurerm_linux_function_app.function_app.name
  resource_group_name = azurerm_linux_function_app.function_app.resource_group_name

  depends_on = [azurerm_linux_function_app.function_app]
}

# output "functionurl" {
#     value = azurerm_linux_function_app.function_app.default_hostname
# }
# output "functionkey" {
#     value = azurerm_linux_function_app.function_app.
# }

output "url" {
    value = "https://${azurerm_linux_function_app.function_app.default_hostname}/api/predict?code=${data.azurerm_function_app_host_keys.hostkey.default_function_key}"
    sensitive = true
}