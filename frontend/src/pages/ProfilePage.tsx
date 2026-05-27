import { useState, useEffect } from 'react';
import { TabBar } from '../components/TabBar';
import { api } from '../api/client';
import type { UserProfile, ActivityLevel } from '../types';

const CURRENT_USER = 'default_user';

const ACTIVITY_LABELS: Record<ActivityLevel, string> = {
  sedentary: '久坐不动',
  light: '轻度活动 (1-2天/周)',
  moderate: '中度活动 (3-5天/周)',
  active: '高度活跃 (6-7天/周)',
  very_active: '极高活跃 (高强度训练)',
};

const GENDER_LABELS: Record<string, string> = {
  male: '男',
  female: '女',
};

export function ProfilePage() {
  const [bmr, setBmr] = useState<number | null>(null);
  const [tdee, setTdee] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    name: '',
    gender: '',
    age: '' as string | number,
    height_cm: '' as string | number,
    weight_kg: '' as string | number,
    activity_level: 'moderate' as ActivityLevel,
  });

  useEffect(() => {
    api.getProfile(CURRENT_USER)
      .then((data) => {
        if (data.profile) {
          setBmr(data.bmr);
          setTdee(data.tdee);
          setForm({
            name: data.profile.name || '',
            gender: data.profile.gender || '',
            age: data.profile.age ?? '',
            height_cm: data.profile.height_cm ?? '',
            weight_kg: data.profile.weight_kg ?? '',
            activity_level: (data.profile.activity_level as ActivityLevel) || 'moderate',
          });
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload: UserProfile = {
        user_id: CURRENT_USER,
        name: form.name,
        gender: form.gender,
        age: form.age === '' ? null : Number(form.age),
        height_cm: form.height_cm === '' ? null : Number(form.height_cm),
        weight_kg: form.weight_kg === '' ? null : Number(form.weight_kg),
        activity_level: form.activity_level,
      };
      const result = await api.updateProfile(payload);
      setBmr(result.bmr);
      setTdee(result.tdee);
    } catch (e) {
      console.error('Save failed:', e);
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const hasAllStats = form.gender && form.age && form.height_cm && form.weight_kg;

  return (
    <div className="fade-in" style={{ paddingBottom: 24 }}>
      <div style={{ padding: '40px 24px 6px' }}>
        <p className="title-section">个人设置</p>
        <h1 className="title-large" style={{ marginTop: 2 }}>我的</h1>
      </div>

      {/* BMR / TDEE Card */}
      {hasAllStats && bmr && tdee && (
        <div style={{ padding: '0 20px 16px' }}>
          <div className="glass-card" style={{ borderRadius: 20, padding: '20px 24px' }}>
            <p style={{ color: 'rgba(60,60,67,0.6)', fontSize: 13, margin: 0, marginBottom: 12 }}>
              每日能量需求
            </p>
            <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center' }}>
              <div>
                <p style={{ color: 'rgba(60,60,67,0.45)', fontSize: 11, margin: '0 0 4px' }}>基础代谢</p>
                <p style={{ color: '#1C1C1E', fontSize: 28, fontWeight: 500, margin: 0, letterSpacing: -1 }}>
                  {bmr}
                </p>
                <p style={{ color: 'rgba(60,60,67,0.45)', fontSize: 11, margin: '2px 0 0' }}>BMR · 千卡</p>
              </div>
              <div style={{ width: 1, background: 'rgba(60,60,67,0.08)', borderRadius: 1 }} />
              <div>
                <p style={{ color: 'rgba(60,60,67,0.45)', fontSize: 11, margin: '0 0 4px' }}>每日消耗</p>
                <p style={{ color: '#007AFF', fontSize: 28, fontWeight: 500, margin: 0, letterSpacing: -1 }}>
                  {tdee}
                </p>
                <p style={{ color: 'rgba(60,60,67,0.45)', fontSize: 11, margin: '2px 0 0' }}>TDEE · 千卡</p>
              </div>
            </div>
            <div style={{
              marginTop: 14, padding: '10px 14px', borderRadius: 10,
              background: 'rgba(0,122,255,0.06)', border: '1px solid rgba(0,122,255,0.1)',
            }}>
              <p style={{ color: 'rgba(60,60,67,0.6)', fontSize: 12, margin: 0, lineHeight: 1.5 }}>
                减脂建议摄入: <span style={{ color: '#1C1C1E', fontWeight: 500 }}>{Math.round(tdee * 0.8)} kcal</span>
                &nbsp;·&nbsp;
                维持体重: <span style={{ color: '#1C1C1E', fontWeight: 500 }}>{tdee} kcal</span>
                &nbsp;·&nbsp;
                增肌建议摄入: <span style={{ color: '#1C1C1E', fontWeight: 500 }}>{Math.round(tdee * 1.1)} kcal</span>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Form */}
      {!loading && (
        <div style={{ padding: '0 20px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          <p className="card-label" style={{ padding: '0 4px 4px' }}>身体数据</p>

          {/* Name */}
          <div className="glass-card" style={{ borderRadius: 16, padding: '12px 16px' }}>
            <p style={{ color: 'rgba(60,60,67,0.55)', fontSize: 12, marginBottom: 6 }}>昵称</p>
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="你的名字"
              style={{
                width: '100%', background: 'none', border: 'none', color: '#1C1C1E',
                fontSize: 16, outline: 'none', fontFamily: 'inherit',
              }}
            />
          </div>

          {/* Gender */}
          <div className="glass-card" style={{ borderRadius: 16, padding: '12px 16px' }}>
            <p style={{ color: 'rgba(60,60,67,0.55)', fontSize: 12, marginBottom: 6 }}>性别</p>
            <div style={{ display: 'flex', gap: 8 }}>
              {['male', 'female'].map((g) => (
                <button
                  key={g}
                  onClick={() => setForm({ ...form, gender: g })}
                  style={{
                    flex: 1, padding: '10px 0', borderRadius: 12, border: 'none',
                    cursor: 'pointer', fontFamily: 'inherit', fontSize: 15, fontWeight: 500,
                    background: form.gender === g
                      ? 'rgba(0,122,255,0.1)'
                      : 'rgba(60,60,67,0.04)',
                    color: form.gender === g ? '#007AFF' : 'rgba(60,60,67,0.35)',
                  }}
                >
                  {GENDER_LABELS[g]}
                </button>
              ))}
            </div>
          </div>

          {/* Age, Height, Weight */}
          <div style={{ display: 'flex', gap: 8 }}>
            {[
              { key: 'age', label: '年龄', unit: '岁', placeholder: '25', min: 1, max: 150 },
              { key: 'height_cm', label: '身高', unit: 'cm', placeholder: '170', min: 30, max: 300 },
              { key: 'weight_kg', label: '体重', unit: 'kg', placeholder: '65', min: 1, max: 500 },
            ].map((field) => (
              <div key={field.key} className="glass-card" style={{ borderRadius: 16, padding: '12px 14px', flex: 1 }}>
                <p style={{ color: 'rgba(60,60,67,0.55)', fontSize: 12, marginBottom: 4 }}>{field.label}</p>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 3 }}>
                  <input
                    type="number"
                    min={field.min}
                    max={field.max}
                    value={form[field.key as keyof typeof form] as string | number}
                    onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                    placeholder={field.placeholder}
                    style={{
                      width: '100%', background: 'none', border: 'none', color: '#1C1C1E',
                      fontSize: 20, fontWeight: 500, outline: 'none', fontFamily: 'inherit',
                      letterSpacing: -0.5, MozAppearance: 'textfield',
                    }}
                  />
                  <span style={{ color: 'rgba(60,60,67,0.35)', fontSize: 12, flexShrink: 0 }}>{field.unit}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Activity Level */}
          <div className="glass-card" style={{ borderRadius: 16, padding: '12px 16px' }}>
            <p style={{ color: 'rgba(60,60,67,0.55)', fontSize: 12, marginBottom: 8 }}>活动水平</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {(Object.keys(ACTIVITY_LABELS) as ActivityLevel[]).map((level) => (
                <button
                  key={level}
                  onClick={() => setForm({ ...form, activity_level: level })}
                  style={{
                    width: '100%', padding: '8px 12px', borderRadius: 10, border: 'none',
                    cursor: 'pointer', fontFamily: 'inherit', fontSize: 14, textAlign: 'left',
                    background: form.activity_level === level
                      ? 'rgba(0,122,255,0.08)'
                      : 'transparent',
                    color: form.activity_level === level ? '#007AFF' : 'rgba(60,60,67,0.45)',
                    fontWeight: form.activity_level === level ? 500 : 400,
                  }}
                >
                  {ACTIVITY_LABELS[level]}
                </button>
              ))}
            </div>
          </div>

          {/* Save Button */}
          <div style={{ paddingTop: 8 }}>
            <button
              className="btn-primary"
              onClick={handleSave}
              disabled={saving}
              style={{ opacity: saving ? 0.6 : 1 }}
            >
              {saving ? '保存中...' : '保存设置'}
            </button>
          </div>
        </div>
      )}

      <TabBar />
    </div>
  );
}
