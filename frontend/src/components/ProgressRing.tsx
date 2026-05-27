export function ProgressRing({ current, target = 2000 }: { current: number; target?: number }) {
  const pct = Math.min(current / target, 1);
  const remaining = target - current;

  return (
    <div style={{
      width: 160, height: 160, borderRadius: '50%', margin: '0 auto', position: 'relative',
      background: `conic-gradient(from -90deg, #007AFF 0% ${pct * 100}%, rgba(0,122,255,0.08) ${pct * 100}% 100%)`,
    }}>
      <div style={{
        position: 'absolute', top: 8, left: 8, right: 8, bottom: 8,
        borderRadius: '50%', background: '#FFFFFF',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      }}>
        <span style={{ color: '#000000', fontSize: 34, fontWeight: 500, letterSpacing: -1, lineHeight: 1 }}>
          {current.toLocaleString()}
        </span>
        <span style={{ color: 'rgba(60,60,67,0.45)', fontSize: 13, fontWeight: 400, marginTop: 2 }}>
          剩余 {remaining} kcal
        </span>
      </div>
    </div>
  );
}
