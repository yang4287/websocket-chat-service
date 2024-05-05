

<template>
  <div class="login-container">
    <div class="login-form">
      <h1>線上聊天室</h1>
      <input v-model="username" placeholder="輸入您的暱稱" />
      <button @click="login">進入聊天室</button>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      username: "",
    };
  },
  methods: {
    async login() {
      if (this.username.trim()) {
        try {
          const response = await fetch(
            `http://localhost:8000/get_client_id?username=${encodeURIComponent(
              this.username
            )}`
          );
          const data = await response.json();
          // 將 client_id 傳給父元件
          this.$emit("client-id-received", data.client_id);
        } catch (error) {
          console.error("Failed to get client ID:", error);
          alert("Failed to login, please try again later.");
        }
      } else {
        alert("Username cannot be empty!");
      }
    },
  },
};
</script>


<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f4f8;
}

.login-form {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 300px;
}

.login-form h1 {
  margin-bottom: 1rem;
}

.login-form input {
  width: 100%;
  padding: 10px;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.login-form button {
  width: 100%;
  padding: 10px;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 5px;
  cursor: pointer;
}

.login-form button:hover {
  background-color: #0056b3;
}

.login-form p {
  margin-top: 1rem;
}

.login-form a {
  text-decoration: none;
  color: #007bff;
}

.login-form a:hover {
  text-decoration: underline;
}
</style>