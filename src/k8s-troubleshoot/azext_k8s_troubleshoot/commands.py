# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_k8s_troubleshoot._client_factory import cf_connectedk8s, cf_connected_cluster


def load_command_table(self, _):
    with self.command_group('k8s-troubleshoot', client_factory=cf_connected_cluster) as g:
        g.custom_command('diagnose', 'diagnose_k8s_troubleshoot')

