import { useState, useEffect } from 'react';
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
  const { videoRef, streaming, startCamera, stopCamera, captureFrame } = useCamera();
  const [step, setStep] = useState(0);
  const [captured, setCaptured] = useState<string[]>([]);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

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
      alert('识别失败，请重试');
    } finally {
      setProcessing(false);
    }
  };

  if (processing) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', minHeight: '100vh', padding: 40,
      }}>
        <div style={{
          width: 60, height: 60, borderRadius: '50%',
          border: '3px solid rgba(255,255,255,0.1)',
          borderTopColor: '#F5F5F7',
          animation: 'spin 1s linear infinite',
          marginBottom: 24,
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        <p style={{ color: '#F5F5F7', fontSize: 17, fontWeight: 500 }}>正在分析食物...</p>
        <p style={{ color: 'rgba(245,245,247,0.4)', fontSize: 14, marginTop: 8 }}>
          估算重量与热量中
        </p>
      </div>
    );
  }

  return (
    <div style={{ background: '#000', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '12px 12px 0' }}>
        <div style={{
          width: 126, height: 36, background: '#000', borderRadius: 20, margin: '0 auto',
        }} />
      </div>

      <div className="nav-bar">
        <button className="btn-ghost" onClick={() => { stopCamera(); navigate('/'); }}>
          取消
        </button>
        <span style={{ color: '#F5F5F7', fontSize: 17, fontWeight: 600, letterSpacing: -0.2 }}>
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
            background: i <= step ? '#F5F5F7' : 'rgba(245,245,247,0.2)',
            transition: 'all 0.3s ease',
          }} />
        ))}
      </div>

      <div style={{ margin: '0 20px', flex: 1, position: 'relative' }}>
        {streaming && (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{
              width: '100%', height: '100%', objectFit: 'cover',
              borderRadius: 36, border: '1px solid rgba(255,255,255,0.08)',
            }}
          />
        )}
        {/* Viewfinder overlay */}
        <div style={{
          position: 'absolute', inset: 0, pointerEvents: 'none', borderRadius: 36,
          overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', top: '50%', left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '60%', height: '60%',
            border: '1px solid rgba(255,255,255,0.12)', borderRadius: 20,
          }}>
            {(['tl', 'tr', 'bl', 'br'] as const).map((pos) => {
              const style: Record<string, React.CSSProperties> = {
                tl: { top: -1, left: -1, borderTop: '2px solid rgba(255,255,255,0.25)', borderLeft: '2px solid rgba(255,255,255,0.25)', borderRadius: '6px 0 0 0' },
                tr: { top: -1, right: -1, borderTop: '2px solid rgba(255,255,255,0.25)', borderRight: '2px solid rgba(255,255,255,0.25)', borderRadius: '0 6px 0 0' },
                bl: { bottom: -1, left: -1, borderBottom: '2px solid rgba(255,255,255,0.25)', borderLeft: '2px solid rgba(255,255,255,0.25)', borderRadius: '0 0 0 6px' },
                br: { bottom: -1, right: -1, borderBottom: '2px solid rgba(255,255,255,0.25)', borderRight: '2px solid rgba(255,255,255,0.25)', borderRadius: '0 0 6px 0' },
              };
              return <div key={pos} style={{ position: 'absolute', width: 20, height: 20, ...style[pos] }} />;
            })}
          </div>
          <div style={{
            position: 'absolute', bottom: 80, left: '50%', transform: 'translateX(-50%)',
            textAlign: 'center',
          }}>
            <p style={{ color: 'rgba(255,255,255,0.28)', fontSize: 13, letterSpacing: 0.3, margin: 0 }}>
              将食物置于框线内
            </p>
            <p style={{ color: 'rgba(255,255,255,0.16)', fontSize: 12, letterSpacing: 0.3, margin: '2px 0 0' }}>
              保持手臂伸直 · 距离约 30cm
            </p>
          </div>
          <div style={{
            position: 'absolute', bottom: 24, left: '50%', transform: 'translateX(-50%)',
            background: 'rgba(30,30,32,0.8)', backdropFilter: 'blur(40px)',
            WebkitBackdropFilter: 'blur(40px)', borderRadius: 24,
            padding: '10px 24px', border: '1px solid rgba(255,255,255,0.06)',
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
          color: 'rgba(245,245,247,0.45)', fontSize: 15, fontWeight: 400,
          letterSpacing: -0.2, margin: 0, lineHeight: 1.4, whiteSpace: 'pre-line',
        }}>
          {ANGLE_HINTS[step]}
        </p>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', padding: '4px 0 20px' }}>
        <button
          onClick={handleCapture}
          style={{
            width: 72, height: 72, borderRadius: '50%', border: '3px solid rgba(245,245,247,0.2)',
            background: 'none', cursor: 'pointer', display: 'flex',
            alignItems: 'center', justifyContent: 'center', padding: 0,
          }}
        >
          <div style={{
            width: 58, height: 58, borderRadius: '50%',
            background: 'linear-gradient(180deg, #F5F5F7 0%, #D1D1D6 100%)',
          }} />
        </button>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0 32px 40px' }}>
        <div style={{ width: 40, height: 40, borderRadius: 12, background: 'rgba(255,255,255,0.08)' }} />
        <div style={{ width: 40, height: 40, borderRadius: 12, background: 'rgba(255,255,255,0.08)' }} />
      </div>
    </div>
  );
}
