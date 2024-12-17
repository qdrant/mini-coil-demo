import axios from 'axios';

export const axiosInstance = axios.create({
  baseURL: process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '/',
});

export function setupAxios(axios, { apiKey }) {
  if (process.env.NODE_ENV === 'development') {
    axios.defaults.baseURL = 'http://localhost:8000';
  } else {
    axios.defaults.baseURL = '/';
  }
}
