import type { FoodItem } from '../types';

interface FoodItemCardProps {
  item: FoodItem;
  onAdjust?: (item: FoodItem) => void;
}

export function FoodItemCard({ item }: FoodItemCardProps) {
  return (
    <div className="glass-card" style={{ borderRadius: 16, padding: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ color: '#1C1C1E', fontSize: 17, fontWeight: 500, margin: 0, letterSpacing: -0.3 }}>
            {item.name}
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 6 }}>
            <span style={{ color: 'rgba(60,60,67,0.55)', fontSize: 13, fontWeight: 400 }}>
              ~{Math.round(item.weight_g)}g
            </span>
            {item.confidence != null && (
              <>
                <span style={{ width: 3, height: 3, borderRadius: '50%', background: 'rgba(60,60,67,0.2)' }} />
                <span style={{ color: 'rgba(60,60,67,0.55)', fontSize: 13 }}>
                  置信度 {Math.round(item.confidence * 100)}%
                </span>
              </>
            )}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <p style={{ color: '#1C1C1E', fontSize: 20, fontWeight: 400, margin: 0, letterSpacing: -0.5 }}>
            {Math.round(item.calories)}
          </p>
          <p style={{ color: 'rgba(60,60,67,0.45)', fontSize: 13, fontWeight: 400, margin: '2px 0 0' }}>
            千卡
          </p>
        </div>
      </div>
    </div>
  );
}
