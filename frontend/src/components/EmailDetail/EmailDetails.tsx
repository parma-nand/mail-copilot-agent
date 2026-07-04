// frontend/src/components/EmailDetail/EmailDetail.tsx
"use client";

import { useEffect, useState } from "react";
import { getEmail } from "@/src/lib/api";

interface EmailDetailProps {
  emailId: string;
}

interface GmailHeader {
  name: string;
  value: string;
}

interface GmailMessage {
  id: string;
  snippet: string;
  payload: {
    headers: GmailHeader[];
    body?: { data?: string };
    parts?: { mimeType: string; body: { data?: string } }[];
  };
}

function getHeader(headers: GmailHeader[], name: string) {
  return headers.find((h) => h.name.toLowerCase() === name.toLowerCase())?.value || "";
}

function decodeBody(payload: GmailMessage["payload"]): string {
  // Try direct body first
  if (payload.body?.data) {
    return atob(payload.body.data.replace(/-/g, "+").replace(/_/g, "/"));
  }
  // Fallback: look for text/plain part
  const textPart = payload.parts?.find((p) => p.mimeType === "text/plain");
  if (textPart?.body?.data) {
    return atob(textPart.body.data.replace(/-/g, "+").replace(/_/g, "/"));
  }
  return "(No readable content)";
}

export default function EmailDetail({ emailId }: EmailDetailProps) {
  const [email, setEmail] = useState<GmailMessage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getEmail(emailId)
      .then(setEmail)
      .catch((err) => setError(err.response?.data?.detail || "Failed to load email"))
      .finally(() => setLoading(false));
  }, [emailId]);

  if (loading) return <div className="p-4 text-gray-500">Loading email...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (!email) return null;

  const headers = email.payload.headers;
  const from = getHeader(headers, "From");
  const subject = getHeader(headers, "Subject");
  const date = getHeader(headers, "Date");
  const body = decodeBody(email.payload);

  return (
    <div className="p-6 max-w-3xl">
      <h2 className="text-xl font-bold mb-1">{subject}</h2>
      <div className="text-sm text-gray-500 mb-4">
        <div>From: {from}</div>
        <div>{date}</div>
      </div>
      <div className="whitespace-pre-wrap text-sm border-t pt-4">{body}</div>
    </div>
  );
}