import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import Companies from "./pages/Companies";
import InterviewSetup from "./pages/InterviewSetup";
import InterviewLive from "./pages/InterviewLive";
import InterviewReport from "./pages/InterviewReport";
import Learning from "./pages/Learning";
import Resume from "./pages/Resume";
import History from "./pages/History";

export default function App() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/companies" element={<Companies />} />
        <Route path="/interview/setup" element={<InterviewSetup />} />
        <Route path="/interview/live" element={<InterviewLive />} />
        <Route path="/interview/report" element={<InterviewReport />} />
        <Route path="/learning" element={<Learning />} />
        <Route path="/resume" element={<Resume />} />
        <Route path="/history" element={<History />} />
      </Routes>
    </div>
  );
}
