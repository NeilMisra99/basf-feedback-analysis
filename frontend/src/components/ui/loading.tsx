import { Skeleton } from "@/components/ui/skeleton";
import { memo } from "react";

// Optimized skeleton components for different loading states

export const FeedbackCardSkeleton = memo(() => (
  <div className="border rounded-lg px-4 bg-white py-3">
    <div className="flex justify-between items-start mb-2">
      <Skeleton className="h-4 w-20" />
      <Skeleton className="h-4 w-16" />
    </div>
    <div className="space-y-2 mb-2">
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-3/4" />
    </div>
    <div className="flex justify-between items-center">
      <Skeleton className="h-6 w-24" />
      <Skeleton className="h-8 w-16" />
    </div>
  </div>
));

FeedbackCardSkeleton.displayName = "FeedbackCardSkeleton";

export const StatCardSkeleton = memo(() => (
  <div className="p-4 border rounded-lg">
    <div className="flex items-center justify-between">
      <div>
        <Skeleton className="h-4 w-24 mb-2" />
        <Skeleton className="h-8 w-16" />
      </div>
      <Skeleton className="h-5 w-5" />
    </div>
  </div>
));

StatCardSkeleton.displayName = "StatCardSkeleton";

export const DashboardSkeleton = memo(() => (
  <div className="h-full flex flex-col">
    {/* Statistics Overview Skeleton - Fixed at top */}
    <div className="flex-shrink-0 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => (
          <StatCardSkeleton key={i} />
        ))}
      </div>
    </div>

    {/* Recent Feedback Title Skeleton */}
    <div className="flex-shrink-0 mb-4">
      <Skeleton className="h-6 w-32" />
    </div>

    {/* Recent Feedback Skeleton - Scrollable */}
    <div className="flex-1 overflow-hidden">
      <div className="max-h-[500px] overflow-y-auto pr-2">
        <div className="space-y-2">
          {[...Array(4)].map((_, i) => (
            <FeedbackCardSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>

    {/* Refresh Button Skeleton - Fixed at bottom */}
    <div className="flex-shrink-0 flex justify-center mt-4 pt-4">
      <div className="bg-white rounded-md p-2 shadow-sm border">
        <Skeleton className="h-8 w-20" />
      </div>
    </div>
  </div>
));

DashboardSkeleton.displayName = "DashboardSkeleton";

export const FeedbackFormSkeleton = memo(() => (
  <div className="max-w-2xl mx-auto">
    <div className="p-6 border rounded-lg">
      <Skeleton className="h-6 w-48 mb-6" />
      
      <div className="space-y-6">
        {/* Category Selection Skeleton */}
        <div>
          <Skeleton className="h-4 w-16 mb-2" />
          <Skeleton className="h-10 w-full" />
        </div>

        {/* Feedback Text Skeleton */}
        <div>
          <Skeleton className="h-4 w-24 mb-2" />
          <Skeleton className="h-32 w-full" />
        </div>

        {/* Submit Button Skeleton */}
        <Skeleton className="h-10 w-full" />
      </div>
    </div>
  </div>
));

FeedbackFormSkeleton.displayName = "FeedbackFormSkeleton";

export const ComponentLoader = memo(() => (
  <div className="space-y-4">
    <Skeleton className="h-8 w-48" />
    <Skeleton className="h-32 w-full" />
    <Skeleton className="h-10 w-24" />
  </div>
));

ComponentLoader.displayName = "ComponentLoader";