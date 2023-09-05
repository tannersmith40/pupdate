import axios from 'axios';
import { useCookies } from 'vue3-cookies';
import { useRouter } from 'vue-router';

const service = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 5000, // request timeout
});

// Request interceptor
service.interceptors.request.use(
  (config) => {
    const { cookies } = useCookies(['token']);
    const token = cookies.get('token');
    if (token) {

      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error(error); // for debug
    Promise.reject(error);
  },
);

// Response interceptor
service.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response.status === 401) {
      const router = useRouter();
      router.push('/login');
    }
    console.error('err' + error); // for debug
    return Promise.reject(error);
  },
);

export default service;
