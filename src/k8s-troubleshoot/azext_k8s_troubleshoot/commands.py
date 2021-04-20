# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_k8s_troubleshoot._client_factory import cf_k8s_troubleshoot


def load_command_table(self, _):

    # TODO: Add command type here
    # k8s-troubleshoot_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_k8s-troubleshoot)


    with self.command_group('k8s-troubleshoot') as g:
        g.custom_command('diagnose', 'diagnose_k8s_troubleshoot')
        # g.command('delete', 'delete')
        # g.custom_command('list', 'list_k8s_troubleshoot')
        # g.show_command('show', 'get')
        # g.generic_update_command('update', setter_name='update', custom_func_name='update_k8s-troubleshoot')


    with self.command_group('k8s-troubleshoot', is_preview=True):
        pass

