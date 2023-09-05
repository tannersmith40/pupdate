import {createRouter, createWebHistory} from 'vue-router';
import {useCookies} from 'vue3-cookies';
import CreateAccount from './components/CreateAccount.vue';
import Login from './components/Login.vue';
import AccountInfo from './components/AccountInfo.vue';
import CurrentUpdates from './components/CurrentUpdates.vue';
import LoginCredentials from './components/LoginCredentials.vue';
import Payment from './components/Payment.vue';
import Pricing from "./components/Pricing.vue";
import Home from "@/components/Home.vue";
import Admin from "@/components/Admin.vue";
import store from './store';

const {cookies} = useCookies();

const routes = [
    {path: '/', component: Home},
    {
        path: '/create-account',
        component: CreateAccount,
    },
    {
        path: '/login',
        component: Login,
    },
    {
        path: '/account-info',
        component: AccountInfo,
        meta: {requiresAuth: true},
    },
    {
        path: '/current-updates',
        component: CurrentUpdates,
        meta: {requiresAuth: true},
    },
    {
        path: '/login-credentials',
        component: LoginCredentials,
        meta: {requiresAuth: true},
    },
    {
        path: '/payment',
        component: Payment,
        meta: {requiresAuth: true},
    },
    {
        path: '/admin',
        component: Admin,
        meta: {requiresAuth: true},
        beforeEnter: (to, from, next) => {
            const role = store.state.role;
            if (role === 'admin' || role === 'owner') {
                next();
            } else {
                next('/');
            }
        },
    },
    {
        path: '/pricing',
        component: Pricing
        // meta: { requiresAuth: true },
    }
]

const router = createRouter({
    history: createWebHistory('/'),
    routes,
});

router.beforeEach((to, from, next) => {
    if (to.meta.requiresAuth && !cookies.get('token')) {
        next('/login');
    } else {
        next();
    }
});

export default router;
