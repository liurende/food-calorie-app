import { useNavigate, useLocation } from 'react-router-dom';

const tabs = [
  { path: '/', icon: '📊', label: '摘要' },
  { path: '/capture', icon: '📷', label: '拍照' },
  { path: '/history', icon: '📅', label: '历史' },
];

export function TabBar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="tab-bar">
      {tabs.map((t) => {
        const active = (t.path === '/' && location.pathname === '/') ||
          (t.path !== '/' && location.pathname.startsWith(t.path));
        return (
          <div
            key={t.path}
            className={`tab-item ${active ? 'active' : 'inactive'}`}
            onClick={() => navigate(t.path)}
          >
            <span className="icon">{t.icon}</span>
            <span className="label">{t.label}</span>
          </div>
        );
      })}
    </div>
  );
}
