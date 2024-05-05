<template>
  <div>
    <ul>
      <li v-for="message in messages" :key="message.id">{{ message.text }}</li>
    </ul>
    <input v-model="newMessage" @keyup.enter="sendMessage">
    <button @click="sendMessage">Send</button>
  </div>
</template>

<script>
export default {
  props: ['ws'],
  data() {
    return {
      newMessage: '',
      messages: []
    };
  },
  mounted() {
    this.ws.onmessage = (event) => {
      this.messages.push({ text: event.data, id: this.messages.length });
    };
  },
  methods: {
    sendMessage() {
      if (this.newMessage.trim() !== '') {
        this.ws.send(this.newMessage);
        this.newMessage = '';
      }
    }
  }
}
</script>
