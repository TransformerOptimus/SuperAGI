import { formatDistanceToNow, parseISO } from 'date-fns';
import {baseUrl} from "@/pages/api/apiConfig";

export const formatTime = (lastExecutionTime) => {
  try {
    const parsedTime = parseISO(lastExecutionTime);
    if (isNaN(parsedTime.getTime())) {
      throw new Error('Invalid time value');
    }
    return formatDistanceToNow(parsedTime, {
      addSuffix: true,
      includeSeconds: true,
    }).replace(/about\s/, '');
  } catch (error) {
    console.error('Error formatting time:', error);
    return 'Invalid Time';
  }
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

export const  downloadFile = (fileId) => {
  window.open(`${baseUrl()}/resources/get/${fileId}`, '_blank');
}

export const refreshUrl = () => {
  if (typeof window === 'undefined') {
    return;
  }

  const urlWithoutToken = window.location.origin + window.location.pathname;
  window.history.replaceState({}, document.title, urlWithoutToken);
};