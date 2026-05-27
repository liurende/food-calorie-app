import { useState, useEffect } from 'react';
import { TabBar } from '../components/TabBar';
import { MealCard } from '../components/MealCard';
import { api } from '../api/client';
import type { StatsData } from '../types';

const CURRENT_USER = 'default_user';

export function HistoryPage() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().slice(0, 10));
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getStats(CURRENT_USER, 'daily', selectedDate)
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedDate]);

  const allMeals = stats?.meals ?? [];

  const weekDates = Array.from({ length: 7 }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - d.getDay() + i);
    return d.toISOString().slice(0, 10);
  });

  const dayLabels = ['日', '一', '二', '三', '四', '五', '六'];

  return (
    <div className="fade-in" style={{ paddingBottom: 24 }}>
      <div style={{ padding: '40px 24px 6px' }}>
        <p className="title-section">
          {new Date(selectedDate).getMonth() + 1}月{new Date(selectedDate).getDate()}日
        </p>
        <h1 className="title-large" style={{ marginTop: 2 }}>历史记录</h1>
      </div>

      <div style={{
        display: 'flex', gap: 4, padding: '16px 20px', overflowX: 'auto',
      }}>
        {weekDates.map((d, i) => {
          const dateObj = new Date(d);
          const isSelected = d === selectedDate;
          const hasData = isSelected && allMeals.length > 0;

          return (
            <button
              key={d}
              onClick={() => setSelectedDate(d)}
              style={{
                flex: '1 0 auto', minWidth: 44, padding: '10px 4px',
                borderRadius: 14, border: 'none', cursor: 'pointer',
                background: isSelected
                  ? 'rgba(0,122,255,0.1)'
                  : 'transparent',
                color: isSelected ? '#007AFF' : 'rgba(60,60,67,0.4)',
                fontFamily: 'inherit',
              }}
            >
              <div style={{ fontSize: 11, fontWeight: 500, marginBottom: 4 }}>
                {dayLabels[i]}
              </div>
              <div style={{ fontSize: 16, fontWeight: isSelected ? 600 : 400, position: 'relative' }}>
                {dateObj.getDate()}
                {hasData && (
                  <span style={{
                    display: 'block', width: 4, height: 4, borderRadius: '50%',
                    background: '#FF9500', margin: '4px auto 0',
                  }} />
                )}
              </div>
            </button>
          );
        })}
      </div>

      {stats && (
        <div style={{ padding: '0 20px 8px' }}>
          <div className="glass-card" style={{ borderRadius: 16, padding: '16px 20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center' }}>
              <div>
                <p style={{
                  color: '#1C1C1E', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5,
                }}>
                  {Math.round(stats.total_calories)}
                </p>
                <p style={{ color: 'rgba(60,60,67,0.55)', fontSize: 12, margin: '2px 0 0' }}>千卡</p>
              </div>
              <div style={{ width: 1, background: 'rgba(60,60,67,0.08)' }} />
              <div>
                <p style={{
                  color: '#1C1C1E', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5,
                }}>
                  {Math.round(stats.total_protein)}
                </p>
                <p style={{ color: 'rgba(60,60,67,0.55)', fontSize: 12, margin: '2px 0 0' }}>蛋白质 g</p>
              </div>
              <div style={{ width: 1, background: 'rgba(60,60,67,0.08)' }} />
              <div>
                <p style={{
                  color: '#1C1C1E', fontSize: 22, fontWeight: 500, margin: 0, letterSpacing: -0.5,
                }}>
                  {allMeals.length}
                </p>
                <p style={{ color: 'rgba(60,60,67,0.55)', fontSize: 12, margin: '2px 0 0' }}>餐次</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div style={{ padding: '0 20px', display: 'flex', flexDirection: 'column', gap: 6, marginTop: 8 }}>
        {loading ? (
          <p style={{ textAlign: 'center', color: 'rgba(60,60,67,0.35)', padding: 40 }}>加载中...</p>
        ) : allMeals.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <p style={{ fontSize: 40, margin: '0 0 12px' }}>🍽</p>
            <p style={{ color: 'rgba(60,60,67,0.4)', fontSize: 15 }}>当天没有记录</p>
          </div>
        ) : (
          allMeals.map((meal) => <MealCard key={meal.id} meal={meal} />)
        )}
      </div>

      <TabBar />
    </div>
  );
}
