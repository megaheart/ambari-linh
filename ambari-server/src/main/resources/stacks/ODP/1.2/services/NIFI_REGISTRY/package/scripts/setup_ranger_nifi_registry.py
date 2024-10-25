#!/usr/bin/env python3
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
from resource_management.core.logger import Logger
from resource_management.core.resources import File
from resource_management.libraries.functions.format import format


def setup_ranger_nifi_registry(upgrade_type=None):
    import params, os

    if params.has_ranger_admin and params.ranger_nifi_registry_plugin_is_available and params.enable_ranger_nifi_registry:
        stack_version = params.stack_version_buildnum
        ranger_cred_file = os.path.realpath(os.path.join(os.path.dirname(params.script_dir),'scripts','ranger_credential_helper.py'))
        File(ranger_cred_file,
             owner=params.nifi_registry_user,
             group=params.nifi_registry_group,
             mode=0o750
             )

        cred_lib_prefix_path = format('{stack_root}/{stack_version}/{service_name}/ext/ranger/lib/*:{stack_root}/{stack_version}/{service_name}/lib/slf4j-api-1.7.12.jar')
        cred_setup_prefix_path = (ranger_cred_file, '-l', cred_lib_prefix_path)

        if params.retryAble:
            Logger.info("nifi-registry: Setup ranger: command retry enables thus retrying if ranger admin is down !")
        else:
            Logger.info("nifi-registry: Setup ranger: command retry not enabled thus skipping if ranger admin is down !")

        # create ranger nifi-registry audit directory
        if params.xa_audit_hdfs_is_enabled and params.has_namenode and params.has_hdfs_client_on_node and upgrade_type is None:
            params.HdfsResource("/ranger/audit",
                                type="directory",
                                action="create_on_execute",
                                owner=params.hdfs_user,
                                group=params.hdfs_user,
                                mode=0o755,
                                recursive_chmod=True
                                )
            params.HdfsResource("/ranger/audit/nifi-registry",
                                type="directory",
                                action="create_on_execute",
                                owner=params.nifi_registry_user,
                                group=params.nifi_registry_group,
                                mode=0o750,
                                recursive_chmod=True
                                )
            params.HdfsResource(None, action="execute")

        api_version = None
        if params.stack_supports_ranger_kerberos:
            api_version = 'v2'
        from resource_management.libraries.functions.setup_ranger_plugin_xml import setup_ranger_plugin
        setup_ranger_plugin('nifi-registry', params.service_name, params.previous_jdbc_jar,
                            params.downloaded_custom_connector, params.driver_curl_source,
                            params.driver_curl_target, params.java_home,
                            params.repo_name, params.nifi_registry_ranger_plugin_repo,
                            params.ranger_env, params.ranger_plugin_properties,
                            params.policy_user, params.policymgr_mgr_url,
                            params.enable_ranger_nifi_registry, conf_dict=params.nifi_registry_config_dir,
                            component_user=params.nifi_registry_user, component_group=params.nifi_registry_group,
                            cache_service_list=['nifi-registry'],
                            plugin_audit_properties=params.config['configurations']['ranger-nifi-registry-audit'],
                            plugin_audit_attributes=params.config['configurationAttributes']['ranger-nifi-registry-audit'],
                            plugin_security_properties=params.config['configurations']['ranger-nifi-registry-security'],
                            plugin_security_attributes=params.config['configurationAttributes']['ranger-nifi-registry-security'],
                            plugin_policymgr_ssl_properties=params.config['configurations']['ranger-nifi-registry-policymgr-ssl'],
                            plugin_policymgr_ssl_attributes=params.config['configurationAttributes']['ranger-nifi-registry-policymgr-ssl'],
                            component_list=[], audit_db_is_enabled=params.xa_audit_db_is_enabled,
                            credential_file=params.credential_file, xa_audit_db_password=params.xa_audit_db_password,
                            ssl_truststore_password=params.ssl_truststore_password,
                            ssl_keystore_password=params.ssl_keystore_password, policy_config_dict = params.ranger_policy_config if params.ranger_policy_config else None,
                            stack_version_override=stack_version, skip_if_rangeradmin_down=not params.retryAble,
                            api_version=api_version,
                            is_security_enabled=params.security_enabled,
                            is_stack_supports_ranger_kerberos=params.stack_supports_ranger_kerberos,
                            component_user_principal=params.ranger_nifi_registry_principal if params.security_enabled else None,
                            component_user_keytab=params.ranger_nifi_registry_keytab if params.security_enabled else None,
                            cred_lib_path_override=cred_lib_prefix_path,
                            cred_setup_prefix_override=cred_setup_prefix_path)
                            
        File(os.path.join(params.nifi_registry_config_dir, 'ranger-nifi-registry-audit.xml'), owner=params.nifi_registry_user, group=params.nifi_registry_group, mode=0o400)
        File(os.path.join(params.nifi_registry_config_dir, 'ranger-nifi-registry-security.xml'), owner=params.nifi_registry_user, group=params.nifi_registry_group, mode=0o400)
        File(os.path.join(params.nifi_registry_config_dir, 'ranger-policymgr-ssl.xml'), owner=params.nifi_registry_user, group=params.nifi_registry_group, mode=0o400)

    else:
        Logger.info('Skipping Ranger integration for NiFi Registry setup.')