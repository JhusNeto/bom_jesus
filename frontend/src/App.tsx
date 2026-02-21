import { Navigate, Route, Routes } from 'react-router-dom';
import { AppLayout } from './components/app-layout';
import { PrivateRoute } from './components/private-route';
import { AdminPage } from './pages/admin-page';
import { ChecklistPage } from './pages/checklist-page';
import { DashboardPage } from './pages/dashboard-page';
import { HelpGuidePage } from './pages/help-guide-page';
import { HelpPage } from './pages/help-page';
import { HistoryPage } from './pages/history-page';
import { HomePage } from './pages/home-page';
import { LoginPage } from './pages/login-page';
import { LossPage } from './pages/loss-page';
import { LotEntryPage } from './pages/lot-entry-page';
import { LotMovePage } from './pages/lot-move-page';
import { ReturnPage } from './pages/return-page';
import { useSyncQueue } from './sync/use-sync-queue';

function App() {
  useSyncQueue();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <AppLayout />
          </PrivateRoute>
        }
      >
        <Route index element={<HomePage />} />
        <Route path="entry" element={<LotEntryPage />} />
        <Route path="move" element={<LotMovePage />} />
        <Route path="loss" element={<LossPage />} />
        <Route path="return" element={<ReturnPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="history" element={<HistoryPage />} />
        <Route path="help" element={<HelpPage />} />
        <Route path="help/:slug" element={<HelpGuidePage />} />
        <Route path="checklist" element={<ChecklistPage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
