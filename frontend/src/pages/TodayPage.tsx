import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { TabBar } from '../components/TabBar';
import { ProgressRing } from '../components/ProgressRing';
import { MealCard } from '../components/MealCard';
import type { Meal, StatsData } from '../types';

const CURRENT_USER = 'default_user';
const DEFAULT_TARGET = 2000;

export function TodayPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<StatsData | null>(null);
  const [calorieTarget, setCalorieTarget] = useState(DEFAULT_TARGET);
  const [loading, setLoading] = useState(true);

  const today = new Date().toISOString().slice(0, 10);

  useEffect(() => {
    Promise.all([
      api.getStats(CURRENT_USER, 'daily', today),
      api.getProfile(CURRENT_USER),
    ])
      .then(([statsData, profileData]) => {
        setStats(statsData);
        if (profileData.tdee) {
          setCalorieTarget(profileData.tdee);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const mealSlots: Array<{ type: 'breakfast' | 'lunch' | 'dinner' | 'snack'; meals: Meal[] }> = [
    { type: 'breakfast', meals: stats?.meals.filter((m) => m.meal_type === 'breakfast') ?? [] },
    { type: 'lunch', meals: stats?.meals.filter((m) => m.meal_type === 'lunch') ?? [] },
    { type: 'dinner', meals: stats?.meals.filter((m) => m.meal_type === 'dinner') ?? [] },
    { type: 'snack', meals: stats?.meals.filter((m) => m.meal_type === 'snack') ?? [] },
  ];

  const now = new Date();
  const weekDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][now.getDay()];
  const dateStr = `${now.getMonth() + 1}月${now.getDate()}日 · ${weekDay}`;

  return (
    <div className="fade-in" style={{ paddingBottom: 24 }}>
      <div style={{ padding: '40px 24px 6px' }}>
        <p className="title-section">{dateStr}</p>
        <h1 className="title-large" style={{ marginTop: 2 }}>今天</h1>
      </div>

      <div style={{ textAlign: 'center', padding: '8px 0 24px' }}>
        <ProgressRing
          current={stats?.total_calories ?? 0}
          target={calorieTarget}
        />
      </div>

      <div style={{ padding: '0 20px', display: 'flex', flexDirection: 'column', gap: 6 }}>
        {!loading && <p className="card-label" style={{ padding: '0 4px 4px' }}>餐食记录</p>}

        {mealSlots.map(({ type, meals }) => {
          if (meals.length > 0) {
            return meals.map((meal) => (
              <MealCard key={meal.id} meal={meal} />
            ));
          }
          return (
            <div
              key={type}
              className="glass-card"
              style={{
                display: 'flex', alignItems: 'center', gap: 14, opacity: 0.4,
              }}
            >
              <div style={{
                width: 44, height: 44, borderRadius: 12, flexShrink: 0,
                background: 'rgba(255,255,255,0.03)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20,
              }}>
                {{ breakfast: '🌅', lunch: '☀️', dinner: '🌙', snack: '🍪' }[type]}
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ color: '#F5F5F7', fontSize: 16, fontWeight: 500, margin: 0 }}>
                  {{ breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '零食' }[type]}
                </p>
                <p style={{ color: 'rgba(245,245,247,0.2)', fontSize: 13, margin: '2px 0 0' }}>
                  还没有记录
                </p>
              </div>
              <span style={{ color: 'rgba(245,245,247,0.2)', fontSize: 16 }}>--</span>
            </div>
          );
        })}
      </div>

      <div style={{ padding: '20px 20px 8px' }}>
        <button className="btn-primary" onClick={() => navigate('/capture')}>
          📷  拍照记录餐食
        </button>
      </div>

      <TabBar />
    </div>
  );
}
