# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.commands.client_factory import get_mgmt_service_client


def _resource_client_factory(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id)


def _resource_providers_client(cli_ctx):
    from azure.mgmt.resource import ResourceManagementClient
    return get_mgmt_service_client(cli_ctx, ResourceManagementClient).providers

    # Alternate: This should also work
    # subscription_id = get_subscription_id(cli_ctx)
    # return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id).providers
