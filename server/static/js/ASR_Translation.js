let recognition;
let isRecognizing = false;
let mediaRecorder;
let audioChunks = [];

// 실시간 텍스트 인식
let finalText = ""; // 최종 텍스트를 저장할 변수
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = 'ko-KR';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function(event) {
        let live_text = "";
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                finalText += event.results[i][0].transcript;
            } else {
                live_text += event.results[i][0].transcript;
            }
        }

        document.getElementById('recognizedText').innerText = live_text || finalText;
        console.log("Live text:", live_text);
        console.log("Final text:", finalText);
    };
}

async function startRecognition() {
    if (!isRecognizing && recognition) {
        finalText = "";
        recognition.start();
        isRecognizing = true;
        document.getElementById("stopButton").disabled = false;

        // 오디오 녹음 시작
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        mediaRecorder.start();

        // 번역 시작 시 스피너와 메시지 표시
        document.getElementById("p_bar_area_upload").hidden = false;
        document.getElementById("processingMessage").innerText = "번역 중입니다. 잠시만 기다려주세요...";
        document.getElementById("spinner").style.display = "inline-block";
    }
}

function stopRecognition() {
    if (isRecognizing) {
        recognition.stop();
        isRecognizing = false;
    }

    if (mediaRecorder) {
        mediaRecorder.stop();
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            sendAudioToServer(audioBlob);
            audioChunks = []; // 청크 초기화
        };
    }

    // 미디어 스트림 중지
    mediaRecorder.stream.getTracks().forEach(track => track.stop());

    if (finalText) {
        sendTextToServer(finalText);
    }
}

// 서버로 텍스트 전송 함수
function sendTextToServer(text) {
    $.ajax({
        method: 'POST',
        url: `/ASR_Translation/upload/live`,
        data: JSON.stringify({ text: text }),
        contentType: 'application/json',
        dataType: 'json',
        success: function(data) {
            console.log('Final text sent successfully:', data);
            
        },
        error: function(error) {
            console.error('Error sending final text:', error);
        }
    });
}

// 서버로 오디오 전송 함수
function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    $.ajax({
        method: 'POST',
        url: `/ASR_Translation/upload/audio`,
        data: formData,
        processData: false,
        contentType: false,
        success: function(data) {
            console.log('Audio sent successfully:', data);
            processtr(); // 번역 처리 요청
        },
        error: function(error) {
            console.error('Error sending audio:', error);
        }
    });
}

// 번역 요청 함수
function processtr(){
    $.ajax({
        method: 'POST',
        url: '/ASR_Translation/processtr',
        data: JSON.stringify({}),
        dataType: 'json',
        contentType: 'application/json',
        success: function(result){
            console.log(result);
            
            // 번역 결과 표시
            $('#translatedText').val(result['0']);
            
            // 스피너를 숨기고 "번역 완료!" 메시지 표시
            $('#spinner').hide();
            $('#processingMessage').text('번역 완료!');
            
        },
        error: function(error){
            alert('에러가 발생했습니다ㅠㅠ\n관리자에게 문의해 주세요.');
            console.log(error.status, error.statusText);
            location.href = '/ASR_Translation';
        }
    });
}

