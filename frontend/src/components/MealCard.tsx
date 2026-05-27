import type { Meal, MealType } from '../types';

const mealConfig: Record<MealType, { emoji: string; label: string }> = {
  breakfast: { emoji: '🌅', label: '早餐' },
  lunch: { emoji: '☀️', label: '午餐' },
  dinner: { emoji: '🌙', label: '晚餐' },
  snack: { emoji: '🍪', label: '零食' },
};

interface MealCardProps {
  meal: Meal;
  onClick?: () => void;
}

export function MealCard({ meal, onClick }: MealCardProps) {
  const config = mealConfig[meal.meal_type] ?? { emoji: '🍽', label: meal.meal_type };
  const hasItems = meal.items.length > 0;
  const foodNames = meal.items.map((i) => i.name).join(' · ');

  return (
    <div
      className="glass-card"
      style={{
        display: 'flex', alignItems: 'center', gap: 14,
        opacity: hasItems ? 1 : 0.6, cursor: onClick ? 'pointer' : undefined,
      }}
      onClick={onClick}
    >
      <div style={{
        width: 44, height: 44, borderRadius: 12, flexShrink: 0,
        background: 'linear-gradient(135deg, rgba(255,149,0,0.15), rgba(255,149,0,0.05))',
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20,
      }}>
        {config.emoji}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{ color: '#1C1C1E', fontSize: 16, fontWeight: 500, margin: 0, letterSpacing: -0.3 }}>
          {config.label}
        </p>
        <p style={{
          color: 'rgba(60,60,67,0.5)', fontSize: 13, margin: '2px 0 0',
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>
          {hasItems ? foodNames : '还没有记录'}
        </p>
      </div>
      <span style={{
        color: hasItems ? '#1C1C1E' : 'rgba(60,60,67,0.25)',
        fontSize: 16, fontWeight: hasItems ? 500 : 400, margin: 0, letterSpacing: -0.3, flexShrink: 0,
      }}>
        {hasItems ? Math.round(meal.total_calories ?? meal.items.reduce((s, i) => s + i.calories, 0)) : '--'}
      </span>
    </div>
  );
}
