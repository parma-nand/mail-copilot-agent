// frontend/src/app/page.tsx
"use client";

import { useState } from "react";
import InboxList from "@/src/components/Inbox/InboxList";
import EmailDetail from "@/src/components/EmailDetail/EmailDetails";
import ComposeForm from "@/src/components/Compose/ComposeForm";

type View = "inbox" | "compose";

export default function Home() {
  const [view, setView] = useState<View>("inbox");
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);

  return (
    <main className="flex h-screen">
      <div className="w-1/3 border-r overflow-y-auto">
        <div className="p-4 border-b flex justify-between items-center">
          <h2 className="text-lg font-bold">Inbox</h2>
          <button
            onClick={() => setView("compose")}
            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
          >
            Compose
          </button>
        </div>
        <InboxList
          onSelectEmail={(id) => {
            setSelectedEmailId(id);
            setView("inbox");
          }}
        />
      </div>

      <div className="flex-1 overflow-y-auto">
        {view === "compose" && <ComposeForm onSent={() => setView("inbox")} />}
        {view === "inbox" && selectedEmailId && <EmailDetail emailId={selectedEmailId} />}
        {view === "inbox" && !selectedEmailId && (
          <p className="p-4 text-gray-400">Select an email to view details</p>
        )}
      </div>
    </main>
  );
}