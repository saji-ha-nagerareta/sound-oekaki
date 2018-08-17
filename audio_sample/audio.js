$("document").ready(function () {
  const start = document.getElementById('start');
  const stop = document.getElementById('stop');
  const canvas = document.getElementById('canvas');
  const drawContext = canvas.getContext('2d');
  const player = document.getElementById('player');

  let mediaRecorder = null;
  let mediaStream = null;

  start.addEventListener('click', () => {
    start.disabled = true;
    stop.disabled = false;

    const chunks = [];
    mediaRecorder = new MediaRecorder(mediaStream, {
      mimeType: 'audio/webm'
    });

    mediaRecorder.addEventListener('dataavailable', e => {
      if (e.data.size > 0) {
        chunks.push(e.data);
      }
    });

    mediaRecorder.addEventListener('stop', () => {
      const a = document.createElement('a');
      var audioFile = new Blob(chunks);
      a.href = URL.createObjectURL(audioFile);
      player.src = URL.createObjectURL(audioFile);
      a.download = 'test.webm';
      a.click();
      // send data to server
      $.ajax({
        type: "POST",
        url: "http://127.0.0.1:8888/pen", // set url
        data: audioFile,
        processData: false
      });
    });

    mediaRecorder.start();
  });

  stop.addEventListener('click', () => {
    if (mediaRecorder === null) {
      return;
    }
    start.disabled = false;
    stop.disabled = true;

    mediaRecorder.stop();
    mediaRecorder = null;
  });

  navigator.mediaDevices.getUserMedia({
    audio: true,
    video: false
  }).then(stream => {
    mediaStream = stream;
    const audioContext = new AudioContext();
    const sourceNode = audioContext.createMediaStreamSource(stream);
    const analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 2048;
    sourceNode.connect(analyserNode);

    function draw() {
      const barWidth = canvas.width / analyserNode.fftSize;
      const array = new Uint8Array(analyserNode.fftSize);
      analyserNode.getByteTimeDomainData(array);
      drawContext.fillStyle = 'rgba(0, 0, 0, 1)';
      drawContext.fillRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < analyserNode.fftSize; ++i) {
        const value = array[i];
        const percent = value / 255;
        const height = canvas.height * percent;
        const offset = canvas.height - height;

        drawContext.fillStyle = 'lime';
        drawContext.fillRect(i * barWidth, offset, barWidth, 2);
      }

      requestAnimationFrame(draw);
    }

    draw();
  }).catch(error => {
    console.log(error);
  });
});
