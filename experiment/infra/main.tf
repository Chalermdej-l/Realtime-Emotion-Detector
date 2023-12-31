# Configure the Azure provider
provider "azurerm" {
  features {}
}

module "resourcegroup" {
  source = "./modules/resourcegroup"   
  resource_group_name      = var.resource_group_name
  resource_group_region    = var.resource_group_region
}

module "dockerregis" {
  source = "./modules/containerregis"   
  resource_group_name      = module.resourcegroup.resource_group_name
  resource_group_region    = module.resourcegroup.resource_group_region
  container_regis_name     = var.container_regis_name
  image_name               = var.docker_image
 }


module "blob" {
  source = "./modules/blob"   
  resource_group_name      = module.resourcegroup.resource_group_name
  resource_group_region    = module.resourcegroup.resource_group_region
  storage_account_name     = var.storage_account_name 
  blob_name                = var.blob_name 
}

module "function" {
  source = "./modules/function"   
  resource_group_name             = module.resourcegroup.resource_group_name
  resource_group_region           = module.resourcegroup.resource_group_region
  storage_name                    = module.blob.container_name
  storage_key                     = module.blob.function_key  
  storage_con                     = module.blob.connection_string 
  adminuser                       = module.dockerregis.registry_name
  adminpw                         = module.dockerregis.registry_pw 
  container_regis_name            = var.container_regis_name
  container_image_name            = var.docker_image
 }

# --output

output "resource_group_name" {
  value = module.resourcegroup.resource_group_name
}

output "resource_group_region" {
  value = module.resourcegroup.resource_group_region
}

output "registry_name" {
    value = module.dockerregis.registry_name
}
output "registry_endpoint" {
    value = module.dockerregis.registry_endpoint
}

output "container_name" {
  value = module.blob.container_name
}
output "connection_string" {
  value = module.blob.connection_string
  sensitive = true
}
output "function_key" {
  value = module.blob.function_key
  sensitive = true
}
# output "function_endpoint" {
#   value = module.function.functionurl
# }
