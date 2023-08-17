import api from './apiConfig';

export const getOrganisation = (userId) => {
  return api.get(`/organisations/get/user/${userId}`);
};

export const getGithubClientId = () => {
  return api.get(`/get/github_client_id`);
};

export const addUser = (userData) => {
  return api.post(`/users/add`, userData);
};

export const getProject = (organisationId) => {
  return api.get(`/projects/get/organisation/${organisationId}`);
};

export const getAgents = (projectId) => {
  return api.get(`/agents/get/project/${projectId}`);
};

export const getToolKit = () => {
  return api.get(`/toolkits/get/local/list`);
};

export const getTools = () => {
  return api.get(`/tools/list`);
};

export const getAgentDetails = (agentId, agentExecutionId) => {
  return api.get(`/agent_executions_configs/details/agent_id/${agentId}/agent_execution_id/${agentExecutionId}`);
};

export const getAgentExecutions = (agentId) => {
  return api.get(`/agentexecutions/get/agent/${agentId}`);
};

export const getExecutionFeeds = (executionId) => {
  return api.get(`/agentexecutionfeeds/get/execution/${executionId}`);
};

export const getExecutionTasks = (executionId) => {
  return api.get(`/agentexecutionfeeds/get/tasks/${executionId}`);
};

export const createAgent = (agentData, scheduledCreate) => {
  return api.post(scheduledCreate ? `/agents/schedule` : `/agents/create`, agentData);
};

export const addAgentRun = (agentData) => {
  return api.post( `/agentexecutions/add_run`, agentData);
};

export const addTool = (toolData) => {
  return api.post(`/toolkits/get/local/install`, toolData);
};

export const updateExecution = (executionId, executionData) => {
  return api.put(`/agentexecutions/update/${executionId}`, executionData);
};

export const editAgentTemplate = (agentTemplateId, agentTemplateData) => {
  return api.put(`/agent_templates/update_agent_template/${agentTemplateId}`, agentTemplateData)
};

export const addExecution = (executionData) => {
  return api.post(`/agentexecutions/add`, executionData);
};

export const getResources = (agentId) => {
  return api.get(`/resources/get/all/${agentId}`);
};

export const getLastActiveAgent = (projectId) => {
  return api.get(`/agentexecutions/get/latest/agent/project/${projectId}`);
};

export const uploadFile = (agentId, formData) => {
  return api.post(`/resources/add/${agentId}`, formData);
};

export const validateAccessToken = () => {
  return api.get(`/validate-access-token`);
};

export const validateLLMApiKey = (model_source, model_api_key) => {
  return api.post(`/validate-llm-api-key`, {model_source, model_api_key});
};

export const checkEnvironment = () => {
  return api.get(`/configs/get/env`);
};

export const getOrganisationConfig = (organisationId, key) => {
  return api.get(`/configs/get/organisation/${organisationId}/key/${key}`);
};

export const updateOrganisationConfig = (organisationId, configData) => {
  return api.post(`/configs/add/organisation/${organisationId}`, configData);
};

export const fetchAgentTemplateList = () => {
  return api.get('/agent_templates/list?template_source=marketplace');
};

export const fetchAgentTemplateDetails = (templateId) => {
  return api.get(`/agent_templates/get/${templateId}`);
};

export const getToolConfig = (toolKitName) => {
  return api.get(`/tool_configs/get/toolkit/${toolKitName}`);
};

export const updateToolConfig = (toolKitName, configData) => {
  return api.post(`/tool_configs/add/${toolKitName}`, configData);
};

export const fetchAgentTemplateListLocal = () => {
  return api.get('/agent_templates/list?template_source=local');
};

export const saveAgentAsTemplate = (executionId) => {
  return api.post(`/agent_templates/save_agent_as_template/agent_execution_id/${executionId}`);
};

export const fetchAgentTemplateConfig = (templateId) => {
  return api.get(`/agent_templates/get/${templateId}?template_source=marketplace`);
};

export const installAgentTemplate = (templateId) => {
  return api.post(`/agent_templates/download?agent_template_id=${templateId}`);
};

export const fetchAgentTemplateConfigLocal = (templateId) => {
  return api.get(`/agent_templates/agent_config?agent_template_id=${templateId}`);
};

export const updatePermissions = (permissionId, data) => {
  return api.put(`/agentexecutionpermissions/update/status/${permissionId}`, data)
};

export const deleteAgent = (agentId) => {
  return api.put(`/agents/delete/${agentId}`)
};

export const authenticateGoogleCred = (toolKitId) => {
  return api.get(`/google/get_google_creds/toolkit_id/${toolKitId}`);
};

export const authenticateTwitterCred = (toolKitId) => {
  return api.get(`/twitter/get_twitter_creds/toolkit_id/${toolKitId}`);
};

export const sendTwitterCreds = (twitter_creds) => {
  return api.post(`/twitter/send_twitter_creds/${twitter_creds}`);
};

