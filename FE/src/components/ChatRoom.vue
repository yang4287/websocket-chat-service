<template>
  <div class="chat-container">
    <header class="chat-header">
      <div>
        線上聊天室
        <span class="participants-container">
          <i class="fa-solid fa-users"></i>
          {{ participantsCount }}
        </span>
      </div>
      <button @click="leaveChatroom" class="leave-button">離開聊天室</button>
    </header>
    <ul class="messages" ref="messagesContainer">
      <li
        v-for="message in messages"
        :key="message.id"
        class="message"
        :class="{
          'my-message':
            message.type === 'message' && message.userName === currentUserId,
          'other-message':
            message.type === 'message' && message.userName !== currentUserId,
        }"
      >
        <template v-if="message.type === 'message'">
          <div class="message-content">
            <div class="user-name">{{ message.userName }}</div>
            <div class="message-text">{{ message.text }}</div>
            <!-- <div class="message-time">{{ message.time }}</div> -->
          </div>
        </template>
        <template v-else>
          <div class="system-message">{{ message.text }}</div>
        </template>
      </li>
    </ul>
    <form @submit.prevent="sendMessage" class="message-form">
      <input type="text" v-model="newMessage" placeholder="Write a message" />
      <button type="submit">Send</button>
    </form>
  </div>
</template>

<script>
export default {
  props: ["ws", "currentUserId"],
  data() {
    return {
      newMessage: "",
      participantsCount: 0,
      messages: [],
      clientColors: {},
    };
  },
  mounted() {
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.participantsCount = data.num_participants;
      if (data.type === "join") {
        this.messages.push({
          userName: data.client_id,
          text: `${data.client_id} 加入聊天室`,
          id: this.messages.length,
          type: data.type,
        });
      } else if (data.type === "message") {
        this.messages.push({
          userName: data.client_id,
          text: data.message,
          id: this.messages.length,
          type: data.type,
        });
      } else if (data.type === "leave") {
        this.messages.push({
          userName: data.client_id,
          text: `${data.client_id} 離開聊天室`,
          id: this.messages.length,
          type: data.type,
        });
      }
    };
  },
  methods: {
    sendMessage() {
      if (this.newMessage.trim()) {
        this.ws.send(this.newMessage);
        this.newMessage = "";
        this.scrollToBottom();
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        container.scrollTop = container.scrollHeight;
      });
    },
    leaveChatroom() {
      if (this.ws) {
        this.ws.close();
      }
      alert("你已離開聊天室！");
      this.$emit("left-chatroom");
    },
  },
  updated() {
    this.scrollToBottom();
  },
};
</script>

<style scoped>
.chat-container {
  font-family: Arial, sans-serif;
  background-color: #f9f9f9;
  max-width: 600px;
  margin: 20px auto;
  border: 1px solid #ddd;
  box-shadow: 0 0 5px #ddd;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 10px 20px;
  border-bottom: 1px solid #ddd;
  font-size: 18px;
}

.participants {
  font-size: 14px;
  color: #666;
}
.participants-container {
  padding: 0 8px;
}

.fa-users {
  margin-right: 5px;
}
.messages {
  list-style: none;
  margin: 0;
  padding: 0;
  height: 300px;
  overflow-y: scroll;
}
.message {
  display: flex;
  justify-content: space-around;
}

.my-message {
  justify-content: flex-end;
}

.my-message .message-content {
  background-color: #e7f5ff;
  align-self: flex-end;
}

.other-message {
  justify-content: flex-start;
}

.other-message .message-content {
  background-color: #fff;
  align-self: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 2%;
  border-radius: 10px 10px 10px 0;
  margin: 2%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  color: #333;
}

.user-name {
  font-weight: bold;
  font-size: 14px;
  color: #7952b3; /* 柔和的紫色 */
}

.message-text {
  margin-top: 5px;
}

.message-time {
  margin-top: 5px;
  font-size: 12px;
  color: #999;
}

.message-form {
  display: flex;
  padding: 10px;
  background: #fff;
  border-top: 1px solid #ddd;
}

.message-form input {
  flex: 1;
  width: 80%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-right: 10px;
}

.message-form button {
  padding: 10px 20px;
  background: #5cb85c;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.user-image {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  margin-right: 10px;
}
.system-message {
  text-align: center;
  color: #888;
  font-style: italic;
}
.leave-button {
  padding: 5px 10px;
  margin-left: 20px;
  background-color: #f44336; /* 红色背景表示离开动作 */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.leave-button:hover {
  background-color: #d32f2f; /* 鼠标悬浮时的深红色 */
}
</style>