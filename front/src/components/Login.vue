<template>
        <div class="row align-items-center pt-5 justify-content-center">
            <div class="main-content col-6 ">
                <h1>Login</h1>
                <form @submit.prevent="login">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" v-model="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" v-model="password" required>
                    </div>
                    <div v-if="error" class="alert alert-danger" role="alert">
                        {{ error }}
                    </div>
                    <button type="submit" class="btn btn-primary">Login</button>
                </form>
            </div>
        </div>
</template>


<script>
import axios from 'axios';
import { useCookies } from 'vue3-cookies';
import { API_URL } from '../api-config.js';

export default {
  data() {
    return {
      username: '',
      password: '',
      error: '',
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post(`${API_URL}/token`, {
          username: this.username,
          password: this.password,
        }, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        });

        if (response.data && response.data.access_token) {
          const { cookies } = useCookies();
          cookies.set('token', response.data.access_token, { expires: 7 }); // Set the authentication token cookie with an expiration date of 7 days
          cookies.set('role', response.data.role, { expires: 7 }); // Set the role cookie with an expiration date of 7 days
          this.$store.commit('setLoggedIn', true);
          this.$store.commit('setRole', response.data.role);
          this.$router.push('/current-updates');
        } else {
          console.error(response);
          this.error = 'An error occurred while logging in.';
        }
      } catch (error) {
        console.error(error);
        this.error = error.response.data.detail || 'An error occurred while logging in.';
      }
    },
  },
  mounted() {
    const { cookies } = useCookies();
    const token = cookies.get('token');
    const role = cookies.get('role');
    if (token && role) {
      this.$store.commit('setLoggedIn', true);
      this.$store.commit('setRole', role);
      this.$router.push('/');
    }
  },
};
</script>
