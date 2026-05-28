import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCamera } from '../hooks/useCamera';
import { api } from '../api/client';

const ANGLE_LABELS = ['正面视图', '45° 侧面', '90° 侧面'];
const ANGLE_HINTS = [
  '正面拍摄食物\n确保完整可见',
  '从右侧约 45° 拍摄\n展示食物高度',
  '从正侧面 90° 拍摄\n展示食物厚度',
];

export function CapturePage() {
  const navigate = useNavigate();
  const { videoRef, streaming, error, startCamera, stopCamera, captureFrame } = useCamera();
  const [step, setStep] = useState(0);
  const [captured, setCaptured] = useState<string[]>([]);
  const [processing, setProcessing] = useState(false);
  const [failure, setFailure] = useState<string | null>(null);

  const handleStartCamera = async () => {
    await startCamera();
  };

  const handleCapture = () => {
    const frame = captureFrame();
    if (!frame) return;

    const newCaptured = [...captured, frame];
    setCaptured(newCaptured);

    if (step < 2) {
      setStep(step + 1);
    } else {
      stopCamera();
      processImages(newCaptured);
    }
  };

  const handleReset = () => {
    setStep(0);
    setCaptured([]);
    setProcessing(false);
    setFailure(null);
    startCamera();
  };

  const processImages = async (frames: string[]) => {
    setProcessing(true);
    try {
      const files = await Promise.all(
        frames.map(async (dataUrl, i) => {
          const res = await fetch(dataUrl);
          const blob = await res.blob();
          return new File([blob], `angle_${i}.jpg`, { type: 'image/jpeg' });
        })
      );

      const uploadResult = await api.uploadImages(files);
      const paths = uploadResult.images.map((img: { path: string }) => img.path);

      const results = await api.recognize(paths);

      navigate('/result', { state: { results, images: frames } });
    } catch (e) {
      console.error('Processing failed:', e);
      setProcessing(false);
      setFailure('识别失败，请检查网络连接后重试');
    }
  };

  // --- Camera not started yet: permission screen ---
  if (!streaming && !processing && !failure) {
    return (
      <div style={{
        background: '#F2F2F7', minHeight: '100vh', display: 'flex',
        flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        padding: 40,
      }}>
        <div style={{
          width: 72, height: 72, borderRadius: 20,
          background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          marginBottom: 24,
        }}>
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round">
            <path d="M23 7l-5 5 5 5" />
            <rect x="1" y="5" width="15" height="14" rx="3" fill="none" stroke="white" />
            <circle cx="8.5" cy="12" r="1.5" fill="white" stroke="none" />
          </svg>
        </div>
        <h2 style={{ color: '#1C1C1E', fontSize: 20, fontWeight: 600, margin: '0 0 8px' }}>
          多角度拍摄
        </h2>
        <p style={{ color: 'rgba(60,60,67,0.5)', fontSize: 14, textAlign: 'center', lineHeight: 1.5, margin: '0 0 32px' }}>
          需要拍摄 3 张食物照片<br />正面 · 斜角 · 侧面
        </p>

        {error ? (
          <div style={{ textAlign: 'center', width: '100%' }}>
            <p style={{ color: '#FF3B30', fontSize: 14, marginBottom: 16 }}>{error}</p>
            <button className="btn-primary" onClick={handleStartCamera} style={{ width: '100%' }}>
              重试
            </button>
          </div>
        ) : (
          <button className="btn-primary" onClick={handleStartCamera} style={{ width: '100%', maxWidth: 300 }}>
            打开摄像头
          </button>
        )}

        <button
          className="btn-ghost"
          onClick={() => navigate('/')}
          style={{ marginTop: 16, color: 'rgba(60,60,67,0.4)', fontSize: 15 }}
        >
          返回
        </button>
      </div>
    );
  }

  // --- Processing loading screen ---
  if (processing) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', minHeight: '100vh', padding: 40,
        background: '#F2F2F7',
      }}>
        <div style={{
          width: 60, height: 60, borderRadius: '50%',
          border: '3px solid rgba(60,60,67,0.1)',
          borderTopColor: '#007AFF',
          animation: 'spin 1s linear infinite',
          marginBottom: 24,
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        <p style={{ color: '#1C1C1E', fontSize: 17, fontWeight: 500 }}>正在分析食物...</p>
        <p style={{ color: 'rgba(60,60,67,0.5)', fontSize: 14, marginTop: 8 }}>
          估算重量与热量中
        </p>
      </div>
    );
  }

  // --- Failure screen ---
  if (failure) {
    return (
      <div style={{
        background: '#F2F2F7', minHeight: '100vh', display: 'flex',
        flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        padding: 40,
      }}>
        <div style={{
          width: 64, height: 64, borderRadius: '50%', background: 'rgba(255,59,48,0.1)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          marginBottom: 20,
        }}>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FF3B30" strokeWidth="2" strokeLinecap="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
        </div>
        <h2 style={{ color: '#1C1C1E', fontSize: 18, fontWeight: 600, margin: '0 0 6px' }}>
          识别失败
        </h2>
        <p style={{ color: 'rgba(60,60,67,0.5)', fontSize: 14, textAlign: 'center', marginBottom: 28 }}>
          {failure}
        </p>
        <button className="btn-primary" onClick={handleReset} style={{ width: '100%', maxWidth: 300 }}>
          重新拍摄
        </button>
        <button
          className="btn-ghost"
          onClick={() => navigate('/')}
          style={{ marginTop: 12, color: 'rgba(60,60,67,0.4)', fontSize: 15 }}
        >
          返回首页
        </button>
      </div>
    );
  }

  // --- Main capture UI ---
  return (
    <div style={{ background: '#F2F2F7', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Home indicator spacer */}
      <div style={{ padding: '12px 12px 0' }}>
        <div style={{
          width: 126, height: 36, borderRadius: 20, margin: '0 auto',
        }} />
      </div>

      <div className="nav-bar">
        <button className="btn-ghost" onClick={() => { stopCamera(); navigate('/'); }}>
          取消
        </button>
        <span style={{ color: '#1C1C1E', fontSize: 17, fontWeight: 600, letterSpacing: -0.2 }}>
          记录餐食
        </span>
        <span style={{ width: 50 }} />
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: 6, padding: '0 0 28px' }}>
        {[0, 1, 2].map((i) => (
          <div key={i} style={{
            width: i === step ? 28 : 4,
            height: 4,
            borderRadius: 2,
            background: i <= step ? '#1C1C1E' : 'rgba(60,60,67,0.15)',
            transition: 'all 0.3s ease',
          }} />
        ))}
      </div>

      {/* Camera viewfinder */}
      <div style={{ margin: '0 20px', flex: 1, position: 'relative' }}>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          style={{
            width: '100%', height: '100%', objectFit: 'cover',
            borderRadius: 36, border: '1px solid rgba(60,60,67,0.08)',
            background: '#000',
            display: streaming ? 'block' : 'none',
          }}
        />
        {/* Viewfinder overlay */}
        <div style={{
          position: 'absolute', inset: 0, pointerEvents: 'none', borderRadius: 36,
          overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', top: '50%', left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '60%', height: '60%',
            border: '1px solid rgba(255,255,255,0.15)', borderRadius: 20,
          }}>
            {(['tl', 'tr', 'bl', 'br'] as const).map((pos) => {
              const style: Record<string, React.CSSProperties> = {
                tl: { top: -1, left: -1, borderTop: '2px solid rgba(255,255,255,0.3)', borderLeft: '2px solid rgba(255,255,255,0.3)', borderRadius: '6px 0 0 0' },
                tr: { top: -1, right: -1, borderTop: '2px solid rgba(255,255,255,0.3)', borderRight: '2px solid rgba(255,255,255,0.3)', borderRadius: '0 6px 0 0' },
                bl: { bottom: -1, left: -1, borderBottom: '2px solid rgba(255,255,255,0.3)', borderLeft: '2px solid rgba(255,255,255,0.3)', borderRadius: '0 0 0 6px' },
                br: { bottom: -1, right: -1, borderBottom: '2px solid rgba(255,255,255,0.3)', borderRight: '2px solid rgba(255,255,255,0.3)', borderRadius: '0 0 6px 0' },
              };
              return <div key={pos} style={{ position: 'absolute', width: 20, height: 20, ...style[pos] }} />;
            })}
          </div>
          <div style={{
            position: 'absolute', bottom: 80, left: '50%', transform: 'translateX(-50%)',
            textAlign: 'center',
          }}>
            <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: 13, letterSpacing: 0.3, margin: 0 }}>
              将食物置于框线内
            </p>
            <p style={{ color: 'rgba(255,255,255,0.25)', fontSize: 12, letterSpacing: 0.3, margin: '2px 0 0' }}>
              保持手臂伸直 · 距离约 30cm
            </p>
          </div>
          <div style={{
            position: 'absolute', bottom: 24, left: '50%', transform: 'translateX(-50%)',
            background: 'rgba(30,30,32,0.8)', backdropFilter: 'blur(40px)',
            WebkitBackdropFilter: 'blur(40px)', borderRadius: 24,
            padding: '10px 24px', border: '1px solid rgba(255,255,255,0.08)',
          }}>
            <p style={{
              color: '#F5F5F7', fontSize: 14, fontWeight: 500,
              letterSpacing: -0.2, margin: 0, whiteSpace: 'nowrap',
            }}>
              {ANGLE_LABELS[step]} · 第 {step + 1} 张
            </p>
          </div>
        </div>
      </div>

      <div style={{ padding: '20px 40px 12px', textAlign: 'center' }}>
        <p style={{
          color: 'rgba(60,60,67,0.6)', fontSize: 15, fontWeight: 400,
          letterSpacing: -0.2, margin: 0, lineHeight: 1.4, whiteSpace: 'pre-line',
        }}>
          {ANGLE_HINTS[step]}
        </p>
      </div>

      {/* Shutter button */}
      <div style={{ display: 'flex', justifyContent: 'center', padding: '4px 0 20px' }}>
        <button
          onClick={handleCapture}
          style={{
            width: 72, height: 72, borderRadius: '50%', border: '3px solid rgba(60,60,67,0.15)',
            background: 'none', cursor: 'pointer', display: 'flex',
            alignItems: 'center', justifyContent: 'center', padding: 0,
          }}
        >
          <div style={{
            width: 58, height: 58, borderRadius: '50%',
            background: 'linear-gradient(180deg, #E5E5EA 0%, #C7C7CC 100%)',
          }} />
        </button>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0 32px 40px' }}>
        <div style={{ width: 40, height: 40, borderRadius: 12 }} />
        <div style={{ width: 40, height: 40, borderRadius: 12 }} />
      </div>
    </div>
  );
}
