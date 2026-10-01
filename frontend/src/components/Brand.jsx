import { ShieldCheck } from "lucide-react";

export default function Brand({ compact = false }) {
  return (
    <div className={`brand ${compact ? "brand-compact" : ""}`}>
      <div className="brand-icon"><ShieldCheck size={24} /></div>
      <div>
        <strong>SecureExam</strong>
        {!compact && <span>Encrypted Examination Portal</span>}
      </div>
    </div>
  );
}
