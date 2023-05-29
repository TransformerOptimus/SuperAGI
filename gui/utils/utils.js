import { formatDistanceToNow } from 'date-fns';

export const formatTime = (lastExecutionTime) => {
  return formatDistanceToNow(new Date(lastExecutionTime), {
    addSuffix: true,
  });
};