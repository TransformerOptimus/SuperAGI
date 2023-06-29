import {baseUrl} from "@/pages/api/apiConfig";
import {EventBus} from "@/utils/eventBus";

export const  getUserTimezone = () => {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

export const formatTimeDifference = (timeDifference) => {
  const units = ['years', 'months', 'days', 'hours', 'minutes'];

  for (const unit of units) {
    if (timeDifference[unit] !== 0) {
      if (unit === 'minutes') {
        return `${timeDifference[unit]} minutes ago`;
      } else {
        return `${timeDifference[unit]} ${unit} ago`;
      }
    }
  }

  return 'Just now';
};

export const formatNumber = (number) => {
  if (number === null || number === undefined || number === 0) {
    return '0';
  }

  const suffixes = ['', 'k', 'M', 'B', 'T'];
  const magnitude = Math.floor(Math.log10(number) / 3);
  const scaledNumber = number / Math.pow(10, magnitude * 3);
  const suffix = suffixes[magnitude];

  if (scaledNumber % 1 === 0) {
    return scaledNumber.toFixed(0) + suffix;
  }

  return scaledNumber.toFixed(1) + suffix;
};

export const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) {
    return '0 Bytes';
  }

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const formattedValue = parseFloat((bytes / Math.pow(k, i)).toFixed(decimals));

  return `${formattedValue} ${sizes[i]}`;
}

export const downloadFile = (fileId) => {
  const authToken = localStorage.getItem('accessToken');
  const url = `${baseUrl()}/resources/get/${fileId}`;
  const env = localStorage.getItem('applicationEnvironment');

  if(env === 'PROD') {
    const headers = {
      Authorization: `Bearer ${authToken}`,
    };

    fetch(url, { headers })
      .then((response) => response.blob())
      .then((blob) => {
        const fileUrl = window.URL.createObjectURL(blob);
        window.open(fileUrl, "_blank");
      })
      .catch((error) => {
        console.error("Error downloading file:", error);
      });
  } else {
    window.open(url, "_blank");
  }
};

export const refreshUrl = () => {
  if (typeof window === 'undefined') {
    return;
  }

  const urlWithoutToken = window.location.origin + window.location.pathname;
  window.history.replaceState({}, document.title, urlWithoutToken);
};

export const loadingTextEffect = (loadingText, setLoadingText, timer) => {
  const text = loadingText;
  let dots = '';

  const interval = setInterval(() => {
    dots = dots.length < 3 ? dots + '.' : '';
    setLoadingText(`${text}${dots}`);
  }, timer);

  return () => clearInterval(interval)
}

export const openNewTab = (id, name, contentType) => {
  EventBus.emit('openNewTab', {
    element: {id: id, name: name, contentType: contentType, internalId: createInternalId()}
  });
}

export const removeTab = (id, name, contentType) => {
  EventBus.emit('removeTab', {
    element: {id: id, name: name, contentType: contentType}
  });
}

export const setLocalStorageValue = (key, value, stateFunction) => {
  stateFunction(value);
  localStorage.setItem(key, value);
  console.log(localStorage.getItem(key));
}

export const setLocalStorageArray = (key, value, stateFunction) => {
  stateFunction(value);
  const arrayString = JSON.stringify(value);
  localStorage.setItem(key, arrayString);
}

export const removeInternalId = (internalId) => {
  const internal_ids = localStorage.getItem("agi_internal_ids");
  let idsArray = internal_ids ? internal_ids.split(",").map(Number) : [];

  if(idsArray.length <= 0) {
    return;
  }

  const internalIdIndex = idsArray.indexOf(internalId);
  if (internalIdIndex !== -1) {
    idsArray.splice(internalIdIndex, 1);
    localStorage.setItem('agi_internal_ids', idsArray.join(','));
    localStorage.removeItem("agent_create_click_" + String(internalId));
    localStorage.removeItem("agent_name_" + String(internalId));
    localStorage.removeItem("agent_description_" + String(internalId));
    localStorage.removeItem("agent_goals_" + String(internalId));
    localStorage.removeItem("agent_instructions_" + String(internalId));
    localStorage.removeItem("agent_constraints_" + String(internalId));
    localStorage.removeItem("agent_model_" + String(internalId));
    localStorage.removeItem("agent_type_" + String(internalId));
    localStorage.removeItem("tool_names_" + String(internalId));
    localStorage.removeItem("tool_ids_" + String(internalId));
    localStorage.removeItem("agent_rolling_window_" + String(internalId));
    localStorage.removeItem("agent_database_" + String(internalId));
    localStorage.removeItem("agent_permission_" + String(internalId));
    localStorage.removeItem("agent_exit_criterion_" + String(internalId));
    localStorage.removeItem("agent_iterations_" + String(internalId));
    localStorage.removeItem("agent_step_time_" + String(internalId));
    localStorage.removeItem("advanced_options_" + String(internalId));
    localStorage.removeItem("has_LTM_" + String(internalId));
    localStorage.removeItem("has_resource_" + String(internalId));
    localStorage.removeItem("agent_files_" + String(internalId));
  }
}

export const createInternalId = () => {
  let newId = 1;

  if (typeof window !== 'undefined') {
    const internal_ids = localStorage.getItem("agi_internal_ids");
    let idsArray = internal_ids ? internal_ids.split(",").map(Number) : [];
    let found = false;

    for (let i = 1; !found; i++) {
      if (!idsArray.includes(i)) {
        newId = i;
        found = true;
      }
    }

    idsArray.push(newId);
    localStorage.setItem('agi_internal_ids', idsArray.join(','));
  }

  return newId;
}