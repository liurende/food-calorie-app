import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FoodItemCard } from '../components/FoodItemCard';
import { MacroBar } from '../components/MacroBar';
import { api } from '../api/client';
import type { RecognizeResult, FoodItem, MealType } from '../types';

interface LocationState {
  results: RecognizeResult[];
  images: string[];
}

export function ResultPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [results] = useState<RecognizeResult[]>(state?.results ?? []);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  if (!state || results.length === 0) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <p style={{ color: 'rgba(60,60,67,0.55)' }}>没有识别结果</p>
        <button className="btn-primary" onClick={() => navigate('/capture')} style={{ marginTop: 16 }}>
          去拍照
        </button>
      </div>
    );
  }

  const totalCal = results.reduce((s, r) => s + r.calories, 0);
  const totalProtein = results.reduce((s, r) => s + (r.protein_g ?? 0), 0);
  const totalCarbs = results.reduce((s, r) => s + (r.carbs_g ?? 0), 0);
  const totalFat = results.reduce((s, r) => s + (r.fat_g ?? 0), 0);

  const handleSave = async () => {
    setSaving(true);
    try {
      const items: FoodItem[] = results.map((r) => ({
        name: r.name,
        weight_g: r.weight_g,
        calories: r.calories,
        protein_g: r.protein_g,
        carbs_g: r.carbs_g,
        fat_g: r.fat_g,
        confidence: r.confidence,
      }));

      await api.createMeal({
        user_id: 'default_user',
        meal_type: (new Date().getHours() < 11 ? 'breakfast'
          : new Date().getHours() < 15 ? 'lunch' : 'dinner') as MealType,
        total_calories: totalCal,
        items,
      });
      setSaved(true);
      setTimeout(() => navigate('/'), 500);
    } catch (e) {
      console.error('Save failed:', e);
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fade-in" style={{ paddingBottom: 24 }}>
      <div className="nav-bar">
        <button className="btn-ghost" onClick={() => navigate('/capture')}>
          ← 返回
        </button>
        <span style={{ color: '#1C1C1E', fontSize: 17, fontWeight: 600 }}>分析结果</span>
        <button
          className="btn-ghost"
          onClick={handleSave}
          disabled={saving || saved}
          style={{ opacity: saved ? 0.4 : 1 }}
        >
          {saved ? '已保存' : '保存'}
        </button>
      </div>

      <div style={{ textAlign: 'center', padding: '8px 0 32px' }}>
        <p style={{ color: 'rgba(60,60,67,0.6)', fontSize: 15, margin: 0 }}>预估总热量</p>
        <p style={{
          color: '#000000', fontSize: 80, fontWeight: 200, margin: 0,
          letterSpacing: -3, lineHeight: 1,
        }}>
          {Math.round(totalCal)}
        </p>
        <p style={{ color: 'rgba(60,60,67,0.45)', fontSize: 18, margin: '4px 0 0', letterSpacing: 0.5 }}>
          千卡
        </p>
      </div>

      <div style={{ padding: '0 20px', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 4px 4px' }}>
          <span className="card-label">识别食物</span>
          <span style={{ color: 'rgba(60,60,67,0.35)', fontSize: 12 }}>
            基于 {state?.images?.length ?? 0} 张照片
          </span>
        </div>

        {results.map((item, i) => (
          <FoodItemCard
            key={i}
            item={{ name: item.name, weight_g: item.weight_g, calories: item.calories,
              protein_g: item.protein_g, carbs_g: item.carbs_g, fat_g: item.fat_g,
              confidence: item.confidence }}
          />
        ))}
      </div>

      <div style={{ padding: '24px 20px 16px' }}>
        <MacroBar protein={totalProtein} carbs={totalCarbs} fat={totalFat} />
      </div>

      <div style={{ padding: '4px 20px' }}>
        <button
          onClick={handleSave}
          disabled={saving || saved}
          className="btn-primary"
          style={{ opacity: saved ? 0.5 : 1 }}
        >
          {saving ? '保存中...' : saved ? '已保存 ✓' : '保存记录'}
        </button>
      </div>
    </div>
  );
}
