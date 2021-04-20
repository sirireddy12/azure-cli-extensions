# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from kubernetes import client as kube_client, config
from azure.cli.core import telemetry
from azure.cli.core.azclierror import FileOperationError
from knack.log import get_logger
import os
import logging
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import azext_k8s_troubleshoot._constants as consts
from azext_k8s_troubleshoot._client_factory import get_subscription_client, _resource_providers_client

logger = get_logger(__name__)


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = consts.DEFAULT_REQUEST_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def setup_logger(logger_name, log_file, level=logging.DEBUG):
    loggr = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)

    loggr.setLevel(level)
    loggr.addHandler(fileHandler)


def set_kube_config(kube_config):
    if kube_config:
        # Trim kubeconfig. This is required for windows os.
        if (kube_config.startswith("'") or kube_config.startswith('"')):
            kube_config = kube_config[1:]
        if (kube_config.endswith("'") or kube_config.endswith('"')):
            kube_config = kube_config[:-1]
        return kube_config
    return None


def load_kube_config(kube_config, kube_context):
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                summary='Problem loading the kubeconfig file')
        raise FileOperationError("Problem loading the kubeconfig file." + str(e))


def get_latest_extension_version(extension_name='connectedk8s'):
    try:
        import re
        git_url = "https://raw.githubusercontent.com/Azure/azure-cli-extensions/master/src/{}/setup.py".format(extension_name)
        response = requests.get(git_url, timeout=10)
        if response.status_code != 200:
            logger.info("Failed to fetch the latest version from '%s' with status code '%s' and reason '%s'",
                        git_url, response.status_code, response.reason)
            return None
        for line in response.iter_lines():
            txt = line.decode('utf-8', errors='ignore')
            if txt.startswith('VERSION'):
                match = re.search(r'VERSION = \'(.*)\'$', txt)
                if match:
                    return match.group(1)
                else:
                    match = re.search(r'VERSION = \"(.*)\"$', txt)
                    if match:
                        return match.group(1)
        return None
    except Exception as ex:  # pylint: disable=broad-except
        logger.info("Failed to get the latest version from '%s'. %s", git_url, str(ex))
        return None


def get_existing_extension_version(extension_name='connectedk8s'):
    from azure.cli.core.extension import get_extensions
    extensions = get_extensions()
    if extensions:
        for ext in extensions:
            if ext.name == extension_name:
                return ext.version or 'Unknown'

    return 'NotFound'


def check_connectivity(url='https://example.org', max_retries=5, timeout=1):
    import timeit
    start = timeit.default_timer()
    success = None
    try:
        with requests.Session() as s:
            s.mount(url, requests.adapters.HTTPAdapter(max_retries=max_retries))
            s.head(url, timeout=timeout)
            success = True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as ex:
        logger.info('Connectivity problem detected.')
        logger.debug(ex)
        success = False
    stop = timeit.default_timer()
    logger.debug('Connectivity check: %s sec', stop - start)
    return success


def get_latest_kubernetes_version():
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[413, 429, 500, 502, 503, 504])
    req_session = requests.Session()
    adapter = TimeoutHTTPAdapter(max_retries=retries)
    req_session.mount("https://", adapter)
    req_session.mount("http://", adapter)

    url = consts.Kubernetes_Github_Latest_Release_Uri

    payload = {}
    headers = {'Accept': 'application/vnd.github.v3+json'}
    try:
        response = req_session.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            latest_release = json.loads(response.text)
            return latest_release["tag_name"]
        else:
            logger.warning("Couldn't fetch the latest kubernetes stable release information. Response status code: {}".format(response.status_code))
    except Exception as e:
        logger.warning("Couldn't fetch the latest kubernetes stable release information. Error: " + str(e))

    return None


def validate_azure_management_reachability(subscription_id, custom_logger):
    try:
        get_subscription_client().get(subscription_id)
    except Exception as ex:
        custom_logger.warning("Not able to reach azure management endpoints. Exception: " + str(ex))


def check_system_permissions(custom_logger):
    try:
        import tempfile
        chart_export_path = os.path.join(os.path.expanduser('~'), '.azure', 'AzureArcCharts')
        os.makedirs(chart_export_path, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=chart_export_path):
            return True
    except (OSError, EnvironmentError):
        return False
    except Exception as ex:
        custom_logger.debug("Couldn't check the system permissions for creating an azure arc charts directory. Error: {}".format(str(ex)), exc_info=True)
        return False


def check_provider_registrations(cli_ctx, custom_logger):
    try:
        rp_client = _resource_providers_client(cli_ctx)
        cc_registration_state = rp_client.get(consts.Connected_Cluster_Provider_Namespace).registration_state
        if cc_registration_state != "Registered":
            custom_logger.error("{} provider is not registered".format(consts.Connected_Cluster_Provider_Namespace))
        kc_registration_state = rp_client.get(consts.Kubernetes_Configuration_Provider_Namespace).registration_state
        if kc_registration_state != "Registered":
            custom_logger.error("{} provider is not registered".format(consts.Kubernetes_Configuration_Provider_Namespace))
    except Exception as ex:
        custom_logger.debug("Couldn't check the required provider's registration status. Error: {}".format(str(ex)), exc_info=True)


# Returns a list of kubernetes pod objects in a given namespace. Object description at: https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1PodList.md
def get_pod_list(api_instance, namespace, label_selector="", field_selector=""):
    try:
        return api_instance.list_namespaced_pod(namespace, label_selector=label_selector, field_selector="")
    except Exception as e:
        logger.debug("Error occurred when retrieving pod information: " + str(e))


def check_linux_amd64_node(configuration, custom_logger=None):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.list_node()
        for item in api_response.items:
            node_arch = item.metadata.labels.get("kubernetes.io/arch")
            node_os = item.metadata.labels.get("kubernetes.io/os")
            if node_arch == "amd64" and node_os == "linux":
                return True
    except Exception as e:  # pylint: disable=broad-except
        if custom_logger:
            custom_logger.error("Error occured while trying to find a linux/amd64 node: " + str(e))
        else:
            logger.debug("Error occured while trying to find a linux/amd64 node: " + str(e))
        # utils.kubernetes_exception_handler(e, consts.Kubernetes_Node_Type_Fetch_Fault, 'Unable to find a linux/amd64 node',
                                        #    raise_error=False)
    return False


def get_config_dp_endpoint(cmd, location):
    cloud_based_domain = cmd.cli_ctx.cloud.endpoints.active_directory.split('.')[2]
    config_dp_endpoint = "https://{}.dp.kubernetesconfiguration.azure.{}".format(location, cloud_based_domain)
    return config_dp_endpoint