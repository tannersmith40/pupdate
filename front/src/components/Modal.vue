<template>
  <div class="modal-mask">
    <div class="modal-wrapper">
      <div class="modal-container">
        <div class="modal-header">
          <slot name="header"></slot>
          <button class="modal-close-button" @click="$emit('close')">
            X
          </button>
        </div>
        <div class="modal-body">
          <slot></slot>
          <form @submit.prevent="saveCustomer">
            <label>
              First Name:
              <input type="text" v-model="firstNameInput" required />
            </label>
            <label>
              Last Name:
              <input type="text" v-model="lastNameInput" required />
            </label>
            <label>
              Email:
              <input type="email" v-model="emailInput" required />
            </label>
            <label>
              Phone Number:
              <input type="tel" v-model="phoneNumberInput" required />
            </label>
            <button type="submit">Save</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    customer: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      firstNameInput: this.customer.first_name,
      lastNameInput: this.customer.last_name,
      emailInput: this.customer.email,
      phoneNumberInput: this.customer.phone_number,
    };
  },
  methods: {
    async saveCustomer() {
      const customerData = {
        first_name: this.firstNameInput,
        last_name: this.lastNameInput,
        email: this.emailInput,
        phone_number: this.phoneNumberInput,
      };
      this.$emit('save', customerData);
    },
  },
};
</script>

<style scoped>
.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: table;
  transition: opacity 0.3s ease;
}

.modal-wrapper {
  display: table-cell;
  vertical-align: middle;
}

.modal-container {
  width: 300px;
  margin: 0px auto;
  padding: 20px 30px;
  background-color: #fff;
  border-radius: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);
  transition: all 0.3s ease;
  font-family: Helvetica, Arial, sans-serif;
}

.modal-header {
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: bold;
}

.modal-body {
  margin-bottom: 10px;
}

.modal-close-button {
  position: absolute;
  top: 5px;
  right: 5px;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  background-color: transparent;
}
</style>