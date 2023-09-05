<template>
  <nav class="navbar bg-dark text-white navbar-expand bg-body-tertiary sticky-top" style="height: 120px; top: 0;">
    <div class="d-flex justify-content-between w-100">
      <a v-bind:class="isLoggedIn ? 'col-md-9 col-lg-10' : 'col-md-8 col-lg-9'" class="navbar-brand" href="#">
        <img src="/pupdate-logo.png" alt="PupDate" class="d-inline-block align-text-top"></a>
      <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNavAltMarkup"
          aria-controls="navbarNavAltMarkup"
          aria-expanded="false"
          aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link to="/" class="nav-link"><h5 class="text-light">Home</h5></router-link>
          </li>
          <li class="nav-item">
            <router-link to="/pricing" class="nav-link"><h5 class="text-light">Pricing</h5></router-link>
          </li>
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link to="/login" class="nav-link"><h5 class="text-light">Login</h5></router-link>
          </li>
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link to="/create-account" class="nav-link"><h5 class="text-light">Sign Up</h5></router-link>
          </li>
          <li class="nav-item" v-if="isLoggedIn">
            <a href="#" @click="logout" class="nav-link"><h5 class="text-light">Logout</h5></a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import {mapState} from 'vuex';

export default {
  methods: {
    logout() {
      this.$emit('logout');
    },
  },
  computed: {
    ...mapState(['isLoggedIn']),
  },
};
</script>
<style scoped>
.bg-dark {
  background-color: #1f4d64 !important;
}
</style>