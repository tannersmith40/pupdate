<script setup>

</script>
<template>
  <div class="main-content   ">
    <h1 class="text-center">Account Info</h1>
  </div>
  <div class="row justify-content-center">
    <div class="col-6">
      <form @submit.prevent="updateAccountInfo">
        <div class="mb-3">
          <label for="first_name" class="form-label">First Name</label>
          <input type="text" class="form-control" id="first_name" v-model="first_name" required>
        </div>
        <div class="mb-3">
          <label for="last_name" class="form-label">Last Name</label>
          <input type="text" class="form-control" id="last_name" v-model="last_name" required>
        </div>
        <div class="mb-3">
          <label for="phone_number" class="form-label">Phone Number</label>
          <input type="text" class="form-control" id="phone_number" v-model="phone_number" required>
        </div>
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input type="text" class="form-control" id="email" v-model="email" required>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input type="password" class="form-control" id="password" v-model="password" required>
        </div>
        <p v-if="loading">Loading...</p>
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
</template>

<script>

import request from '@/utils/request';

export default {
  data() {
    return {
      first_name: '',
      last_name: '',
      phone_number: '',
      email: '',
      password: '',
      error: '',
      success: '',
      loading: false,
    };
  },
  methods: {
    async getAccountInfo() {
      try {
        this.loading = true;
        const response = await request.get('/account-info');
        if (response) {
          this.first_name = response.first_name;
          this.last_name = response.last_name;
          this.phone_number = response.phone_number;
          this.email = response.email;
        } else {
          this.error = "An error occurred while retrieving user credentials.";
        }

      } catch (error) {
        this.error = "An error occurred while retrieving user  account info.";
        setTimeout(() => {
          this.success = '';
        }, 5000);
      } finally {
        this.loading = false;
      }
    },
    async updateAccountInfo() {
      try {
        this.loading = true;
        const response = await request.post('account-info', {
          email: this.email,
          password: this.password,
          first_name: this.first_name,
          last_name: this.last_name,
          phone_number: this.phone_number,
        },);
        if (response && response.result && response.result == 'success') {
          this.success = "Account Info updated successfully.";
          setTimeout(() => {
            this.success = '';
          }, 5000);
        } else {
          this.error = "An error occurred while updating user Account Info.";
          setTimeout(() => {
            this.success = '';
          }, 5000);
        }

      } catch (error) {
        console.log(error);
        this.error = "An error occurred while updating user Account Info. {error}";
        setTimeout(() => {
          this.success = '';
        }, 5000);
      } finally {
        this.loading = false;
      }
    },

  },
  mounted() {
    this.getAccountInfo();
  }
}
</script>
