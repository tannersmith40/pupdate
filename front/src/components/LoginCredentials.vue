<script setup>

</script>

<template>
  <div class="main-content  ts-0">
    <h1 class="text-center">Login Credentials</h1></div>
  <div class="row justify-content-center">
    <div class="main-content col-6 p-3">
      <form @submit.prevent="updateUserCredentials">
        <h2>Lancaster Puppies</h2>
        <div class="mb-3">
          <label for="username" class="form-label">Lancaster Email</label>
          <input type="text" class="form-control" id="lancaster_username" v-model="lancaster_email" required>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Lancaster Password</label>
          <input type="password" class="form-control" id="lancaster_password" v-model="lancaster_password" required>
        </div>
        <h2>Gmail</h2>
        <div class="mb-3">
          <label for="username" class="form-label">Email</label>
          <input type="text" class="form-control" id="username" v-model="gmail_username" @input="wasGmailModified = true" required>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">
            Gmail App Password
            <a href="#" class="text-primary" data-bs-toggle="modal" data-bs-target="#passwordHelpModal">Help</a>
          </label>
          <input type="password" class="form-control" id="password" v-model="gmail_password" required>
        </div>
        <div v-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>
        <div v-if="success" class="alert alert-success" role="alert">
          {{ success }}
        </div>
        <div class="d-flex justify-content-center mt-3">
          <button type="submit" class="btn btn-primary">Save</button>
        </div>
      </form>
    </div>
  </div>
  <div class="modal fade" id="passwordHelpModal" tabindex="-1" aria-labelledby="passwordHelpModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="passwordHelpModalLabel">Gmail App Password Tutorial</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <!-- Put your tutorial here. You could use a <video> element or an <iframe> for a YouTube video -->
          <p>Here is how to create a Gmail app password...</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        </div>
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
      lancaster_email: '',
      lancaster_password: '',
      gmail_username: '',
      gmail_password: '',
      error: '',
      success: '',
      wasGmailModified: false,
    };
  },
  methods: {
    async getUserCredentials() {
      try {
        const {cookies} = useCookies();
        const token = cookies.get('token');
        if (!token) {
          this.$router.push('/');
        } else {
          const response = await axios.get(`${API_URL}/user_credentials`, {
            headers: {
              Authorization: `Bearer ${token}`,
            }
          });

          if (response.data) {
            this.lancaster_email = response.data.lancaster_email;
            this.lancaster_password = response.data.lancaster_password;
            this.gmail_username = response.data.gmail_username;
            this.gmail_password = response.data.gmail_password;
          } else {
            this.error = "An error occurred while retrieving user credentials.";
          }
        }
      } catch (error) {
        this.error = "An error occurred while retrieving user credentials.";
      }
    },
    async updateUserCredentials() {
      try {
        const {cookies} = useCookies();
        const token = cookies.get('token');
        if (!token) {
          this.$router.push('/');
        } else {
          const response = await axios.post(`${API_URL}/user_credentials`, {
            lancaster_email: this.lancaster_email,
            lancaster_password: this.lancaster_password,
            gmail_username: this.gmail_username,
            gmail_password: this.gmail_password
          }, {
            headers: {
              Authorization: `Bearer ${token}`,
            }
          });
          if (response.data && response.data.result && response.data.result == 'success') {
            this.success = "User credentials updated successfully.";
            setTimeout(() => {
              this.success = '';
            }, 5000);
          } else {
            this.error = "An error occurred while updating user credentials.";
            setTimeout(() => {
              this.success = '';
            }, 5000);
          }
        }
      } catch (error) {
        console.log(error);
        this.error = "An error occurred while updating user credentials.";
      }
    },
    async user_credentials() {
      try {
        const {cookies} = useCookies();
        const token = cookies.get('token');
        if (!token) {
          this.$router.push('/');
        } else {
          const response = await axios.get(`${API_URL}/user_credentials`, {
            headers: {
              Authorization: `Bearer ${token}`,
            }
          });

          if (response.data && response.data.result && response.data.result == 'success') {
            this.lancaster_email = response.data.lancaster_email;
            this.lancaster_password = response.data.lancaster_password;
            this.gmail_username = response.data.gmail_username;
            this.gmail_password = response.data.gmail_password;
          } else {
            this.error = "An error occurred while retrieving user credentials.";
          }
        }
      } catch (error) {
        this.error = error.response.data.detail || "An error occurred while retrieving user credentials.";
      }
    }
  },
  watch: {
    lancaster_email(newEmail) {
      if (!this.wasGmailModified) {
        this.gmail_username = newEmail;
      }
    },
  },
  mounted() {
    this.getUserCredentials();
  }
}
</script>
<style scoped>

</style>