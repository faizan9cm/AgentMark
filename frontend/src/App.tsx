import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import ChatPage from "./pages/ChatPage";
import DashboardPage from "./pages/DashboardPage";
import RunsPage from "./pages/RunsPage";
import TracePage from "./pages/TracePage";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/runs" element={<RunsPage />} />
          <Route path="/trace/:runId" element={<TracePage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}