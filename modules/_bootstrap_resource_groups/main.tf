resource "aws_resourcegroups_group" "resource_groups" {
  for_each = var.resource_groups
  name     = each.value

  resource_query {
    query = file("${path.module}/queries/${each.value}.json")
  }
}
