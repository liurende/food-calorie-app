import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { TodayPage } from './pages/TodayPage';
import { CapturePage } from './pages/CapturePage';
import { ResultPage } from './pages/ResultPage';
import { HistoryPage } from './pages/HistoryPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<TodayPage />} />
          <Route path="/capture" element={<CapturePage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
