<template>
  <div id="app" class="container-fluid m-0 p-0 overflow-hidden d-flex flex-column" style="position: relative;">
    <Navbar @logout="logout" class="text-white"/>
    <div class="row flex-grow-1">
      <div class="col-md-2 ms-0 text-white overflow-hidden" v-if="isLoggedIn">
        <Sidebar/>
      </div>

      <div v-bind:class="isLoggedIn ? 'col-md-10' : 'col-md-12'" class="bg-light pt-5 overflow-auto" style="height: calc(100vh - 120px);
    overflow-y: auto;">
        <router-view/>
      </div>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex';
import {useCookies} from 'vue3-cookies';
import Navbar from './components/Navbar.vue';
import Sidebar from './components/Sidebar.vue';

export default {
  components: {
    Navbar,
    Sidebar,
  },
  computed: {
    ...mapState(['isLoggedIn']),
  },
  methods: {
    async logout() {
      try {
        const {cookies} = useCookies();

        cookies.remove('token');
        cookies.remove('role');
        await this.$store.dispatch('logout');
        console.log(this.$store.state.isLoggedIn);
      } catch (err) {
        console.error(err);
      }
    },
  },
};
</script>

<style>
#app {
  .text-white {
    color: white;
  }

  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.bg-light {
  background-color: #ffffff !important;
}
</style>

<script setup>
</script>