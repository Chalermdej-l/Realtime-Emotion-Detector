provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}
resource "azurerm_resource_group" "face-analysis" {
  name     = var.resource_group_name
  location = var.resource_group_region
  
}

output "resource_group_name" {
  value = azurerm_resource_group.face-analysis.name
}
output "resource_group_region" {
  value = azurerm_resource_group.face-analysis.location
}