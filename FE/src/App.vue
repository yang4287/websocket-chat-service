<template>
  <div>
    <login v-if="!isLoggedIn" @client-id-received="setupWebSocket"></login>
    <chat-room
      v-if="isLoggedIn"
      :ws="ws"
      :current-user-id="currentUserId"
      @left-chatroom="handleLeftChatroom"
    ></chat-room>
  </div>
</template>

<script>
import Login from "./components/Login.vue";
import ChatRoom from "./components/ChatRoom.vue";

export default {
  components: {
    Login,
    ChatRoom,
  },
  data() {
    return {
      ws: null,
      isLoggedIn: false,
      currentUserId: null,
    };
  },
  methods: {
    setupWebSocket(clientId) {
      this.currentUserId = clientId;
      console.log(this.currentUserId);
      this.ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);
      this.ws.onopen = () => {
        console.log("WebSocket connection established");
        this.isLoggedIn = true;
      };
      this.ws.onerror = (error) => {
        console.error("WebSocket error: ", error);
      };
      // this.ws.onclose = () => {
      //   console.log("WebSocket connection closed");
      //   this.isLoggedIn = false;
      //   this.ws = null;
      // };
    },
    handleLeftChatroom() {
      this.isLoggedIn = false;
    },
  },
};
</script>