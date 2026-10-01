import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./layouts/AppLayout";
import AdminDashboard from "./pages/admin/AdminDashboard";
import LoginPage from "./pages/auth/LoginPage";
import CreateExamPage from "./pages/lecturer/CreateExamPage";
import ExamManagementPage from "./pages/lecturer/ExamManagementPage";
import LecturerDashboard from "./pages/lecturer/LecturerDashboard";
import ExamPage from "./pages/student/ExamPage";
import StudentDashboard from "./pages/student/StudentDashboard";
import ProtectedRoute from "./routes/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute roles={["student"]}><AppLayout /></ProtectedRoute>}>
        <Route path="/student" element={<StudentDashboard />} />
        <Route path="/student/exams/:examId" element={<ExamPage />} />
      </Route>
      <Route element={<ProtectedRoute roles={["lecturer"]}><AppLayout /></ProtectedRoute>}>
        <Route path="/lecturer" element={<LecturerDashboard />} />
        <Route path="/lecturer/exams/new" element={<CreateExamPage />} />
        <Route path="/lecturer/exams/:examId" element={<ExamManagementPage />} />
      </Route>
      <Route element={<ProtectedRoute roles={["admin"]}><AppLayout /></ProtectedRoute>}>
        <Route path="/admin" element={<AdminDashboard />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
