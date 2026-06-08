import { Routes, Route, Navigate } from "react-router-dom";
import Landing from "./pages/Landing";
import AppShell from "./pages/AppShell";
import Recognize from "./pages/Recognize";
import Practice from "./pages/Practice";
import Dictionary from "./pages/Dictionary";
import History from "./pages/History";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/app" element={<AppShell />}>
        <Route index element={<Navigate to="recognize" replace />} />
        <Route path="recognize" element={<Recognize />} />
        <Route path="practice" element={<Practice />} />
        <Route path="dictionary" element={<Dictionary />} />
        <Route path="history" element={<History />} />
      </Route>
    </Routes>
  );
}
