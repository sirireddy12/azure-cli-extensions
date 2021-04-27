# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from knack.util import CLIError
from knack.log import get_logger
import logging
from packaging import version
from kubernetes import client as kube_client, config
import azext_k8s_troubleshoot._utils as utils
import colorama  # pylint: disable=import-error


logger = get_logger(__name__)


def diagnose_k8s_troubleshoot(cmd, client, resource_group_name, cluster_name, kube_config=None, kube_context=None, location=None, storage_account=None,
                              sas_token=None, output_file=os.path.join(os.path.expanduser('~'), '.azure', 'az_k8s_troubleshoot_output.tar.gz')):
    colorama.init()                          
    troubleshoot_log_path = os.path.join(os.path.expanduser('~'), '.azure', 'connected8s_troubleshoot.log')
    utils.setup_logger('connectedk8s_troubleshoot', troubleshoot_log_path)
    tr_logger = logging.getLogger('connectedk8s_troubleshoot')

    kube_config = utils.set_kube_config(kube_config)

    # Loading the kubeconfig file in kubernetes client configuration
    utils.load_kube_config(kube_config, kube_context, custom_logger=tr_logger)
    configuration = kube_client.Configuration()
    try:
        latest_connectedk8s_version = utils.get_latest_extension_version()
        local_connectedk8s_version = utils.get_existing_extension_version()
        tr_logger.info("Latest available connectedk8s version: {}".format(latest_connectedk8s_version))
        tr_logger.info("Local connectedk8s version: {}".format(local_connectedk8s_version))
        if latest_connectedk8s_version and local_connectedk8s_version != 'Unknown' and local_connectedk8s_version != 'NotFound':
            if version.parse(local_connectedk8s_version) < version.parse(latest_connectedk8s_version):
                logger.warning("You have an update pending. You can update the connectedk8s extension to latest v{} using 'az extension update -n connectedk8s'".format(latest_connectedk8s_version))

        crb_permission = utils.can_create_clusterrolebindings(configuration, custom_logger=tr_logger)
        if not crb_permission:
            tr_logger.error("CLI logged in cred doesn't have permission to create clusterrolebindings on this kubernetes cluster.")

        permitted = utils.check_system_permissions(tr_logger)
        if not permitted:
            tr_logger.error("CLI doesn't have the permission/privilege to install azure arc charts at path {}".format(os.path.join(os.path.expanduser('~'), '.azure', 'AzureArcCharts')))
        required_node_exists = utils.check_linux_amd64_node(configuration, custom_logger=tr_logger)
        if not required_node_exists:
            tr_logger.warning("Couldn't find any linux/amd64 node on the Kubernetes cluster")
        config_dp_endpoint = utils.get_config_dp_endpoint(cmd, location)
        helm_registry_path = utils.get_helm_registry(cmd, config_dp_endpoint, custom_logger=tr_logger)
        tr_logger.info("Helm Registry path : {}".format(helm_registry_path))
        utils.check_provider_registrations(cmd.cli_ctx, tr_logger)
        os.environ['HELM_EXPERIMENTAL_OCI'] = '1'
        utils.pull_helm_chart(helm_registry_path, kube_config, kube_context, custom_logger=tr_logger)

        try:
            # Fetch ConnectedCluster
            connected_cluster = client.get(resource_group_name, cluster_name, raw=True)
            tr_logger.info("Connected cluster resource: {}".format(connected_cluster.response.content))
        except Exception as ex:
            try:
                if ex.error.error.code == "NotFound" or ex.error.error.code == "ResourceNotFound":
                    tr_logger.error("Connected cluster resource doesn't exist. " + str(ex))
            except AttributeError:
                pass
            tr_logger.error("Couldn't check the existence of Connected cluster resource. Error: {}".format(str(ex)))

        kapi_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
        try:
            pod_list = kapi_instance.list_namespaced_pod('azure-arc')
            pods_count = 0
            for pod in pod_list.items:
                pods_count += 1
                if pod.status.phase != 'Running':
                    tr_logger.warning("Pod {} is in {} state. Reason: {}. Container statuses: {}".format(pod.metadata.name, pod.status.phase, pod.status.reason, pod.status.container_statuses))

            if pods_count == 0:
                tr_logger.warning("No pods found in azure-arc namespace.")

        except Exception as ex:
            tr_logger.error("Error occured while fetching pod's statues : {}".format(str(ex)))

        try:
            # Creating the .tar.gz for logs and deleting the actual log file
            import tarfile
            with tarfile.open(output_file, "w:gz") as tar:
                tar.add(troubleshoot_log_path, 'connected8s_troubleshoot.log')
            logging.shutdown()  # To release log file handler, so that the actual log file can be removed after archiving
            os.remove(troubleshoot_log_path)
        except Exception as ex:
            tr_logger.error("Error occured while archiving the log file: {}".format(str(ex)), exc_info=True)

        print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}The diagnostic logs have been collected and archived at '{output_file}'.")

    except Exception as ex:
        tr_logger.error("Exception caught while running troubleshoot: {}".format(str(ex)), exc_info=True)
        logger.error("Exception caught while running troubleshoot: {}".format(str(ex)), exc_info=True)
