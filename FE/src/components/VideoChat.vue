<template>
  <div class="video-container">
    <button v-if="!callActive" @click="startCall">開啟視訊</button>
    <button v-if="callActive" @click="hangUp">關閉視訊</button>
    <video ref="localVideo" autoplay muted></video>
    <div class="remote-videos">
      <video
        v-for="(stream, index) in remoteStreams"
        :key="index"
        ref="remoteVideos"
        autoplay
      ></video>
    </div>
  </div>
</template>

<script>
export default {
  props: ["currentUserId"],
  data() {
    return {
      peerConnection: null,
      localStream: null,
      remoteStreams: [],
      callActive: false,
      ws: null,
    };
  },

  methods: {
    async startCall() {
      this.localStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      this.$refs.localVideo.srcObject = this.localStream;
      this.setupWebSocket();
      this.callActive = true;
    },
    hangUp() {
      // 停止本地流的所有轨道
      if (this.localStream) {
        this.localStream.getTracks().forEach((track) => track.stop());
        if (this.$refs.localVideo) {
          this.$refs.localVideo.srcObject = null;
        }
      }

      // 关闭所有的 PeerConnection
      if (this.peerConnection) {
        this.peerConnection.close();
        this.peerConnection = null;
      }

      // 清空远程流列表并清除视频元素的 srcObject
      this.remoteStreams.forEach((stream) => {
        if (stream.getTracks) {
          stream.getTracks().forEach((track) => track.stop());
        }
      });
      this.remoteStreams = [];
      this.$nextTick(() => {
        const videoElements = this.$refs.remoteVideos;
        if (videoElements) {
          videoElements.forEach((video) => (video.srcObject = null));
        }
      });

      // 标记视频聊天不再活跃
      this.callActive = false;

      // 关闭 WebSocket 连接
      if (this.ws) {
        this.ws.close();
      }
    },
    setupWebSocket() {
      this.ws = new WebSocket(
        `ws://localhost:8000/ws/webrtc/${this.currentUserId}`
      );
      this.ws.onopen = () => console.log("WebSocket connected for WebRTC");
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data);
        this.handleMessage(data);
      };
      this.ws.onerror = (error) => console.error("WebSocket error:", error);
      this.ws.onclose = () => console.log("WebSocket closed");
    },
    handleMessage(data) {
      if (data.type === "offer") {
        this.receiveOffer(data.offer, data.clientId);
      } else if (data.type === "answer") {
        this.receiveAnswer(data.answer);
      } else if (data.type === "ice_candidate") {
        this.peerConnection.addIceCandidate(
          new RTCIceCandidate(data.candidate)
        );
      }
    },
    receiveOffer(offer, clientId) {
      this.createPeerConnection();
      this.peerConnection.setRemoteDescription(
        new RTCSessionDescription(offer)
      );
      this.peerConnection.createAnswer().then((answer) => {
        this.peerConnection.setLocalDescription(answer);
        this.sendSignal("answer", { answer, clientId });
      });
    },
    receiveAnswer(answer) {
      this.peerConnection.setRemoteDescription(
        new RTCSessionDescription(answer)
      );
    },
    createPeerConnection() {
      const config = {
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
      };
      this.peerConnection = new RTCPeerConnection(config);
      this.localStream.getTracks().forEach((track) => {
        this.peerConnection.addTrack(track, this.localStream);
      });
      this.peerConnection.ontrack = (event) => {
        this.remoteStreams.push(event.streams[0]);
        this.$nextTick(() => {
          const videoElements = this.$refs.remoteVideos;
          videoElements.forEach((video, index) => {
            video.srcObject = this.remoteStreams[index];
          });
        });
      };
      this.peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          this.sendSignal("ice_candidate", { candidate: event.candidate });
        }
      };
    },
    sendSignal(type, message) {
      console.log(JSON.stringify({ type, ...message }));
      this.ws.send(JSON.stringify({ type, ...message }));
    },
  },
};
</script>

<style>
.video-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.video-container video {
  width: 300px; /* Adjust as needed */
  border: 1px solid black;
}
.remote-videos {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}
.remote-videos video {
  margin: 5px;
}
</style>
