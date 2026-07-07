// frontend/src/components/Compose/ComposeForm.tsx
"use client";

import { useState } from "react";
import { sendEmail } from "@/src/lib/api";

interface ComposeFormProps {
  initialTo?: string;
  initialSubject?: string;
  initialBody?: string;
  onSent?: () => void;
}

export default function ComposeForm({
  initialTo = "",
  initialSubject = "",
  initialBody = "",
  onSent,
}: ComposeFormProps) {
  const [to, setTo] = useState(initialTo);
  const [subject, setSubject] = useState(initialSubject);
  const [body, setBody] = useState(initialBody);
  const [sending, setSending] = useState(false);
  const [status, setStatus] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const handleSend = async () => {
    if (!to || !subject || !body) {
      setStatus({ type: "error", message: "Please fill in To, Subject, and Body." });
      return;
    }
    setSending(true);
    setStatus(null);
    try {
      await sendEmail({ to, subject, body });
      setStatus({ type: "success", message: "Email sent successfully!" });
      setTo("");
      setSubject("");
      setBody("");
      onSent?.();
    } catch (err: any) {
      setStatus({
        type: "error",
        message: err.response?.data?.detail || "Failed to send email.",
      });
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl">
      <h2 className="text-lg font-bold mb-4">Compose</h2>

      <div className="space-y-3">
        <div>
          <label className="block text-xs text-gray-500 mb-1">To</label>
          <input
            type="email"
            value={to}
            onChange={(e) => setTo(e.target.value)}
            className="w-full border rounded px-3 py-2 text-sm"
            placeholder="recipient@example.com"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Subject</label>
          <input
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="w-full border rounded px-3 py-2 text-sm"
            placeholder="Subject"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Body</label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={10}
            className="w-full border rounded px-3 py-2 text-sm"
            placeholder="Write your message..."
          />
        </div>

        {status && (
          <div
            className={`text-sm p-2 rounded ${
              status.type === "success" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
            }`}
          >
            {status.message}
          </div>
        )}

        <button
          onClick={handleSend}
          disabled={sending}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          {sending ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}