// frontend/src/app/page.tsx
"use client";

import { useState } from "react";
import InboxList from "@/src/components/Inbox/InboxList";
import EmailDetail from "@/src/components/EmailDetail/EmailDetails";

export default function Home() {
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);

  return (
    <main className="flex h-screen">
      <div className="w-1/3 border-r overflow-y-auto">
        <h2 className="p-4 text-lg font-bold border-b">Inbox</h2>
        <InboxList onSelectEmail={setSelectedEmailId} />
      </div>
      <div className="flex-1 overflow-y-auto">
        {selectedEmailId ? (
          <EmailDetail emailId={selectedEmailId} />
        ) : (
          <p className="p-4 text-gray-400">Select an email to view details</p>
        )}
      </div>
    </main>
  );
}