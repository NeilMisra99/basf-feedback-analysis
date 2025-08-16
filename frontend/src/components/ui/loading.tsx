import { Skeleton } from "@/components/ui/skeleton";


export const FeedbackCardSkeleton = () => (
  <div className="transition-colors rounded-lg shadow-none border">
    <div className="px-4 py-6">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <Skeleton className="h-5 w-16 rounded-full" />
            <Skeleton className="h-5 w-20 rounded-full" />
            <div className="flex items-center gap-1">
              <Skeleton className="h-3 w-3" />
              <Skeleton className="h-3 w-24" />
            </div>
          </div>

          <div className="mb-2">
            <div className="space-y-1">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-4/5" />
              <Skeleton className="h-4 w-3/5" />
            </div>
          </div>

          <div className="flex items-center gap-2 mb-2">
            <div className="flex items-center gap-1">
              <Skeleton className="h-4 w-4" />
              <Skeleton className="h-5 w-16 rounded-full" />
            </div>
            <Skeleton className="h-3 w-20" />
          </div>

          <div className="rounded-lg p-2 bg-gray-50">
            <Skeleton className="h-4 w-20 mb-1" />
            <div className="space-y-1">
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-3/4" />
            </div>
          </div>
        </div>

        <div className="flex-shrink-0">
          <Skeleton className="h-8 w-16 rounded-md" />
        </div>
      </div>
    </div>
  </div>
);

export const StatCardSkeleton = () => (
  <div className="p-4 border rounded-lg bg-white shadow-none">
    <div className="flex items-center justify-between">
      <div>
        <Skeleton className="h-4 w-16 mb-2" />
        <Skeleton className="h-8 w-12" />
      </div>
      <Skeleton className="h-5 w-5" />
    </div>
  </div>
);

export const TotalFeedbackSkeleton = () => (
  <div className="p-4 border rounded-lg bg-white shadow-none">
    <div className="flex items-center justify-between">
      <div>
        <Skeleton className="h-4 w-20 mb-2" />
        <Skeleton className="h-8 w-12" />
      </div>
      <Skeleton className="h-5 w-5" />
    </div>
  </div>
);

export const SentimentBreakdownSkeleton = () => (
  <div className="p-6 border rounded-lg bg-white shadow-sm">
    <div className="flex items-center justify-between mb-3">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-5 w-5 rounded-full" />
    </div>
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Skeleton className="h-3 w-3 rounded-full" />
          <Skeleton className="h-3 w-16" />
        </div>
        <Skeleton className="h-3 w-8" />
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Skeleton className="h-3 w-3 rounded-full" />
          <Skeleton className="h-3 w-18" />
        </div>
        <Skeleton className="h-3 w-8" />
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Skeleton className="h-3 w-3 rounded-full" />
          <Skeleton className="h-3 w-14" />
        </div>
        <Skeleton className="h-3 w-8" />
      </div>
    </div>
  </div>
);

export const CategoryBreakdownSkeleton = () => (
  <div className="p-6 border rounded-lg bg-white shadow-sm">
    <div className="flex items-center justify-between mb-3">
      <Skeleton className="h-4 w-30" />
      <Skeleton className="h-5 w-5 rounded-full" />
    </div>
    <div className="space-y-2">
      <div className="flex justify-between">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-3 w-8" />
      </div>
      <div className="flex justify-between">
        <Skeleton className="h-3 w-20" />
        <Skeleton className="h-3 w-8" />
      </div>
      <div className="flex justify-between">
        <Skeleton className="h-3 w-18" />
        <Skeleton className="h-3 w-8" />
      </div>
    </div>
  </div>
);

export const DashboardSkeleton = () => (
  <div className="bg-white p-8 rounded-2xl shadow-sm border h-full flex flex-col">
    <div className="flex-shrink-0 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <TotalFeedbackSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
        <StatCardSkeleton />
      </div>
    </div>

    <div className="flex-shrink-0 mb-4">
      <Skeleton className="h-6 w-36" />
    </div>

    <div className="flex-1 overflow-hidden">
      <div className="max-h-[500px] overflow-y-auto pr-2">
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <FeedbackCardSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>

    <div className="flex-shrink-0 flex justify-center mt-6 pt-4">
      <div className="bg-gray-50 rounded-md p-2 shadow-sm border">
        <Skeleton className="h-9 w-24" />
      </div>
    </div>
  </div>
);

export const FeedbackFormSkeleton = () => (
  <div className="max-w-2xl mx-auto">
    <div className="border rounded-lg bg-white shadow-none">
      <div className="flex flex-col space-y-1.5 p-6">
        <Skeleton className="h-6 w-44" />
      </div>

      <div className="p-6 pt-0">
        <div className="space-y-6">
          <div className="space-y-2">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-10 w-full rounded-md" />
            <Skeleton className="h-0 w-0" />
          </div>

          <div className="space-y-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-32 w-full rounded-md" />
            <Skeleton className="h-0 w-0" />
          </div>

          <Skeleton className="h-10 w-full rounded-md" />
        </div>
      </div>
    </div>
  </div>
);

export const ComponentLoader = () => (
  <div className="space-y-4">
    <Skeleton className="h-8 w-48" />
    <Skeleton className="h-32 w-full" />
    <Skeleton className="h-10 w-24" />
  </div>
);
