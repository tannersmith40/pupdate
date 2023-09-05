import { createStore } from 'vuex';
import { createApp } from 'vue';
import createPersistedState from 'vuex-persistedstate';
import VueCookies from 'vue3-cookies';

const app = createApp({});
app.use(VueCookies);

export default createStore({
  state: {
    isLoggedIn: false,
    role: null,
  },
  mutations: {
    setLoggedIn(state) {
      state.isLoggedIn = true;
    },
    setLoggedOut(state) {
      state.isLoggedIn = false;
    },
    setRole(state, role) {
      state.role = role;
    },
  },
  actions: {
    login({ commit }) {
      commit('setLoggedIn');
    },
    logout({ commit }) {
       app.config.globalProperties.$cookies.remove('token');
      commit('setLoggedOut');
      commit('setRole', null);
    },
    setRole({ commit }, role) {
      commit('setRole', role);
    },
  },
  getters: {
    isLoggedIn(state) {
      return state.isLoggedIn;
    },
    role(state) {
      return state.role;
    },
  },
  plugins: [createPersistedState()],
});