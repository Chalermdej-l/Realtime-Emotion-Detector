resource "azurerm_storage_account" "analysis_storage_account" {
  name                     = var.storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.resource_group_region
  account_tier             = "Standard"
  account_replication_type = "LRS"

  identity {
    type = "SystemAssigned"
  }

  network_rules {
    default_action             = "Allow"
    virtual_network_subnet_ids = []
  }

  lifecycle {
    prevent_destroy = false
  }
}

resource "azurerm_storage_container" "analysis_storage" {
  name                  = var.blob_name 
  storage_account_name  = azurerm_storage_account.analysis_storage_account.name
  container_access_type = "private"
}

output "container_name" {
    value = azurerm_storage_container.analysis_storage.name
}

output "connection_string" {
    value = azurerm_storage_account.analysis_storage_account.primary_connection_string
}

output "function_key" {
    value = azurerm_storage_account.analysis_storage_account.primary_access_key
}