"use client";

import ReviewQueue from "@/components/ReviewQueue";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function ReviewQueuePage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-1">Review Queue</h1>
          <p className="text-muted-foreground">
            Documents flagged for manual review. Approve, reject, or edit extracted fields.
          </p>
        </div>
        <Link href="/finance">
          <Button variant="outline">Back to Dashboard</Button>
        </Link>
      </div>
      <ReviewQueue />
    </div>
  );
}
