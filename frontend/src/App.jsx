import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Mic, Square, Loader, Play, Radio } from 'lucide-react';
import './App.css';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [hasGreeted, setHasGreeted] = useState(false);
  const [status, setStatus] = useState("Ready to Start");
  const [aiSpeaking, setAiSpeaking] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    document.title = "Loop AI Assistant";
  }, []);

  const handleStartConversation = async () => {
    setIsLoading(true);
    setStatus("Connecting...");
    
    try {
      const response = await axios.get('http://localhost:5000/greet', {
        responseType: 'blob',
      });
      playAudio(response.data, "Loop AI is introducing itself...");
      setHasGreeted(true);
    } catch (error) {
      console.error("Greeting failed:", error);
      setStatus("Connection Failed. Is Backend Running?");
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = handleStop;
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setStatus("Listening...");
    } catch (err) {
      console.error("Mic Error:", err);
      setStatus("Microphone Access Denied");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setStatus("Thinking...");
    }
  };

  const handleStop = async () => {
    setIsLoading(true);
    const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm;codecs=opus' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
      const response = await axios.post('http://localhost:5000/chat-voice', formData, {
        responseType: 'blob',
      });
      playAudio(response.data, "Loop AI Speaking...");
    } catch (error) {
      console.error("Error:", error);
      setStatus("Error. Try again.");
      setIsLoading(false);
    }
  };

  const playAudio = (blob, statusText) => {
    const audioUrl = URL.createObjectURL(blob);
    const audio = new Audio(audioUrl);
    setStatus(statusText);
    setAiSpeaking(true);
    audio.play();
    
    audio.onended = () => {
      setStatus("Tap Mic to Reply");
      setIsLoading(false);
      setAiSpeaking(false);
    };
  };

  return (
    <div className="app-container">
      <div className="glass-card">
        {/* Header Section */}
        <div className="header">
          <div className="logo-icon">
            <Radio size={24} color="white" />
          </div>
          <h1>Loop AI Hospital Network Assistant</h1>
        </div>

        {/* Status Pill */}
        <div className={`status-pill ${isRecording ? 'recording' : ''} ${aiSpeaking ? 'speaking' : ''}`}>
          <span className="status-dot"></span>
          {status}
        </div>

        {/* Main Action Button */}
        <div className="controls">
          {!hasGreeted ? (
            <button 
              className={`action-button start-btn ${isLoading ? 'loading' : ''}`}
              onClick={handleStartConversation}
              disabled={isLoading}
            >
              {isLoading ? <Loader className="icon spin" /> : <Play className="icon fill-icon" />}
            </button>
          ) : (
            <div className="mic-wrapper">
              {/* Animated Rings behind the mic */}
              {isRecording && <div className="pulse-ring"></div>}
              
              <button 
                className={`action-button mic-btn ${isRecording ? 'active' : ''} ${isLoading ? 'loading' : ''}`}
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isLoading}
              >
                {isLoading ? <Loader className="icon spin" /> : 
                 isRecording ? <Square className="icon" /> : 
                 <Mic className="icon" />}
              </button>
            </div>
          )}
        </div>

        {/* Footer Instruction */}
        <p className="instruction">
          {!hasGreeted 
            ? "Tap Play to Connect" 
            : isRecording 
              ? "Tap to Finish Speaking" 
              : "Tap Microphone to Speak"}
        </p>
      </div>
    </div>
  );
}

export default App;