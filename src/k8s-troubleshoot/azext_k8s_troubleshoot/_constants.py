# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=line-too-long

Connected_Cluster_Provider_Namespace = 'Microsoft.Kubernetes'
Kubernetes_Configuration_Provider_Namespace = 'Microsoft.KubernetesConfiguration'
Custom_Locations_Provider_Namespace = 'Microsoft.ExtendedLocation'
Arc_Namespace = 'azure-arc'
DEFAULT_REQUEST_TIMEOUT = 10  # seconds
AZURE_IDENTITY_CERTIFICATE_SECRET = 'azure-identity-certificate'
ISO_861_Time_format = "%Y-%m-%dT%H:%M:%SZ"

# Custom fault types

Load_Kubeconfig_Fault_Type = "Error while loading kubeconfig"

# URL constants
Kubernetes_Github_Latest_Release_Uri = "https://api.github.com/repos/kubernetes/kubernetes/releases/latest"