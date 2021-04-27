# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import os.path
from azure.cli.core.commands.parameters import get_location_type, file_type
from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):

    with self.argument_context('k8s-troubleshoot diagnose') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('cluster_name', options_list=['--name', '-n'], help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
        c.argument('storage_account', options_list=['--storage-account'], help='Name or ID of the storage account to save the diagnostic information')
        c.argument('sas_token', options_list=['--sas-token'], help='The SAS token with writable permission for the storage account.')
        c.argument('output_file', options_list=['--output-file'], type=file_type, default=os.path.join(os.path.expanduser('~'), '.azure', 'az_k8s_troubleshoot_output.tar.gz'), help="Output zipped file path for the logs collected during troubleshoot.")
