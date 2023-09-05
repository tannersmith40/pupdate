<template>
  <Modal @close="$emit('close')">
    <h2>Edit Customer</h2>
    <form @submit.prevent="saveCustomer">
      <label>
        First Name:
        <input type="text" v-model="customerData.first_name" required />
      </label>
      <label>
        Last Name:
        <input type="text" v-model="customerData.last_name" required />
      </label>
      <label>
        Email:
        <input type="email" v-model="customerData.email" required />
      </label>
      <label>
        Phone Number:
        <input type="tel" v-model="customerData.phone_number" required />
      </label>
      <button type="submit">Save</button>
    </form>
  </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';

export default {
  components: {
    Modal,
  },
  props: {
    customer: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      customerData: { ...this.customer },
    };
  },
  methods: {
    async saveCustomer() {
      this.$emit('save', this.customerData);
    },
  },
};
</script>