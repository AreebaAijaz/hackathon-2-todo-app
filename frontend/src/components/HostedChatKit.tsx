"use client";

import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { useSession } from "@/lib/auth-client";

interface HostedChatKitProps {
  className?: string;
}

/**
 * OpenAI Hosted ChatKit Component
 *
 * This component uses OpenAI's hosted ChatKit infrastructure.
 * It requires:
 * 1. Domain allowlist configured at OpenAI Platform
 * 2. NEXT_PUBLIC_OPENAI_DOMAIN_KEY environment variable
 * 3. Backend /api/chatkit/session endpoint for session creation
 */
export default function HostedChatKit({ className = "" }: HostedChatKitProps) {
  const { data: session } = useSession();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const domainKey = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY;

  const { control } = useChatKit({
    api: {
      // Get client secret from our backend
      async getClientSecret(existing) {
        // If we have an existing token and it's not expired, refresh it
        if (existing) {
          const res = await fetch(`${apiUrl}/api/chatkit/refresh`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({ token: existing }),
          });

          if (res.ok) {
            const data = await res.json();
            return data.client_secret;
          }
        }

        // Create new session
        const res = await fetch(`${apiUrl}/api/chatkit/session`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
        });

        if (!res.ok) {
          throw new Error(`Failed to create session: ${res.statusText}`);
        }

        const data = await res.json();
        return data.client_secret;
      },

      // Domain key from OpenAI Platform (optional for some setups)
      ...(domainKey && { domainKey }),
    },
    locale: "en",
    onError: ({ error }) => {
      console.error("ChatKit error:", error);
    },
    onThreadChange: ({ threadId }) => {
      // Optionally persist thread ID for conversation continuity
      if (threadId) {
        localStorage.setItem("chatkit_thread_id", threadId);
      }
    },
  });

  if (!session) {
    return (
      <div className="h-full flex items-center justify-center">
        <p className="text-[var(--muted-foreground)]">Please sign in to chat</p>
      </div>
    );
  }

  return (
    <div className={`h-full w-full ${className}`}>
      <ChatKit
        control={control}
        className="h-full w-full"
      />
    </div>
  );
}
