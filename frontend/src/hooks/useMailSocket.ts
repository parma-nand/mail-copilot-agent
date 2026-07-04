// frontend/src/hooks/useMailSocket.ts
import { useEffect, useRef } from "react";
import { EmailSummary } from "@/src/types/mail";

export function useMailSocket(onNewEmails: (emails: EmailSummary[]) => void) {
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_API_URL!.replace("http", "ws") + "/ws/mail";
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "new_emails") {
        onNewEmails(data.emails);
      }
    };

    ws.onerror = (err) => console.error("WebSocket error:", err);

    return () => {
      ws.close();
    };
  }, [onNewEmails]);
}