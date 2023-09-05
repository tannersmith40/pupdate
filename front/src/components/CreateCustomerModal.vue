<template>
  <Modal @close="$emit('close')">
    <h2>Create Customer</h2>
    <form @submit.prevent="createCustomer">
      <label>
        First Name:
        <input type="text" v-model="firstName" required />
      </label>
      <label>
        Last Name:
        <input type="text" v-model="lastName" required />
      </label>
      <label>
        Email:
        <input type="email" v-model="email" required />
      </label>
      <label>
        Phone Number:
        <input type="tel" v-model="phoneNumber" required />
      </label>
      <button type="submit">Create</button>
    </form>
  </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';

export default {
  components: {
    Modal,
  },
  data() {
    return {
      firstName: '',
      lastName: '',
      email: '',
      phoneNumber: '',
    };
  },
  methods: {
    async createCustomer() {
      const customerData = {
        first_name: this.firstName,
        last_name: this.lastName,
        email: this.email,
        phone_number: this.phoneNumber,
      };
      this.$emit('create', customerData);
    },
  },
};
</script>