# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.common.client_factory import get_client_from_cli_profile


def cf_connectedk8s(cli_ctx, *_):
    from azure.mgmt.hybridkubernetes import ConnectedKubernetesClient
    return get_mgmt_service_client(cli_ctx, ConnectedKubernetesClient)


def cf_connected_cluster(cli_ctx, _):
    return cf_connectedk8s(cli_ctx).connected_cluster


def _resource_client_factory(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id)


def _resource_providers_client(cli_ctx):
    from azure.mgmt.resource import ResourceManagementClient
    return get_mgmt_service_client(cli_ctx, ResourceManagementClient).providers

    # Alternate: This should also work
    # subscription_id = get_subscription_id(cli_ctx)
    # return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id).providers


def get_subscription_client():
    from azure.mgmt.resource import SubscriptionClient
    return get_client_from_cli_profile(SubscriptionClient).subscriptions
