import { formatDistanceToNow, parseISO } from 'date-fns';
import { utcToZonedTime, zonedTimeToUtc } from 'date-fns-tz';
import {baseUrl} from "@/pages/api/apiConfig";
import {EventBus} from "@/utils/eventBus";
import JSZip from "jszip";
import moment from 'moment';

export const getUserTimezone = () => {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

export const convertToGMT = (dateTime) => {
  if (!dateTime) {
    return null;
  }
  return moment.utc(dateTime).format('YYYY-MM-DD HH:mm:ss');
};

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
export const formatTime = (lastExecutionTime) => {
  try {
    const parsedTime = new Date(lastExecutionTime + 'Z'); // append 'Z' to indicate UTC
    if (isNaN(parsedTime.getTime())) {
      throw new Error('Invalid time value');
    }

    const timeZone = 'Asia/Kolkata';
    const zonedTime = utcToZonedTime(parsedTime, timeZone);

    return formatDistanceToNow(zonedTime, {
      addSuffix: true,
      includeSeconds: true
    }).replace(/about\s/, '')
        .replace(/minutes?/, 'min')
        .replace(/hours?/, 'hrs')
        .replace(/days?/, 'day')
        .replace(/weeks?/, 'week');
  } catch (error) {
    console.error('Error formatting time:', error);
    return 'Invalid Time';
  }
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

export const downloadFile = (fileId, fileName = null) => {
  const authToken = localStorage.getItem('accessToken');
  const url = `${baseUrl()}/resources/get/${fileId}`;
  const env = localStorage.getItem('applicationEnvironment');

  if (env === 'PROD') {
    const headers = {
      Authorization: `Bearer ${authToken}`,
    };

    return fetch(url, { headers })
      .then((response) => response.blob())
      .then((blob) => {
        if (fileName) {
          const fileUrl = window.URL.createObjectURL(blob);
          const anchorElement = document.createElement('a');
          anchorElement.href = fileUrl;
          anchorElement.download = fileName;
          anchorElement.click();
          window.URL.revokeObjectURL(fileUrl);
        } else {
          return blob;
        }
      })
      .catch((error) => {
        console.error('Error downloading file:', error);
      });
  } else {
    if (fileName) {
      window.open(url, '_blank');
    } else {
      return fetch(url)
        .then((response) => response.blob())
        .catch((error) => {
          console.error('Error downloading file:', error);
        });
    }
  }
};

export const downloadAllFiles = (files,run_name) => {
  const zip = new JSZip();
  const promises = [];
  const fileNamesCount = {};

  files.forEach((file, index) => {
    fileNamesCount[file.name]
      ? fileNamesCount[file.name]++
      : (fileNamesCount[file.name] = 1);

    let modifiedFileName = file.name;
    if (fileNamesCount[file.name] > 1) {
      const fileExtensionIndex = file.name.lastIndexOf(".");
      const name = file.name.substring(0, fileExtensionIndex);
      const extension = file.name.substring(fileExtensionIndex + 1);
      modifiedFileName = `${name} (${fileNamesCount[file.name] - 1}).${extension}`;
    }

    const promise = downloadFile(file.id)
      .then((blob) => {
        const fileBlob = new Blob([blob], {type: file.type});
        zip.file(modifiedFileName, fileBlob);
      })
      .catch((error) => {
        console.error("Error downloading file:", error);
      });

    promises.push(promise);
  });

  Promise.all(promises)
      .then(() => {
        zip.generateAsync({ type: "blob" })
            .then((content) => {
              const now = new Date();
              const timestamp = `${now.getFullYear()}-${("0" + (now.getMonth() + 1)).slice(-2)}-${("0" + now.getDate()).slice(-2)}_${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}`.replace(/:/g, '-');
              const zipFilename = `${run_name}_${timestamp}.zip`;
              const downloadLink = document.createElement("a");
              downloadLink.href = URL.createObjectURL(content);
              downloadLink.download = zipFilename;
              downloadLink.click();
            })
            .catch((error) => {
              console.error("Error generating zip:", error);
            });
      });
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

export const openNewTab = (id, name, contentType, hasInternalId) => {
  EventBus.emit('openNewTab', {
    element: {id: id, name: name, contentType: contentType, internalId: hasInternalId ? createInternalId() : 0}
  });
}

export const removeTab = (id, name, contentType, internalId) => {
  EventBus.emit('removeTab', {
    element: {id: id, name: name, contentType: contentType, internalId: internalId}
  });
}

export const setLocalStorageValue = (key, value, stateFunction) => {
  stateFunction(value);
  localStorage.setItem(key, value);
}

export const setLocalStorageArray = (key, value, stateFunction) => {
  stateFunction(value);
  const arrayString = JSON.stringify(value);
  localStorage.setItem(key, arrayString);
}

const getInternalIds = () => {
  const internal_ids = localStorage.getItem("agi_internal_ids");
  return internal_ids ? JSON.parse(internal_ids) : [];
}

const removeAgentInternalId = (internalId) => {
  let idsArray = getInternalIds();
  const internalIdIndex = idsArray.indexOf(internalId);

  if (internalIdIndex !== -1) {
    idsArray.splice(internalIdIndex, 1);
    localStorage.setItem('agi_internal_ids', JSON.stringify(idsArray));
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
    localStorage.removeItem("agent_start_time_" + String(internalId));
    localStorage.removeItem("agent_expiry_date_" + String(internalId));
    localStorage.removeItem("agent_expiry_type_" + String(internalId));
    localStorage.removeItem("agent_expiry_runs_" + String(internalId));
    localStorage.removeItem("agent_time_unit_" + String(internalId));
    localStorage.removeItem("agent_time_value_" + String(internalId));
    localStorage.removeItem("agent_is_recurring_" + String(internalId));
  }
}

const removeAddToolkitInternalId = (internalId) => {
  let idsArray = getInternalIds();
  const internalIdIndex = idsArray.indexOf(internalId);

  if (internalIdIndex !== -1) {
    idsArray.splice(internalIdIndex, 1);
    localStorage.setItem('agi_internal_ids', JSON.stringify(idsArray));
    localStorage.removeItem('tool_github_' + String(internalId));
  }
}

const removeToolkitsInternalId = (internalId) => {
  let idsArray = getInternalIds();
  const internalIdIndex = idsArray.indexOf(internalId);

  if (internalIdIndex !== -1) {
    idsArray.splice(internalIdIndex, 1);
    localStorage.setItem('agi_internal_ids', JSON.stringify(idsArray));
    localStorage.removeItem('toolkit_tab_' + String(internalId));
    localStorage.removeItem('api_configs_' + String(internalId));
  }
}

export const resetLocalStorage = (contentType, internalId) => {
  switch (contentType) {
    case 'Create_Agent':
      removeAgentInternalId(internalId);
      break;
    case 'Add_Toolkit':
      removeAddToolkitInternalId(internalId);
      break;
    case 'Marketplace':
      localStorage.removeItem('marketplace_tab');
      localStorage.removeItem('market_item_clicked');
      localStorage.removeItem('market_detail_type');
      localStorage.removeItem('market_item');
      break;
    case 'Toolkits':
      removeToolkitsInternalId(internalId);
      break;
    default:
      break;
  }
}

export const createInternalId = () => {
  let newId = 1;

  if (typeof window !== 'undefined') {
    let idsArray = getInternalIds();
    let found = false;

    for (let i = 1; !found; i++) {
      if (!idsArray.includes(i)) {
        newId = i;
        found = true;
      }
    }

    idsArray.push(newId);
    localStorage.setItem('agi_internal_ids', JSON.stringify(idsArray));
  }

  return newId;
}

export const returnToolkitIcon = (toolkitName) => {
  const toolkitData = [
    {name: 'Jira Toolkit', imageSrc: '/images/jira_icon.svg'},
    {name: 'Email Toolkit', imageSrc: '/images/gmail_icon.svg'},
    {name: 'Google Calendar Toolkit', imageSrc: '/images/google_calender_icon.svg'},
    {name: 'GitHub Toolkit', imageSrc: '/images/github_icon.svg'},
    {name: 'Google Search Toolkit', imageSrc: '/images/google_search_icon.svg'},
    {name: 'Searx Toolkit', imageSrc: '/images/searx_icon.svg'},
    {name: 'Slack Toolkit', imageSrc: '/images/slack_icon.svg'},
    {name: 'Web Scrapper Toolkit', imageSrc: '/images/webscraper_icon.svg'},
    {name: 'Twitter Toolkit', imageSrc: '/images/twitter_icon.svg'},
    {name: 'Google SERP Toolkit', imageSrc: '/images/google_serp_icon.svg'},
    {name: 'File Toolkit', imageSrc: '/images/filemanager_icon.svg'},
    {name: 'CodingToolkit', imageSrc: '/images/app-logo-light.png'},
    {name: 'Image Generation Toolkit', imageSrc: '/images/app-logo-light.png'},
  ];

  const toolkit = toolkitData.find((tool) => tool.name === toolkitName);
  return toolkit ? toolkit.imageSrc : '/images/custom_tool.svg';
}

export const returnResourceIcon = (file) => {
  const fileTypeIcons = {
    'application/pdf': '/images/pdf_file.svg',
    'application/txt': '/images/txt_file.svg',
    'text/plain': '/images/txt_file.svg',
    'image': '/images/img_file.svg',
  };

  return fileTypeIcons[file.type] || '/images/default_file.svg';
};

export const convertToTitleCase = (str) => {
  if(str === null || str === '') {
    return '';
  }

  const words = str.toLowerCase().split('_');
  const capitalizedWords = words.map((word) => word.charAt(0).toUpperCase() + word.slice(1));
  return capitalizedWords.join(' ');
}