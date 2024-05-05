<template>
  <div>
    <input v-model="username" placeholder="Enter your username">
    <button @click="login">進入聊天室</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: ''
    };
  },
  methods: {
    login() {
      this.$emit('login', this.username);
    }
  }
}
</script>