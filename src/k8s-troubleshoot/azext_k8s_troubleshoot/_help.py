# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['k8s-troubleshoot'] = """
    type: group
    short-summary: Commands to troubleshoot azure-arc connected kubernetes cluster.
"""


helps['k8s-troubleshoot diagnose'] = """
  type: command
  short-summary: Collects diagnose infomation and gets logs on the connected cluster.
  parameters:
        - name: --storage-account
          type: string
          short-summary: Name or ID of the storage account to save the diagnostic information.
        - name: --sas-token
          type: string
          short-summary: The SAS token with writable permission for the storage account.
  examples:
      - name: using storage account name and a shared access signature token with write permission
        text: az k8s-troubleshoot diagnose -g MyResourceGroup -n ConnectedCluster --storage-account MyStorageAccount --sas-token "MySasToken"
      - name: using the resource id of a storage account resource you own.
        text: az k8s-troubleshoot diagnose -g MyResourceGroup -n ConnectedCluster --storage-account "MyStoreageAccountResourceId"
      - name: using the storage account in diagnostics settings for your connected cluster.
        text: az k8s-troubleshoot diagnose -g MyResourceGroup -n ConnectedCluster
"""