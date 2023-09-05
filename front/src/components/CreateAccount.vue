<template>
  <div class="row justify-content-center">
    <div class="main-content col-6 p-3">
      <div class="main-content p-3">
        <h1>Create Account</h1>
        <form @submit.prevent="createAccount">
          <div class="mb-3">
            <label for="firstName" class="form-label">First Name</label>
            <input type="text" class="form-control" id="firstName" v-model="firstName" required>
          </div>
          <div class="mb-3">
            <label for="lastName" class="form-label">Last Name</label>
            <input type="text" class="form-control" id="lastName" v-model="lastName" required>
          </div>
          <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input type="email" class="form-control" id="email" v-model="email" required>
          </div>
          <div class="mb-3">
            <label for="phone" class="form-label">Phone</label>
            <input type="tel" class="form-control" id="phone" v-model="phone" required>
          </div>
          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input type="password" class="form-control" id="password" v-model="password" required>
          </div>
          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>
          <button type="submit" class="btn btn-primary">Create</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import {useCookies} from 'vue3-cookies';
import {API_URL} from '../api-config.js';

export default {
  data() {
    return {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      password: '',
      error: ''
    };
  },
  methods: {
    async createAccount() {
      try {
        const response = await axios.post(`${API_URL}/create-account`, {
          first_name: this.firstName,
          last_name: this.lastName,
          email: this.email,
          phone_number: this.phone,
          password: this.password,
        });

        if (!response || !response.data) {
          this.error = "No response received from the server.";
          return;
        }

        console.log(response);

        if (response.data && response.data.access_token) {
          const {cookies} = useCookies();
          cookies.set('token', response.data.access_token, {expires: 7}); // Set the authentication token cookie with an expiration date of 7 days
          cookies.set('role', response.data.role, {expires: 7}); // Set the role cookie with an expiration date of 7 days
          this.$store.commit('setLoggedIn', true); // Set the 'loggedIn' state to true in the store
          this.$store.commit('setRole', response.data.role); // Set the 'role' state to the user's role in the store
          this.$router.push('/');
        } else {
          this.error = "An error occurred while creating your account.";
        }
      } catch (error) {
        console.log(error); // add this line to log the full error object
        this.error = error.response.data.detail || "An error occurred while creating your account.";
      }

    },
    // async createAccount() {
    //   try {
    //     const response = await axios.post(`${API_URL}/create-account`, {
    //       first_name: this.firstName,
    //       last_name: this.lastName,
    //       email: this.email,
    //       phone_number: this.phone,
    //       password: this.password,
    //     });
    //     console.log(response);
    //     if (response.data && response.data.token) {
    //       const { setCookie } = useCookies();
    //       setCookie('token', response.data.token, { path: '/' });
    //       this.$router.push('/');
    //     } else {
    //       this.error = "An error occurred while creating your account.";
    //     }
    //   } catch (error) {
    //     this.error = error.response.data.detail || "An error occurred while creating your account.";
    //   }
    // },
  },
};
</script>


