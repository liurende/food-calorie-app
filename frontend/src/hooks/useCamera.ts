import { useState, useRef, useCallback, useEffect } from 'react';

export function useCamera() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Attach stream to video element once it mounts in the DOM
  useEffect(() => {
    if (streaming && streamRef.current && videoRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch(console.error);
    }
  }, [streaming]);

  const startCamera = useCallback(async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1080 }, height: { ideal: 1440 } },
        audio: false,
      });
      streamRef.current = stream;
      setStreaming(true);
    } catch (e) {
      console.error('Camera access denied:', e);
      setError('无法访问摄像头，请检查权限设置');
    }
  }, []);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setStreaming(false);
    setError(null);
  }, []);

  const captureFrame = useCallback((): string | null => {
    if (!videoRef.current) return null;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;
    ctx.drawImage(videoRef.current, 0, 0);
    return canvas.toDataURL('image/jpeg', 0.9);
  }, []);

  return { videoRef, streaming, error, startCamera, stopCamera, captureFrame };
}
