resource "azurerm_container_registry" "face-analysis-container" {
  name                     = var.container_regis_name
  resource_group_name      = var.resource_group_name
  location                 = var.resource_group_region
  sku                      = "Basic"
  admin_enabled            = true
}

output "registry_name" {
    value = azurerm_container_registry.face-analysis-container.name  
}
output "registry_endpoint" {
    value = azurerm_container_registry.face-analysis-container.data_endpoint_enabled  
}

output "registry_user" {
    value = azurerm_container_registry.face-analysis-container.admin_username  
}
output "registry_pw" {
    value = azurerm_container_registry.face-analysis-container.admin_password  
}

