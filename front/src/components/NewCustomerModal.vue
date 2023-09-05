<template>
  <div class="modal" tabindex="-1" role="dialog" :class="{ show: showNewCustomerModal }">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">New Customer</h5>
          <button type="button" class="btn-close" @click="showNewCustomerModal = false"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="first_name" class="form-label">First Name</label>
            <input type="text" class="form-control" id="first_name" v-model="newCustomerData.first_name" />
          </div>
          <div class="mb-3">
            <label for="last_name" class="form-label">Last Name</label>
            <input type="text" class="form-control" id="last_name" v-model="newCustomerData.last_name" />
          </div>
          <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input type="email" class="form-control" id="email" v-model="newCustomerData.email" />
          </div>
          <div class="mb-3">
            <label for="phone_number" class="form-label">Phone Number</label>
            <input type="tel" class="form-control" id="phone_number" v-model="newCustomerData.phone_number" />
          </div>
          <div class="mb-3">
            <label for="role" class="form-label">Role</label>
            <select class="form-select" id="role" v-model="newCustomerData.role">
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div class="mb-3">
            <label for="date_start" class="form-label">Date Start</label>
            <input type="date" class="form-control" id="date_start" v-model="newCustomerData.date_start" />
          </div>
          <div class="mb-3">
            <label for="date_end" class="form-label">Date End</label>
            <input type="date" class="form-control" id="date_end" v-model="newCustomerData.date_end" />
          </div>
          <div class="mb-3">
            <label for="max_puppy" class="form-label">Max Puppy</label>
            <input type="number" class="form-control" id="max_puppy" v-model="newCustomerData.max_puppy" />
          </div>
          <div class="mb-3">
            <label for="max_cycle" class="form-label">Max Cycle</label>
            <input type="number" class="form-control" id="max_cycle" v-model="newCustomerData.max_cycle" />
          </div>
          <div class="mb-3">
            <label for="status" class="form-label">Status</label>
            <select class="form-select" id="status" v-model="newCustomerData.status">
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showNewCustomerModal = false">Cancel</button>
          <button type="button" class="btn btn-primary" @click="createCustomer">Create</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    showNewCustomerModal: {
      type: Boolean,
      required: true,
    },
    newCustomerData: {
      type: Object,
      required: true,
    },
  },
  methods: {
    createCustomer() {
      this.$emit('create-customer');
    },
  },
};
</script>