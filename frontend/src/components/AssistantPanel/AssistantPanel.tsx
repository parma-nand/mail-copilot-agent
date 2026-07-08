// frontend/src/components/AssistantPanel/AssistantPanel.tsx
"use client";

import { CopilotSidebar } from "@copilotkit/react-ui";

export default function AssistantPanel() {
  return (
    <CopilotSidebar
      labels={{
        title: "Mail Assistant",
        initial:
          "Hi! I can compose emails, search your inbox, open specific messages, and pre-fill replies. Try: 'send an email to john@example.com about the meeting tomorrow'",
      }}
      defaultOpen={true}
    />
  );
}