export const sendGoogleCreds = (google_creds, toolkit_id) => {
  return api.post(`/google/send_google_creds/toolkit_id/${toolkit_id}`, google_creds);
};

export const fetchToolTemplateList = () => {
  return api.get(`/toolkits/get/list?page=0`);
};

export const fetchKnowledgeTemplateList = () => {
  return api.get(`/knowledges/get/list?page=0`);
};

export const fetchToolTemplateOverview = (toolTemplateName) => {
  return api.get(`/toolkits/marketplace/readme/${toolTemplateName}`);
};

export const updateMarketplaceToolTemplate = (templateName) => {
  return api.put(`/toolkits/update/${templateName}`);
};

export const installToolkitTemplate = (templateName) => {
  return api.get(`/toolkits/get/install/${templateName}`);
};

export const checkToolkitUpdate = (templateName) => {
  return api.get(`/toolkits/check_update/${templateName}`);
};

export const getExecutionDetails = (executionId, agentId) => {
  return api.get(`/agent_executions_configs/details/agent/${agentId}/agent_execution/${executionId}`);
};

export const stopSchedule = (agentId) => {
  return api.post(`/agents/stop/schedule?agent_id=${agentId}`);
};

export const createAndScheduleRun = (requestData) => {
  return api.post(`/agentexecutions/schedule`, requestData);
};

export const agentScheduleComponent = (agentId) => {
  return api.get(`/agents/get/schedule_data/${agentId}`);
};

export const updateSchedule = (requestData) => {
  return api.put(`/agents/edit/schedule`, requestData);
};

export const getDateTime = (agentId) => {
  return api.get(`/agents/get/schedule_data/${agentId}`);
};

export const getMetrics = () => {
  return api.get(`/analytics/metrics`)
};

export const getAllAgents = () => {
  return api.get(`/analytics/agents/all`)
};

export const getAgentRuns = (agent_id) => {
  return api.get(`analytics/agents/${agent_id}`);
};

export const getActiveRuns = () => {
  return api.get(`analytics/runs/active`);
};

export const getToolsUsage = () => {
  return api.get(`analytics/tools/used`);
};

export const getLlmModels = () => {
  return api.get(`organisations/llm_models`);
};

export const getAgentWorkflows = () => {
  return api.get(`organisations/agent_workflows`);
};

export const fetchVectorDBList = () => {
  return api.get(`/vector_dbs/get/list`);
};

export const getVectorDatabases = () => {
  return api.get(`/vector_dbs/user/list`);
};

export const getVectorDBDetails = (vectorDBId) => {
  return api.get(`/vector_dbs/db/details/${vectorDBId}`);
};

export const deleteVectorDB = (vectorDBId) => {
  return api.post(`/vector_dbs/delete/${vectorDBId}`);
};

export const updateVectorDB = (vectorDBId, newIndices) => {
  return api.put(`/vector_dbs/update/vector_db/${vectorDBId}`, newIndices);
};

export const connectPinecone = (pineconeData) => {
  return api.post(`/vector_dbs/connect/pinecone`, pineconeData);
};

export const connectQdrant = (qdrantData) => {
  return api.post(`/vector_dbs/connect/qdrant`, qdrantData);
};

export const connectWeaviate = (weaviateData) => {
  return api.post(`/vector_dbs/connect/weaviate`, weaviateData);
};

export const getKnowledge = () => {
  return api.get(`/knowledges/user/list`);
};

export const getKnowledgeDetails = (knowledgeId) => {
  return api.get(`/knowledges/user/get/details/${knowledgeId}`);
};

export const deleteCustomKnowledge = (knowledgeId) => {
  return api.post(`/knowledges/delete/${knowledgeId}`);
};

export const deleteMarketplaceKnowledge = (knowledgeName) => {
  return api.post(`/knowledges/uninstall/${knowledgeName}`);
};

export const addUpdateKnowledge = (knowledgeData) => {
  return api.post(`/knowledges/add_or_update/data`, knowledgeData);
};

export const getValidIndices = () => {
  return api.get(`/vector_db_indices/user/valid_indices`);
};

export const getValidMarketplaceIndices = (knowledgeName) => {
  return api.get(`/vector_db_indices/marketplace/valid_indices/${knowledgeName}`);
};

export const fetchKnowledgeTemplateOverview = (knowledgeName) => {
  return api.get(`/knowledges/marketplace/get/details/${knowledgeName}`);
};

export const installKnowledgeTemplate = (knowledgeName, indexId) => {
  return api.get(`/knowledges/install/${knowledgeName}/index/${indexId}`);
};

export const createApiKey = (apiName) => {
  return api.post(`/api-keys`, apiName);
};

export const getApiKeys = () => {
  return api.get(`/api-keys`);
};

export const editApiKey = (apiDetails) => {
  return api.put(`/api-keys`, apiDetails);
};

export const deleteApiKey = (apiId) => {
  return api.delete(`/api-keys/${apiId}`);
};

