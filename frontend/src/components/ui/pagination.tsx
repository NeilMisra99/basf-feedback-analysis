import { Button } from "./button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  disabled?: boolean;
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  disabled = false,
}: PaginationProps) {
  if (totalPages <= 1) return null;

  const getVisiblePages = () => {
    const delta = 2;
    const range = [];
    const start = Math.max(1, currentPage - delta);
    const end = Math.min(totalPages, currentPage + delta);

    for (let i = start; i <= end; i++) {
      range.push(i);
    }

    return range;
  };

  const visiblePages = getVisiblePages();

  return (
    <div className="flex items-center justify-center gap-2">
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={disabled || currentPage <= 1}
        className="flex items-center gap-1 !bg-white"
      >
        <ChevronLeft className="h-4 w-4" />
        Previous
      </Button>

      {visiblePages[0] > 1 && (
        <>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(1)}
            disabled={disabled}
            className={`min-w-[2.5rem] ${
              currentPage === 1
                ? "!bg-black !text-white border-black"
                : "!bg-white !text-black border-gray-300"
            }`}
          >
            1
          </Button>
          {visiblePages[0] > 2 && (
            <span className="text-muted-foreground px-2">...</span>
          )}
        </>
      )}

      {visiblePages.map((page) => (
        <Button
          key={page}
          variant="outline"
          size="sm"
          onClick={() => onPageChange(page)}
          disabled={disabled}
          className={`min-w-[2.5rem] ${
            currentPage === page
              ? "!bg-black !text-white border-black"
              : "!bg-white !text-black border-gray-300"
          }`}
        >
          {page}
        </Button>
      ))}

      {visiblePages[visiblePages.length - 1] < totalPages && (
        <>
          {visiblePages[visiblePages.length - 1] < totalPages - 1 && (
            <span className="text-muted-foreground px-2">...</span>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(totalPages)}
            disabled={disabled}
            className={`min-w-[2.5rem] ${
              currentPage === totalPages
                ? "!bg-black !text-white border-black"
                : "!bg-white !text-black border-gray-300"
            }`}
          >
            {totalPages}
          </Button>
        </>
      )}

      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={disabled || currentPage >= totalPages}
        className="flex items-center gap-1 !bg-white"
      >
        Next
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  );
}
