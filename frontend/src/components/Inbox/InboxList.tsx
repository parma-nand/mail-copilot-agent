"use client";

import { useEffect, useState } from "react";
import { getInbox } from "@/src/lib/api";
import { EmailSummary } from "@/src/types/mail";
import { useMailSocket } from "@/src/hooks/useMailSocket";

export default function InboxList({ onSelectEmail }: { onSelectEmail: (id: string) => void }) {
  const [emails, setEmails] = useState<EmailSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getInbox()
      .then(setEmails)
      .catch((err) => setError(err.response?.data?.detail || "Failed to load inbox"))
      .finally(() => setLoading(false));
  }, []);

  // ADD THIS BLOCK:
  useMailSocket((newEmails) => {
    setEmails((prev) => [...newEmails, ...prev]);
  });

  if (loading) return <div className="p-4 text-gray-500">Loading inbox...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (emails.length === 0) return <div className="p-4 text-gray-500">No emails found.</div>;

  return (
    <ul className="divide-y divide-gray-200">
      {emails.map((email) => (
        <li
          key={email.id}
          onClick={() => onSelectEmail(email.id)}
          className={`p-4 cursor-pointer hover:bg-gray-50 ${!email.is_read ? "font-semibold bg-blue-50" : ""}`}
        >
          <div className="flex justify-between text-sm">
            <span className="truncate">{email.sender}</span>
            <span className="text-gray-400 text-xs">{email.date}</span>
          </div>
          <div className="text-sm">{email.subject}</div>
          <div className="text-xs text-gray-500 truncate">{email.preview}</div>
        </li>
      ))}
    </ul>
  );
}