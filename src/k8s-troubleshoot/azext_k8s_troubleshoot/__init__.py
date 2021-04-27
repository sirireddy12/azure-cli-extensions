# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_k8s_troubleshoot._help import helps  # pylint: disable=unused-import


class K8s_troubleshootCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_k8s_troubleshoot._client_factory import cf_connectedk8s
        k8s_troubleshoot_custom = CliCommandType(
            operations_tmpl='azext_k8s_troubleshoot.custom#{}',
            client_factory=cf_connectedk8s)
        super(K8s_troubleshootCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=k8s_troubleshoot_custom)

    def load_command_table(self, args):
        from azext_k8s_troubleshoot.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_k8s_troubleshoot._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = K8s_troubleshootCommandsLoader
