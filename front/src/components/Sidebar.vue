<template>
  <div class="ps-0">
    <div class="col-auto bg-dark sidebar">
      <div class="d-flex flex-column align-items-start ms-3 pt-3 text-white">
        <ul class="nav nav-pills flex-column mb-sm-auto ms-0 mb-0 text-light" id="menu">
          <li class="nav-item">
            <router-link to="/current-updates" class="nav-link">
              <h5 class="text-light" :class="{ 'fs-4': $route.path ==='/current-updates'}">
                <span class="text-truncate">Current Updates</span>
              </h5>
            </router-link>
          </li>
          <li>
            <router-link to="/login-credentials" class="nav-link">
              <h5 class="text-light" :class="{ 'fs-4': $route.path ==='/login-credentials'}"><span class="text-truncate">Login Credentials</span>
              </h5>
            </router-link>
          </li>
          <li>
            <router-link to="/payment" class="nav-link">
              <h5 class="text-light" :class="{ 'fs-4': $route.path ==='/payment'}"><span class="">Payment</span></h5>
            </router-link>
          </li>
          <li>
            <router-link to="/account-info" class="nav-link">
              <h5 class="text-light" :class="{ 'fs-4': $route.path ==='/account-info'}"><span
                  class="text-truncate">Account Info</span></h5>
            </router-link>
          </li>
          <li v-if="cookies.get('role') === 'admin' || cookies.get('role') === 'owner'" class="nav-item">
            <router-link to="/admin" class="nav-link">
              <h5 class="text-light" :class="{ 'fs-4': $route.path ==='/admin'}"><span class="">Admin</span></h5>
            </router-link>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import {useCookies} from 'vue3-cookies';

export default {
  name: "Sidebar",
  setup() {
    const {cookies} = useCookies();
    return {
      cookies,
    };
  },
};
</script>

<style scoped>
@media (min-width: 768px) {
  .sidebar {
    height: calc(100vh - 120px);
    top: 0;
  }
}

.bg-dark {
  background-color: #1f4d64 !important;
}

</style>