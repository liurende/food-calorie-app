interface MacroBarProps {
  protein: number;
  carbs: number;
  fat: number;
}

export function MacroBar({ protein, carbs, fat }: MacroBarProps) {
  return (
    <div className="glass-card" style={{ padding: '20px 24px', borderRadius: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ textAlign: 'center', flex: 1 }}>
          <div style={{ width: 36, height: 4, borderRadius: 2,
            background: 'linear-gradient(90deg, #FF453A, #FF6B60)', margin: '0 auto 10px' }} />
          <p style={{ color: '#F5F5F7', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5 }}>
            {Math.round(protein)}
          </p>
          <p style={{ color: 'rgba(245,245,247,0.4)', fontSize: 12, fontWeight: 500, margin: '2px 0 0', letterSpacing: 0.3 }}>
            蛋白质 · g
          </p>
        </div>
        <div style={{ width: 1, height: 28, background: 'rgba(255,255,255,0.06)' }} />
        <div style={{ textAlign: 'center', flex: 1 }}>
          <div style={{ width: 36, height: 4, borderRadius: 2,
            background: 'linear-gradient(90deg, #30D158, #6EE790)', margin: '0 auto 10px' }} />
          <p style={{ color: '#F5F5F7', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5 }}>
            {Math.round(carbs)}
          </p>
          <p style={{ color: 'rgba(245,245,247,0.4)', fontSize: 12, fontWeight: 500, margin: '2px 0 0', letterSpacing: 0.3 }}>
            碳水 · g
          </p>
        </div>
        <div style={{ width: 1, height: 28, background: 'rgba(255,255,255,0.06)' }} />
        <div style={{ textAlign: 'center', flex: 1 }}>
          <div style={{ width: 36, height: 4, borderRadius: 2,
            background: 'linear-gradient(90deg, #0A84FF, #40A8FF)', margin: '0 auto 10px' }} />
          <p style={{ color: '#F5F5F7', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5 }}>
            {Math.round(fat)}
          </p>
          <p style={{ color: 'rgba(245,245,247,0.4)', fontSize: 12, fontWeight: 500, margin: '2px 0 0', letterSpacing: 0.3 }}>
            脂肪 · g
          </p>
        </div>
      </div>
    </div>
  );
}
