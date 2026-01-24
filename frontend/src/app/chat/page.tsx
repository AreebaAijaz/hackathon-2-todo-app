"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useSession, signOut } from "@/lib/auth-client";
import ChatKitWindow from "@/components/ChatKitWindow";

export default function ChatPage() {
  const router = useRouter();
  const { data: session, isPending } = useSession();
  const [showDropdown, setShowDropdown] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    if (!isPending && !session) {
      router.push("/login");
    }
  }, [session, isPending, router]);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await signOut();
      router.push("/login");
      router.refresh();
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  if (isPending) {
    return (
      <div className="min-h-screen bg-[var(--background)] flex flex-col items-center justify-center">
        <div className="w-12 h-12 rounded-full border-4 border-[var(--muted)] border-t-[var(--gradient-start)] animate-spin" />
        <p className="mt-4 text-[var(--muted-foreground)]">Loading...</p>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  const user = session.user;
  const userInitial =
    user?.name?.charAt(0).toUpperCase() ||
    user?.email?.charAt(0).toUpperCase() ||
    "U";

  return (
    <div className="h-screen flex flex-col bg-[var(--background)]">
      {/* Top navigation bar */}
      <nav className="flex items-center justify-between px-4 sm:px-6 py-3 border-b border-[var(--border)] bg-[var(--card)]">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-9 h-9 rounded-xl gradient-bg flex items-center justify-center">
            <svg
              className="w-5 h-5 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
              />
            </svg>
          </div>
          <span className="text-xl font-bold group-hover:text-[var(--gradient-start)] transition-colors">
            TaskFlow
          </span>
        </Link>

        {/* Navigation tabs */}
        <div className="flex items-center gap-1 bg-[var(--muted)] rounded-lg p-1">
          <Link
            href="/tasks"
            className="px-4 py-2 text-sm font-medium rounded-md text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-[var(--background)] transition-colors"
          >
            Tasks
          </Link>
          <div className="px-4 py-2 text-sm font-medium rounded-md bg-[var(--background)] text-[var(--foreground)] shadow-sm">
            AI Chat
          </div>
        </div>

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="w-10 h-10 rounded-full bg-[var(--gradient-start)] hover:bg-[var(--gradient-mid)] flex items-center justify-center transition-colors"
          >
            <span className="text-white font-bold">{userInitial}</span>
          </button>

          {showDropdown && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowDropdown(false)}
              />
              <div className="absolute right-0 mt-2 w-64 bg-[var(--card)] border border-[var(--border)] rounded-xl shadow-xl z-20 overflow-hidden">
                <div className="px-4 py-3 bg-[var(--muted)]">
                  <p className="text-sm font-semibold truncate">{user?.name}</p>
                  <p className="text-xs text-[var(--muted-foreground)] truncate">
                    {user?.email}
                  </p>
                </div>
                <div className="border-t border-[var(--border)] py-1">
                  <button
                    onClick={handleLogout}
                    disabled={isLoggingOut}
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-[var(--error)] hover:bg-[var(--error-light)] transition-colors"
                  >
                    {isLoggingOut ? (
                      <div className="w-5 h-5 border-2 border-[var(--error)]/30 border-t-[var(--error)] rounded-full animate-spin" />
                    ) : (
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                        />
                      </svg>
                    )}
                    {isLoggingOut ? "Signing out..." : "Sign out"}
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </nav>

      {/* Chat window - takes remaining height */}
      <div className="flex-1 overflow-hidden">
        <ChatKitWindow />
      </div>
    </div>
  );
}
