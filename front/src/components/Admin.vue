<template>
  <div class="ps-0">
    <div class="d-flex justify-content-between align-items-center ">
      <h1>Customers</h1>
      <button class="btn btn-primary ms-auto me-3" data-bs-toggle="modal" data-bs-target="#customerModal" @click="addNewCustomer">New Customer
      </button>
    </div>

    <div class="table-responsive">
      <table class="table table-hover m-0 p-0">
        <thead>
        <tr>
          <th>Status</th>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Role</th>
          <th>Date Start</th>
          <th>Date End</th>
          <th>Puppies</th>
          <th>Cycles</th>
          <th>Last</th>
          <th>Runs</th>
          <th>Result</th>
          <th>Detail</th>
        </tr>
        </thead>
        <tbody ref="customerRows">
        <tr v-for="customer in displayedCustomers" :key="customer.id">
          <td>
            <button type="button" class="btn btn-sm status-button"
                    :class="{ 'btn-success': customer.status, 'btn-warning': !customer.status }">
              {{ customer.status ? 'Active' : 'Inactive' }}
            </button>
          </td>

          <td class="text-truncate">{{ customer.first_name }} {{ customer.last_name }}</td>
          <td class="text-truncate">{{ customer.email }}</td>
          <td class="text-truncate">{{ customer.phone_number }}</td>
          <td class="text-truncate">{{ customer.role }}</td>
          <td class="text-truncate">{{ customer.date_start }}</td>
          <td class="text-truncate">{{ customer.date_end }}</td>
          <td class="text-truncate">{{ customer.max_puppies }}</td>
          <td class="text-truncate" title="Maximum number of launches per day">{{ customer.max_runs }}</td>
          <td class="text-truncate" :title="customer.task_date_end">{{ customer.task_date_end }}</td>
          <td class="text-truncate" title="Number of launches today">{{ customer.task_today_runs }}</td>
          <td class="text-truncate">{{ customer.task_result }}</td>
          <td class="text-truncate" :title="customer.task_result_detail" style="max-width: 100px; ">{{
              customer.task_result_detail
            }}
          </td>
          <td class="text-truncate">
            <button class="btn btn-sm btn-primary  me-2" data-bs-toggle="modal" data-bs-target="#customerModal"
                    @click="editCustomer(customer)">Edit
            </button>
            <!--          <button class="btn btn-sm btn-primary" @click="editCustomer(customer)">Edit</button>-->
            <button class="btn btn-sm btn-danger" data-bs-toggle="modal" data-bs-target="#deleteConfirmationModal"
                    @click="confirmDeleteCustomer(customer)">Delete
            </button>

          </td>
        </tr>
        </tbody>
      </table>
    </div>
      <div class="d-flex justify-content-center mt-5">
      <button class="btn btn-secondary me-4" @click="previousPage" :disabled="currentPage === 1">Previous</button>
      <button class="btn btn-secondary" @click="nextPage" :disabled="currentPage === pageCount">Next</button>
    </div>
  </div>

  <!-- Modal -->
  <div class="modal fade" id="customerModal" tabindex="-1" ref="SaveCustomeModalRef">
    <div class="modal-dialog">

      <div class="modal-content">
        <form @submit.prevent="editCustomerData ? saveCustomer() : createCustomer()">
          <div class="modal-header">
            <h5 class="modal-title">{{ editCustomerData ? 'Edit Customer' : 'New Customer' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>


            <div class="mb-3">
              <label for="first_name" class="form-label">First Name:</label>
              <input type="text" class="form-control" id="first_name" v-model="form.first_name"/>
            </div>
            <div class="mb-3">
              <label for="last_name" class="form-label">Last Name:</label>
              <input type="text" class="form-control" id="last_name" v-model="form.last_name"/>
            </div>
            <div class="mb-3">
              <label for="email" class="form-label">Email:</label>
              <input type="email" class="form-control" id="email" v-model="form.email"/>
            </div>
            <div class="mb-3">
              <label for="password" class="form-label">Password:</label>
              <input type="text" class="form-control" id="password" v-model="form.password"/>
            </div>
            <div class="mb-3">
              <label for="phone_number" class="form-label">Phone Number:</label>
              <input type="tel" class="form-control" id="phone_number" v-model="form.phone_number"/>
            </div>
            <div class="mb-3">
              <label for="role" class="form-label">Role:</label>
              <select class="form-select" id="role" v-model="form.role">
                <option value="user">User</option>
                <option value="admin">Admin</option>
                <option value="owner">Owner</option>
              </select>
            </div>
            <div class="mb-3">
              <label for="date_start" class="form-label">Date Start:</label>
              <input type="date" class="form-control" id="date_start" v-model="form.date_start"/>
            </div>
            <div class="mb-3">
              <label for="date_end" class="form-label">Date End:</label>
              <input type="date" class="form-control" id="date_end" v-model="form.date_end"/>
            </div>
            <div class="mb-3">
              <label for="max_puppy" class="form-label">Max Puppies:</label>
              <input type="number" class="form-control" id="max_puppies" v-model="form.max_puppies"/>
            </div>
            <div class="mb-3">
              <label for="max_cycle" class="form-label">Max Runs:</label>
              <input type="number" class="form-control" id="max_runs" v-model="form.max_runs"/>
            </div>
          </div>
          <div class="modal-footer">
            <button type="submit" class="btn btn-primary">{{ editCustomerData ? 'Save' : 'Create' }}</button>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Delete confirmation modal -->
  <div class="modal fade" id="deleteConfirmationModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Delete Customer {{ selectedCustomer ? selectedCustomer.email : '' }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          Are you sure you want to delete this customer ?
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn btn-danger" @click="deleteCustomer">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request';
import {Modal} from 'bootstrap';

export default {
  data() {
    return {
      errorMessage: '',
      customers: [],
      currentPage: 1,
      pageSize: 25,
      pageCount: 0,
      editCustomerData: null,
      showNewCustomerModal: false,
      customerToDelete: null,
      selectedCustomer: null,
      newCustomerData: {
        first_name: '',
        last_name: '',
        password: '',
        email: '',
        phone_number: '',
        role: 'user',
        date_start: '',
        date_end: '',
        max_puppies: '',
        max_runs: '',

      },
      form: {
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        phone_number: '',
        role: 'user',
        date_start: '',
        date_end: '',
        max_puppies: '',
        max_runs: '',
        user_id: '',
      },
    };
  },
  async created() {
    await this.fetchCustomers();
  },
  computed: {
    displayedCustomers() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.customers.slice(start, end);
    },
  },
  methods: {
    async fetchCustomers() {
      try {
        const data = await request.get('/customer');
        this.customers = data;
        this.pageCount = Math.ceil(this.customers.length / this.pageSize);
      } catch (error) {
        console.error(error);
      }


      this.pageCount = Math.ceil(this.customers.length / this.pageSize);
    },
    previousPage() {
      this.currentPage -= 1;
    },
    nextPage() {
      this.currentPage += 1;
    },
    editCustomer(customer) {
      this.errorMessage = '';
      const userRole = this.$store.state.role;
      if (userRole === 'owner' || (userRole === 'admin' && customer.role === 'user')) {
        console.log(customer);
        this.editCustomerData = {...customer};
        this.form = {...customer};
        this.currentForm = this.form;
      } else {
        this.errorMessage = 'You do not have permission to edit this customer record.';
        setTimeout(() => {
          this.errorMessage = '';
        }, 3000);
      }
    },
    async saveCustomer() {
      try {
        console.log("Save" + this.currentForm);
        const data = await request.put(`/customer`, this.currentForm);
        console.log(data);
        const index = this.customers.findIndex((customer) => customer.user_id === data.user_id);
        this.customers.splice(index, 1, {
          ...data,
          date_start: data.date_start ? new Date(new Date(data.date_start).setDate(new Date(data.date_start).getDate() + 1)).toISOString().split('T')[0] : null,
          date_end: data.date_end ? new Date(new Date(data.date_end).setDate(new Date(data.date_end).getDate() + 1)).toISOString().split('T')[0] : null,
        });
        this.editCustomerData = null;
        this.currentForm = null;
        if (data) this.errorMessage = '';
        const save_modal = document.querySelector('#customerModal');
        const modal = Modal.getInstance(save_modal);
        modal.hide();
      } catch (error) {
        console.error(error);
        this.errorMessage = error.message;
        // Display the Bootstrap modal with the error message

      }
    },


    confirmDeleteCustomer(customer) {
      this.customerToDelete = customer;
      this.selectedCustomer = customer;
      // const deleteConfirmationModalEl = document.querySelector('#deleteConfirmationModal');
      // const deleteConfirmationModal = new bootstrap.Modal(deleteConfirmationModalEl);
      // deleteConfirmationModal.show();
    },
    async deleteCustomer() {
      if (!this.customerToDelete) return;
      const index = this.customers.findIndex((c) => c.user_id === this.customerToDelete.user_id);
      if (index !== -1) {
        try {
          const response = await request.delete(`/customer/${this.customerToDelete.user_id}`);
          console.log(response);
          if (response && response.result && response.result == 'success') {
            this.customers.splice(index, 1);
            this.success = "Customer deleted.";
            setTimeout(() => {
              this.success = '';
            }, 5000);

          } else {
            this.error = "An error occurred while deleting customer.";
            setTimeout(() => {
              this.success = '';
            }, 5000);
          }
        } catch (error) {
          console.error(error);
          const deleteConfirmationModalEl = document.querySelector('#deleteConfirmationModal');
          const modal = Modal.getInstance(deleteConfirmationModalEl);
          modal.hide();
        }
      }
      const deleteConfirmationModalEl = document.querySelector('#deleteConfirmationModal');
      const modal = Modal.getInstance(deleteConfirmationModalEl);
      modal.hide();
      this.customerToDelete = null;
    },

    addNewCustomer() {
      this.showNewCustomerModal = true;
    },
    async createCustomer() {
      try {
        const data = await request.post('/customer', this.form);

        this.customers.push(data);
        // this.editCustomerData = null;
        // this.currentForm = null;
        if (data) this.errorMessage = '';
        const save_modal = document.querySelector('#customerModal');
        const modal = Modal.getInstance(save_modal);
        modal.hide();
      } catch (error) {
        console.error(error);
        this.errorMessage = error.message;
      }
    },
    scrollToFirstMatch() {
      const rows = this.$refs.customerRows;
      if (rows) {
        for (let i = 0; i < rows.length; i++) {
          const row = rows[i];
          if (row.offsetTop >= this.$el.scrollTop) {
            this.$el.scrollTop = row.offsetTop;
            break;
          }
        }
      }
    },
  }
  ,
  watch: {
    displayedCustomers() {
      this.scrollToFirstMatch();
    }
    ,
  }
  ,
}
;
</script>
<style scoped>
.status-button {
  cursor: default;
  pointer-events: none;
}
</style>