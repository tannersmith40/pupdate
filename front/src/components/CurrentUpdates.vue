<script setup>

</script>
<template>
  <div>
    <div class="d-flex justify-content-between align-items-center my-4">
 <h1 class="text-center flex-grow-1">Current Updates</h1>
      <button class="btn btn-primary ms-auto me-3" @click="fetchLogs">Refresh</button>

    </div>
    <div class="log-container">
      <div class="log-content">
        <table class="table table-striped">
          <thead>
          <tr>
            <th class="col-2" :style="{ minWidth: `${maxTimestampLength}px` }">Timestamp</th>
            <th class="col-10">Updates</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td style="width: 200px">{{ formatTimestamp(log.timestamp) }}</td>
            <td>{{ log.message }}</td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
  </div>
</template>

<script>
import {reactive, onMounted, toRefs, computed} from 'vue';
import request from '@/utils/request';

export default {
  name: 'LogTable',
  setup() {
    const state = reactive({
      logs: [],
      loading: false,
      error: null,
    });

    const fetchLogs = async () => {
      try {
        state.loading = true;
        const response = await request.get('/logs');
        if (!response) {
          state.error = 'An error occurred while fetching logs.';
          throw new Error('Network response was not ok');
        }
        const data = response
        state.logs = Array.isArray(data) ? data : Object.values(data);
      } catch (error) {
        state.error = 'An error occurred while fetching logs.';
        console.error(error);
        setTimeout(() => {
          state.success = '';
        }, 5000);
      } finally {
        state.loading = false;
      }
    };

    const maxTimestampLength = computed(() => {
      const timestamps = state.logs.map(log => log.timestamp);
      const formattedTimestamps = timestamps.map(timestamp => formatTimestamp(timestamp));
      return Math.max(...formattedTimestamps.map(timestamp => timestamp.length));
    });

    const formatTimestamp = timestamp => {
      const date = new Date(timestamp);
      return date.toISOString().slice(0, 19).replace('T', ' ');
    };

    onMounted(() => {
      fetchLogs();
    });

    return {
      ...toRefs(state),
      fetchLogs,
      maxTimestampLength,
      formatTimestamp,
    };
  },
};
</script>

<style scoped>

.log-container {
  display: flex;
  flex-direction: column;
  height: 100vh; /* Set the height of the container to the full viewport height */
}


.log-content {
  flex-grow: 1;
  overflow-y: auto;
}
</style>