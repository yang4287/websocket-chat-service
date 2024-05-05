<template>
  <div id="app">
    <login-component v-if="!isLoggedIn" @login="handleLogin" />
    <chat-component v-if="isLoggedIn" :ws="websocket" />
  </div>
</template>

<script>
import LoginComponent from './components/LoginComponent.vue'
import ChatComponent from './components/ChatComponent.vue'

export default {
  components: {
    LoginComponent,
    ChatComponent
  },
  data() {
    return {
      isLoggedIn: false,
      websocket: null
    };
  },
  methods: {
    handleLogin(username) {
      this.websocket = new WebSocket(`ws://localhost:8000/ws/${username}`);
      this.websocket.onopen = () => {
        this.isLoggedIn = true;
      };
      this.websocket.onerror = (error) => {
        console.error('WebSocket Error: ', error);
      };
    }
  }
}
</script>
