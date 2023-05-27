export const convertToHash = (data) => {
  return Object.entries(data).reduce((acc, [key, value]) => {
    acc[key] = value;
    return acc;
  }, {});
}