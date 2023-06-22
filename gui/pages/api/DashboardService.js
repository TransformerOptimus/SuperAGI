import api from './apiConfig';

export const getOrganisation = (userId) => {
  return api.get(`/organisations/get/user/${userId}`);
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

export const getTools = () => {
  return api.get(`/tools/get`);
};

export const getAgentDetails = (agentId) => {
  return api.get(`/agents/get/details/${agentId}`);
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

export const createAgent = (agentData) => {
  return api.post(`/agents/create`, agentData);
};

export const updateAgents = (agentData) => {
  return api.put(`/agentconfigs/update/`, agentData);
};

export const updateExecution = (executionId, executionData) => {
  return api.put(`/agentexecutions/update/${executionId}`, executionData);
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
}

export const validateAccessToken = () => {
  return api.get(`/validate-access-token`);
}

export const checkEnvironment = () => {
  return api.get(`/configs/get/env`);
}

export const getOrganisationConfig = (organisationId, key) => {
  return api.get(`/configs/get/organisation/${organisationId}/key/${key}`);
}

export const updateOrganisationConfig = (organisationId, configData) => {
  return api.post(`/configs/add/organisation/${organisationId}`, configData);
}

export const fetchAgentTemplateList = () => {
  return api.get('/agent_templates/list?template_source=marketplace');
}

export const fetchAgentTemplateListLocal = () => {
  return api.get('/agent_templates/list?template_source=local');
}

export const saveAgentAsTemplate = (agentId) => {
  return api.post(`agent_templates/save_agent_as_template/${agentId}`);
}

export const fetchAgentTemplateConfig = (templateId) => {
  return api.get(`agent_templates/get/${templateId}?template_source=marketplace`);
}

export const fetchAgentTemplateConfigLocal = (templateId) => {
  return api.get(`agent_templates/agent_config?agent_template_id=${templateId}`);
}

export const installAgentTemplate = (templateId) => {
  return api.post(`agent_templates/download?agent_template_id=${templateId}`);
}

export const updatePermissions = (permissionId, data) => {
  return api.put(`/agentexecutionpermissions/update/status/${permissionId}`, data)
}