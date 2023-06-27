import {baseUrl} from "@/pages/api/apiConfig";
import {EventBus} from "@/utils/eventBus";

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
    element: {id: id, name: name, contentType: contentType}
  });
}

export const removeTab = (id, name, contentType) => {
  EventBus.emit('removeTab', {
    element: {id: id, name: name, contentType: contentType}
  });
}