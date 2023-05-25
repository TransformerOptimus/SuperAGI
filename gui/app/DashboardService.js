import axios from 'axios';

const fetchAgentList = async () => {
  try {
    const response = await axios.get('/api/my-endpoint');
    return response.data;
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
};